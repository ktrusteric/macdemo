from typing import List, Optional
from pymongo.database import Database
from app.models.user import UserTags, UserTag, TagCategory, UserCreate, User, UserRole, TagSource
from app.core.security import get_password_hash, verify_password
from app.utils.region_mapper import RegionMapper
from app.utils.energy_weight_system import EnergyWeightSystem, get_energy_weight  # 🔥 新增能源权重系统
from datetime import datetime
import uuid

class UserService:
    def __init__(self, database: Database):
        self.db = database
        self.user_tags_collection = self.db.user_tags
        self.users_collection = self.db.users

    async def create_user(
        self, 
        user_data: UserCreate, 
        energy_types: List[str] = None
    ) -> User:
        """创建新用户（基于城市生成区域标签）"""
        try:
            # 检查邮箱是否已存在
            existing_user = await self.users_collection.find_one({"email": user_data.email})
            if existing_user:
                raise ValueError("Email already registered")
            
            # 检查用户名是否已存在
            existing_username = await self.users_collection.find_one({"username": user_data.username})
            if existing_username:
                raise ValueError("Username already taken")
            
            # 验证注册城市是否支持（改用省份映射验证）
            province_code = RegionMapper.get_province_by_city(user_data.register_city)
            if not province_code:
                raise ValueError(f"不支持的注册城市: {user_data.register_city}")
            
            # 通过省份获取区域信息（确保完整的地域信息）
            region_code = RegionMapper.get_region_by_province(province_code)
            if not region_code:
                raise ValueError(f"无法获取城市 {user_data.register_city} 的区域信息")
            
            # 🔥 获取注册时的完整地域信息
            location_info = RegionMapper.get_full_location_info(user_data.register_city)
            
            # 🔥 构建注册信息（用于重置标签功能）
            register_info = {
                "register_city": user_data.register_city,
                "energy_types": energy_types or [],
                "location_info": location_info,
                "register_time": datetime.utcnow().isoformat(),
                "province_code": province_code,
                "region_code": region_code
            }
            
            # 创建用户基础信息
            user_id = str(uuid.uuid4())
            hashed_password = get_password_hash(user_data.password)
            
            user_doc = {
                "id": user_id,
                "email": user_data.email,
                "username": user_data.username,
                "hashed_password": hashed_password,
                "role": UserRole.FREE,
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "has_initial_tags": False,
                "register_city": user_data.register_city,
                "register_info": register_info  # 🔥 存储完整的注册信息
            }
            
            # 插入用户基础信息
            await self.users_collection.insert_one(user_doc)
            
            # 根据注册城市自动初始化标签
            await self.initialize_user_tags_by_city(user_id, user_data.register_city, energy_types)
            
            # 更新用户标签初始化状态
            user_doc["has_initial_tags"] = True
            await self.users_collection.update_one(
                {"id": user_id},
                {"$set": {"has_initial_tags": True}}
            )
            
            # 返回用户对象（不包含密码）
            user_doc.pop("hashed_password", None)
            return User(**user_doc)
            
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")

    async def initialize_user_tags_by_city(
        self, 
        user_id: str, 
        register_city: str,
        energy_types: List[str] = None
    ) -> UserTags:
        """基于注册城市初始化用户标签（四层标签权重体系 + 能源分层权重）"""
        try:
            # 验证城市有效性（改用省份映射验证）
            province_code = RegionMapper.get_province_by_city(register_city)
            if not province_code:
                raise ValueError(f"Unsupported city: {register_city}")
            
            # 获取完整位置信息
            location_info = RegionMapper.get_full_location_info(register_city)
            
            tags = []
            
            # 🔥 四级地区标签权重体系：城市(5.0) > 省份(1.5) > 地区(1.0) > 全国(0.5)
            
            # 1. 城市标签（权重5.0，用户明确选择，最高优先级）
            tags.append(UserTag(
                category=TagCategory.CITY,
                name=location_info["city"],
                weight=5.0,  # 🔥 注册城市权重提升到5.0
                source=TagSource.PRESET,
                created_at=datetime.utcnow()
            ))
            
            # 2. 省份标签（权重1.5，自动生成）
            if "province" in location_info:
                tags.append(UserTag(
                    category=TagCategory.PROVINCE,
                    name=location_info["province"],
                    weight=1.5,  # 🔥 省份权重调整为1.5
                    source=TagSource.REGION_AUTO,
                    created_at=datetime.utcnow()
                ))
            
            # 3. 地区标签（权重1.0，自动生成）
            if "region" in location_info:
                tags.append(UserTag(
                    category=TagCategory.REGION,
                    name=location_info["region"],
                    weight=1.0,  # 🔥 地区权重调整为1.0
                    source=TagSource.REGION_AUTO,
                    created_at=datetime.utcnow()
                ))
            
            # 4. 全国标签（权重0.5，自动生成，确保覆盖）
            # 🔥 注意：统一使用"全国"标签，不使用"中国"标签，避免重复
            tags.append(UserTag(
                category=TagCategory.REGION,
                name="全国",
                weight=0.5,  # 🔥 全国权重最低0.5
                source=TagSource.REGION_AUTO,
                created_at=datetime.utcnow()
            ))
            
            # 🔥 5. 能源类型标签（使用分层权重系统）
            if energy_types:
                energy_tags_info = self._create_energy_tags_with_weights(energy_types)
                tags.extend(energy_tags_info["tags"])
                
                # 输出能源标签信息
                print(f"⚡ 能源标签分层权重配置:")
                for category, products in energy_tags_info["hierarchy"].items():
                    if products:
                        print(f"   📁 {category} (大类权重: 3.0)")
                        for product in products:
                            print(f"      └── {product} (具体产品权重: 5.0)")
            
            # 创建或更新用户标签
            user_tags = UserTags(
                user_id=user_id,
                tags=tags,
                updated_at=datetime.utcnow()
            )
            
            # 保存到数据库
            await self.user_tags_collection.replace_one(
                {"user_id": user_id},
                user_tags.dict(),
                upsert=True
            )
            
            print(f"✅ 用户 {user_id} 标签初始化完成:")
            print(f"   🏙️ 城市标签: {location_info['city']} (权重: 5.0)")
            if "province" in location_info:
                print(f"   🏛️ 省份标签: {location_info['province']} (权重: 1.5)")
            if "region" in location_info:
                print(f"   🗺️ 地区标签: {location_info['region']} (权重: 1.0)")
            print(f"   🌍 全国标签: 全国 (权重: 0.5)")
            
            return user_tags
            
        except Exception as e:
            raise Exception(f"Failed to initialize user tags: {str(e)}")

    def _create_energy_tags_with_weights(self, energy_types: List[str]) -> dict:
        """
        🔥 创建能源标签，应用分层权重系统
        
        Args:
            energy_types: 用户选择的能源类型列表
            
        Returns:
            dict: 包含标签列表和层级信息
        """
        energy_tags = []
        hierarchy_info = {}
        categories_added = set()
        
        for energy_type in energy_types:
            # 获取能源权重和大类信息
            weight_enum = get_energy_weight(energy_type)
            weight = float(weight_enum)  # 🔥 将Enum转换为数值
            category = EnergyWeightSystem.get_energy_category(energy_type)
            
            # 添加能源标签
            energy_tags.append(UserTag(
                category=TagCategory.ENERGY_TYPE,
                name=energy_type,
                weight=weight,  # 🔥 使用分层权重：大类3.0，具体产品5.0
                source=TagSource.PRESET,
                created_at=datetime.utcnow()
            ))
            
            # 记录层级信息
            if category:
                if category not in hierarchy_info:
                    hierarchy_info[category] = []
                hierarchy_info[category].append(energy_type)
                
                # 如果选择的是具体产品，自动添加对应的大类标签（避免重复）
                if category != energy_type and category not in categories_added:
                    category_weight_enum = get_energy_weight(category)
                    category_weight = float(category_weight_enum)  # 🔥 将Enum转换为数值
                    
                    energy_tags.append(UserTag(
                        category=TagCategory.ENERGY_TYPE,
                        name=category,
                        weight=category_weight,  # 🔥 大类权重3.0
                        source=TagSource.REGION_AUTO,  # 自动生成的大类标签
                        created_at=datetime.utcnow()
                    ))
                    categories_added.add(category)
                    
                    if category not in hierarchy_info:
                        hierarchy_info[category] = []
        
        return {
            "tags": energy_tags,
            "hierarchy": hierarchy_info,
            "categories_count": len(categories_added),
            "products_count": len(energy_types)
        }

    async def get_user_region_info(self, user_id: str) -> dict:
        """获取用户的完整区域信息（城市、省份、区域）"""
        try:
            # 获取用户信息
            user = await self.get_user_by_id(user_id)
            if not user or not user.register_city:
                return {
                    "user_id": user_id,
                    "city": None,
                    "province": None,
                    "region": None,
                    "location_info": None
                }
            
            # 获取完整位置信息
            location_info = RegionMapper.get_full_location_info(user.register_city)
            
            return {
                "user_id": user_id,
                "city": location_info.get("city"),
                "city_code": location_info.get("city_code"),
                "province": location_info.get("province"),
                "province_code": location_info.get("province_code"),
                "region": location_info.get("region"),
                "region_code": location_info.get("region_code"),
                "location_info": location_info
            }
        except Exception as e:
            raise Exception(f"Failed to get user region info: {str(e)}")

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """验证用户登录"""
        try:
            # 查找用户
            user_doc = await self.users_collection.find_one({"email": email})
            if not user_doc:
                return None
            
            # 验证密码
            if not verify_password(password, user_doc.get("hashed_password", "")):
                return None
            
            # 返回用户对象（不包含密码）
            user_doc.pop("hashed_password", None)
            user_doc.pop("_id", None)
            return User(**user_doc)
            
        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户信息"""
        try:
            user_doc = await self.users_collection.find_one({"id": user_id})
            if not user_doc:
                return None
            
            user_doc.pop("hashed_password", None)
            user_doc.pop("_id", None)
            return User(**user_doc)
            
        except Exception as e:
            raise Exception(f"Failed to get user: {str(e)}")

    async def get_access_features(self, role: UserRole) -> List[str]:
        """根据用户角色获取可访问功能"""
        feature_mapping = {
            UserRole.FREE: [
                "dashboard",
                "basic_content", 
                "ai_assistants"
            ],
            UserRole.PAID: [
                "dashboard",
                "basic_content",
                "research_reports", 
                "ai_assistants",
                "advanced_recommendations"
            ],
            UserRole.ADMIN: [
                "dashboard",
                "basic_content",
                "research_reports", 
                "ai_assistants",
                "advanced_recommendations",
                "user_management",
                "content_management"
            ]
        }
        return feature_mapping.get(role, [])

    async def get_user_tags(self, user_id: str) -> Optional[UserTags]:
        """获取用户标签（统一处理演示用户和正常用户）"""
        try:
            # 优先检查是否为演示用户
            if user_id.startswith('user') and len(user_id) <= 10:
                demo_tags = await self.get_demo_user_tags(user_id)
                if demo_tags:
                    return demo_tags
            
            # 查找正常用户标签
            document = await self.user_tags_collection.find_one({"user_id": user_id})
            if not document:
                return None
            
            return UserTags(**document)
        except Exception as e:
            raise Exception(f"Failed to get user tags: {str(e)}")

    async def ensure_user_has_tags(self, user_id: str) -> UserTags:
        """确保用户有标签，如果没有则初始化"""
        try:
            # 检查是否已有标签
            existing_tags = await self.get_user_tags(user_id)
            if existing_tags and existing_tags.tags:
                return existing_tags
            
            # 如果是演示用户，不需要初始化
            if user_id.startswith('user') and len(user_id) <= 10:
                raise Exception(f"Demo user {user_id} should have predefined tags")
            
            # 尝试获取用户信息
            user = await self.get_user_by_id(user_id)
            
            # 如果用户存在且有注册城市，基于城市初始化标签
            if user and hasattr(user, 'register_city') and user.register_city:
                return await self.initialize_user_tags_by_city(
                    user_id, 
                    user.register_city, 
                    energy_types=["天然气", "电力"]  # 默认能源类型
                )
            
            # 如果用户不存在或没有注册城市，创建基础标签
            print(f"为用户 {user_id} 创建基础标签（用户{'不存在' if not user else '无注册城市'}）")
            basic_tags = [
                # 移除"全国"标签，避免用户获取过多无关内容
                # UserTag(
                #     category=TagCategory.REGION,
                #     name="全国",
                #     weight=1.0,
                #     source=TagSource.PRESET,
                #     created_at=datetime.utcnow()
                # ),
                UserTag(
                    category=TagCategory.ENERGY_TYPE,
                    name="天然气",
                    weight=1.0,
                    source=TagSource.PRESET,
                    created_at=datetime.utcnow()
                ),
                UserTag(
                    category=TagCategory.ENERGY_TYPE,
                    name="电力",
                    weight=1.0,
                    source=TagSource.PRESET,
                    created_at=datetime.utcnow()
                )
            ]
            
            user_tags = UserTags(
                user_id=user_id,
                tags=basic_tags,
                updated_at=datetime.utcnow()
            )
            
            await self.user_tags_collection.replace_one(
                {"user_id": user_id},
                user_tags.dict(),
                upsert=True
            )
            
            print(f"✅ 成功为用户 {user_id} 创建了 {len(basic_tags)} 个基础标签")
            return user_tags
            
        except Exception as e:
            print(f"❌ 确保用户标签失败: {str(e)}")
            raise Exception(f"Failed to ensure user has tags: {str(e)}")

    async def reset_user_tags_to_registration(self, user_id: str) -> UserTags:
        """
        🔥 根据用户注册信息重置标签
        
        这个方法会清除所有用户手动添加的标签，
        恢复到注册时的原始标签配置
        
        Args:
            user_id: 用户ID
            
        Returns:
            UserTags: 重置后的用户标签
        """
        try:
            # 获取用户信息（包含注册信息）
            user = await self.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"用户不存在: {user_id}")
            
            # 检查是否有注册信息
            if not hasattr(user, 'register_info') or not user.register_info:
                # 如果没有注册信息，使用 register_city 作为备选方案
                if hasattr(user, 'register_city') and user.register_city:
                    print(f"⚠️ 用户 {user_id} 缺少详细注册信息，使用 register_city: {user.register_city}")
                    # 使用基础的城市信息重新初始化
                    return await self.initialize_user_tags_by_city(user_id, user.register_city, [])
                else:
                    raise ValueError(f"用户 {user_id} 缺少注册信息，无法重置标签")
            
            register_info = user.register_info
            original_city = register_info.get("register_city")
            original_energy_types = register_info.get("energy_types", [])
            
            print(f"🔄 开始重置用户 {user_id} 的标签...")
            print(f"   📍 原始注册城市: {original_city}")
            print(f"   ⚡ 原始能源类型: {original_energy_types}")
            
            # 删除现有标签
            await self.user_tags_collection.delete_one({"user_id": user_id})
            print(f"   🗑️ 已清除所有现有标签")
            
            # 根据注册信息重新初始化标签
            new_tags = await self.initialize_user_tags_by_city(
                user_id, 
                original_city, 
                original_energy_types
            )
            
            print(f"✅ 用户 {user_id} 标签重置完成")
            print(f"   🏷️ 新标签数量: {len(new_tags.tags)}")
            
            # 统计标签类型
            tag_stats = {}
            for tag in new_tags.tags:
                category = tag.category
                if category not in tag_stats:
                    tag_stats[category] = 0
                tag_stats[category] += 1
            
            print(f"   📊 标签分布: {tag_stats}")
            
            return new_tags
            
        except Exception as e:
            print(f"❌ 重置用户标签失败: {str(e)}")
            raise Exception(f"Failed to reset user tags: {str(e)}")

    async def update_user_tags(self, user_id: str, tags: List[UserTag]) -> UserTags:
        """更新用户标签"""
        try:
            # 验证标签
            self._validate_tags(tags)
            
            # 创建或更新用户标签
            user_tags = UserTags(
                user_id=user_id,
                tags=tags,
                updated_at=datetime.utcnow()
            )
            
            # 保存到数据库
            await self.user_tags_collection.replace_one(
                {"user_id": user_id},
                user_tags.dict(),
                upsert=True
            )
            
            return user_tags
            
        except Exception as e:
            raise Exception(f"Failed to update user tags: {str(e)}")

    async def add_user_tag(
        self, 
        user_id: str, 
        tag_name: str, 
        category: TagCategory, 
        weight: float = 1.0,
        source: TagSource = TagSource.MANUAL
    ) -> bool:
        """
        为用户添加新标签（用于收藏学习等场景）
        """
        try:
            # 获取当前用户标签
            current_user_tags = await self.get_user_tags(user_id)
            if not current_user_tags:
                # 如果用户没有标签，先初始化
                current_user_tags = await self.ensure_user_has_tags(user_id)
            
            # 检查标签是否已存在
            existing_tag_names = {tag.name for tag in current_user_tags.tags}
            if tag_name in existing_tag_names:
                return False  # 标签已存在，不重复添加
            
            # 创建新标签
            new_tag = UserTag(
                category=category,
                name=tag_name,
                weight=weight,
                source=source,
                created_at=datetime.utcnow()
            )
            
            # 添加到现有标签列表
            updated_tags = current_user_tags.tags + [new_tag]
            
            # 更新用户标签
            await self.update_user_tags(user_id, updated_tags)
            
            return True
            
        except Exception as e:
            print(f"添加用户标签失败: {str(e)}")
            return False

    def _validate_tags(self, tags: List[UserTag]) -> None:
        """验证标签数据"""
        if len(tags) > 50:  # 限制标签数量
            raise ValueError("Too many tags. Maximum 50 tags allowed.")
        
        # 检查每个分类的标签数量
        category_counts = {}
        for tag in tags:
            category_counts[tag.category] = category_counts.get(tag.category, 0) + 1
            if category_counts[tag.category] > 10:
                raise ValueError(f"Too many tags in category {tag.category}. Maximum 10 tags per category.")

    async def get_user_tags_by_category(
        self, 
        user_id: str, 
        category: TagCategory
    ) -> List[UserTag]:
        """按分类获取用户标签"""
        user_tags = await self.get_user_tags(user_id)
        if not user_tags:
            return []
        
        return [tag for tag in user_tags.tags if tag.category == category]

    async def get_demo_users(self) -> List[dict]:
        """获取所有演示用户列表"""
        try:
            # 查找所有包含demo_user_id字段的用户
            cursor = self.users_collection.find(
                {"demo_user_id": {"$exists": True}},
                {
                    "id": 1,
                    "demo_user_id": 1,
                    "username": 1,
                    "email": 1,
                    "description": 1,
                    "register_city": 1,
                    "_id": 0
                }
            ).sort("demo_user_id", 1)
            
            demo_users = await cursor.to_list(length=None)
            return demo_users
            
        except Exception as e:
            raise Exception(f"Failed to get demo users: {str(e)}")

    async def get_demo_user_tags(self, demo_user_id: str) -> Optional[UserTags]:
        """根据演示用户ID获取用户标签"""
        try:
            # 首先通过demo_user_id找到真实的用户ID
            user_doc = await self.users_collection.find_one({"demo_user_id": demo_user_id})
            if not user_doc:
                return None
            
            real_user_id = user_doc["id"]
            
            # 获取用户标签
            document = await self.user_tags_collection.find_one({"user_id": real_user_id})
            if not document:
                return None
            
            return UserTags(**document)
            
        except Exception as e:
            raise Exception(f"Failed to get demo user tags: {str(e)}")

    async def get_demo_user_by_id(self, demo_user_id: str) -> Optional[User]:
        """根据演示用户ID获取用户信息"""
        try:
            user_doc = await self.users_collection.find_one({"demo_user_id": demo_user_id})
            if not user_doc:
                return None
            
            user_doc.pop("hashed_password", None)
            user_doc.pop("_id", None)
            return User(**user_doc)
            
        except Exception as e:
            raise Exception(f"Failed to get demo user by ID: {str(e)}")
    
    async def get_users(self, page: int = 1, page_size: int = 20) -> dict:
        """获取用户列表（用于管理员后台）"""
        try:
            # 计算跳过数量
            skip = (page - 1) * page_size
            
            # 获取总数
            total = await self.users_collection.count_documents({})
            
            # 获取用户列表
            cursor = self.users_collection.find(
                {},
                {"hashed_password": 0, "_id": 0}  # 排除密码字段和_id字段
            ).skip(skip).limit(page_size).sort("created_at", -1)  # 按创建时间倒序
            
            users_list = []
            async for user_doc in cursor:
                # 获取用户标签数量
                tags_count = 0
                user_tags = await self.user_tags_collection.find_one({"user_id": user_doc["id"]})
                if user_tags and "tags" in user_tags:
                    tags_count = len(user_tags["tags"])
                
                user_info = {
                    "id": user_doc["id"],
                    "username": user_doc.get("username", ""),
                    "email": user_doc.get("email", ""),
                    "register_city": user_doc.get("register_city"),
                    "role": user_doc.get("role", "free"),
                    "is_active": user_doc.get("is_active", True),
                    "created_at": user_doc.get("created_at", ""),
                    "tags_count": tags_count
                }
                users_list.append(user_info)
            
            return {
                "data": users_list,
                "total": total,
                "page": page,
                "page_size": page_size
            }
            
        except Exception as e:
            raise Exception(f"Failed to get users: {str(e)}")

    def _generate_region_tags(self, city: str) -> List[UserTag]:
        """
        基于用户注册城市生成完整的地区标签层次
        权重体系：城市(5.0) > 省份(1.5) > 地区(1.0) > 全国(0.5)
        """
        region_tags = []
        
        # 🔥 四级地区标签权重配置
        REGION_WEIGHT_CONFIG = {
            "city": 5.0,        # 注册城市权重最高
            "province": 1.5,    # 省份权重
            "region": 1.0,      # 地区权重  
            "national": 0.5     # 全国权重最低
        }
        
        # 1. 城市标签（用户注册选择，权重最高）
        region_tags.append(UserTag(
            category="city",
            name=city,
            weight=REGION_WEIGHT_CONFIG["city"],
            source="preset",
            created_at=datetime.utcnow()
        ))
        
        # 2. 省份标签（自动生成）
        province = self._get_province_from_city(city)
        if province and province != city:
            region_tags.append(UserTag(
                category="province", 
                name=province,
                weight=REGION_WEIGHT_CONFIG["province"],
                source="region_auto",
                created_at=datetime.utcnow()
            ))
        
        # 3. 地区标签（自动生成）
        region = self._get_region_from_city(city)
        if region:
            region_tags.append(UserTag(
                category="region",
                name=region,
                weight=REGION_WEIGHT_CONFIG["region"], 
                source="region_auto",
                created_at=datetime.utcnow()
            ))
        
        # 4. 全国标签（权重0.5，自动生成，确保覆盖）
        # 🔥 注意：统一使用"全国"标签，不使用"中国"标签，避免重复
        region_tags.append(UserTag(
            category=TagCategory.REGION,
            name="全国",
            weight=0.5,  # 🔥 全国权重最低0.5
            source=TagSource.REGION_AUTO,
            created_at=datetime.utcnow()
        ))
        
        return region_tags 