from typing import List, Optional
from pymongo.database import Database
from app.models.user import UserTags, UserTag, TagCategory, UserCreate, User, UserRole, TagSource
from app.core.security import get_password_hash, verify_password
from app.utils.region_mapper import RegionMapper
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
                "register_city": user_data.register_city
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
        """基于注册城市初始化用户标签（三层标签：城市、省份、区域）"""
        try:
            # 验证城市有效性（改用省份映射验证）
            province_code = RegionMapper.get_province_by_city(register_city)
            if not province_code:
                raise ValueError(f"Unsupported city: {register_city}")
            
            # 获取完整位置信息
            location_info = RegionMapper.get_full_location_info(register_city)
            
            tags = []
            
            # 1. 城市标签（权重2.5，用户明确选择）
            tags.append(UserTag(
                category=TagCategory.CITY,
                name=location_info["city"],
                weight=2.5,
                source=TagSource.PRESET,
                created_at=datetime.utcnow()
            ))
            
            # 2. 省份标签（权重2.0，自动生成）
            if "province" in location_info:
                tags.append(UserTag(
                    category=TagCategory.PROVINCE,
                    name=location_info["province"],
                    weight=2.0,
                    source=TagSource.REGION_AUTO,
                    created_at=datetime.utcnow()
                ))
            
            # 3. 区域标签（权重1.5，自动生成）
            if "region" in location_info:
                tags.append(UserTag(
                    category=TagCategory.REGION,
                    name=location_info["region"],
                    weight=1.5,
                    source=TagSource.REGION_AUTO,
                    created_at=datetime.utcnow()
                ))
            
            # 4. 能源类型标签（如果提供，权重设为2.0，与省份标签相当）
            if energy_types:
                for energy_type in energy_types:
                    tags.append(UserTag(
                        category=TagCategory.ENERGY_TYPE,
                        name=energy_type,
                        weight=2.0,  # 提升能源类型权重
                        source=TagSource.PRESET,
                        created_at=datetime.utcnow()
                    ))
            
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
            raise Exception(f"Failed to initialize user tags: {str(e)}")

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

    async def update_user_tags(self, user_id: str, tags: List[UserTag]) -> UserTags:
        """更新用户标签"""
        try:
            # 验证标签数据
            self._validate_tags(tags)
            
            user_tags = UserTags(
                user_id=user_id,
                tags=tags,
                updated_at=datetime.utcnow()
            )
            
            # 更新或插入文档
            await self.user_tags_collection.replace_one(
                {"user_id": user_id},
                user_tags.dict(),
                upsert=True
            )
            
            return user_tags
        except Exception as e:
            raise Exception(f"Failed to update user tags: {str(e)}")

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