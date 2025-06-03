from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.user import UserRole, AdminPermission, User, UserProfile
from app.models.content import Content, ContentCreateRequest, ContentUpdateRequest, JsonArticle, CONTENT_TYPE_MAP
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.database import get_database
from app.utils.region_mapper import RegionMapper
from app.services.user_service import UserService
from app.utils.tag_processor import TagProcessor
from app.core.config import settings
import logging
import json
import ast
from bson import ObjectId

logger = logging.getLogger(__name__)

# 硬编码的管理员账户配置
BUILTIN_ADMIN_ACCOUNTS = {
    "admin": {
        "username": "admin",
        "email": "admin@energy-system.com",
        "password_hash": get_password_hash("admin123456"),  # 默认密码
        "role": UserRole.ADMIN,
        "is_active": True,
        "register_city": "北京"
    },
    "superadmin": {
        "username": "superadmin", 
        "email": "superadmin@energy-system.com",
        "password_hash": get_password_hash("super123456"),  # 超级管理员密码
        "role": UserRole.ADMIN,
        "is_active": True,
        "register_city": "北京"
    }
}

class AdminService:
    def __init__(self, db):
        self.db = db
        self.users_collection = db.users
        self.content_collection = db.content
        
    async def authenticate_admin(self, username: str, password: str) -> Optional[User]:
        """管理员认证 - 使用硬编码账户"""
        try:
            logger.info(f"🔐 尝试管理员认证: {username}")
            
            # 检查是否是内置管理员账户
            admin_account = None
            
            # 支持用户名或邮箱登录
            for account_key, account_info in BUILTIN_ADMIN_ACCOUNTS.items():
                if (username == account_info["username"] or 
                    username == account_info["email"]):
                    admin_account = account_info
                    break
            
            if not admin_account:
                logger.warning(f"❌ 管理员账户不存在: {username}")
                return None
            
            # 验证密码
            if not verify_password(password, admin_account["password_hash"]):
                logger.warning(f"❌ 管理员密码错误: {username}")
                return None
            
            # 创建管理员用户对象
            admin_user = User(
                id=f"builtin_admin_{admin_account['username']}",  # 使用特殊ID标识内置管理员
                email=admin_account["email"],
                username=admin_account["username"],
                role=admin_account["role"],
                is_active=admin_account["is_active"],
                created_at=datetime.utcnow().isoformat(),
                has_initial_tags=True,  # 管理员默认已配置标签
                register_city=admin_account["register_city"]
            )
            
            logger.info(f"✅ 管理员认证成功: {username}")
            return admin_user
            
        except Exception as e:
            logger.error(f"❌ 管理员认证异常: {str(e)}")
            return None
    
    def get_admin_permissions(self, user_role: UserRole) -> List[str]:
        """获取管理员权限列表"""
        if user_role == UserRole.ADMIN:
            return [
                AdminPermission.MANAGE_ARTICLES,
                AdminPermission.MANAGE_USERS,
                AdminPermission.MANAGE_TAGS,
                AdminPermission.VIEW_ANALYTICS,
                AdminPermission.SYSTEM_CONFIG
            ]
        return []
    
    async def create_article(self, article_data: ContentCreateRequest, admin_id: str) -> Content:
        """创建文章"""
        try:
            # 创建文章对象
            article_dict = article_data.dict()
            article_dict["id"] = str(ObjectId())
            article_dict["created_at"] = datetime.utcnow()
            article_dict["updated_at"] = datetime.utcnow()
            
            if not article_dict.get("publish_time"):
                article_dict["publish_time"] = datetime.utcnow()
            
            # 插入数据库
            result = await self.content_collection.insert_one(article_dict)
            
            # 返回创建的文章
            article_dict["_id"] = str(result.inserted_id)
            content = Content(**article_dict)
            
            logger.info(f"管理员 {admin_id} 创建文章成功: {content.title}")
            return content
            
        except Exception as e:
            logger.error(f"创建文章失败: {str(e)}")
            raise Exception(f"创建文章失败: {str(e)}")
    
    async def update_article(self, article_id: str, update_data: ContentUpdateRequest, admin_id: str) -> Content:
        """更新文章"""
        try:
            # 检查文章是否存在
            existing_article = await self.content_collection.find_one({"_id": ObjectId(article_id)})
            if not existing_article:
                raise Exception("文章不存在")
            
            # 准备更新数据
            update_dict = {}
            for field, value in update_data.dict(exclude_unset=True).items():
                if value is not None:
                    update_dict[field] = value
            
            update_dict["updated_at"] = datetime.utcnow()
            
            # 更新数据库
            await self.content_collection.update_one(
                {"_id": ObjectId(article_id)},
                {"$set": update_dict}
            )
            
            # 获取更新后的文章
            updated_article = await self.content_collection.find_one({"_id": ObjectId(article_id)})
            updated_article["id"] = str(updated_article["_id"])
            content = Content(**updated_article)
            
            logger.info(f"管理员 {admin_id} 更新文章成功: {content.title}")
            return content
            
        except Exception as e:
            logger.error(f"更新文章失败: {str(e)}")
            raise Exception(f"更新文章失败: {str(e)}")
    
    async def delete_article(self, article_id: str, admin_id: str) -> bool:
        """删除文章"""
        try:
            # 检查文章是否存在
            existing_article = await self.content_collection.find_one({"_id": ObjectId(article_id)})
            if not existing_article:
                raise Exception("文章不存在")
            
            # 删除文章
            result = await self.content_collection.delete_one({"_id": ObjectId(article_id)})
            
            if result.deleted_count > 0:
                logger.info(f"管理员 {admin_id} 删除文章成功: {existing_article.get('title', 'Unknown')}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"删除文章失败: {str(e)}")
            raise Exception(f"删除文章失败: {str(e)}")
    
    def parse_json_tags(self, tag_string: Optional[str]) -> List[str]:
        """解析JSON字符串格式的标签（使用统一的TagProcessor）"""
        return TagProcessor.safe_parse_tags(tag_string)
    
    def convert_json_article_to_content(self, json_article: JsonArticle) -> Dict[str, Any]:
        """将JSON格式的文章转换为Content格式"""
        try:
            # 处理发布时间
            publish_time = datetime.utcnow()
            try:
                if json_article.发布时间:
                    publish_time = datetime.strptime(json_article.发布时间, "%Y-%m-%d")
            except:
                try:
                    publish_time = datetime.strptime(json_article.发布日期, "%Y-%m-%d")
                except:
                    pass
            
            # 🔥 解析基础信息标签，基于此确定内容类型
            basic_info_tags = self.parse_json_tags(json_article.基础信息标签)
            
            # 🔥 基于基础信息标签确定内容类型
            content_type = "news"  # 默认为行业资讯
            if basic_info_tags:
                # 按优先级匹配内容类型
                if "政策法规" in basic_info_tags:
                    content_type = "policy"
                elif "调价公告" in basic_info_tags:
                    content_type = "price"
                elif "交易公告" in basic_info_tags:
                    content_type = "announcement"
                elif "行业资讯" in basic_info_tags:
                    content_type = "news"
            
            # 解析其他标签
            region_tags = self.parse_json_tags(json_article.地域标签)
            energy_type_tags = json_article.能源品种标签 or []
            business_field_tags = self.parse_json_tags(json_article.业务领域标签)
            beneficiary_tags = self.parse_json_tags(json_article.受益主体标签)
            policy_measure_tags = self.parse_json_tags(json_article.关键措施标签)
            importance_tags = self.parse_json_tags(json_article.重要性标签)
            
            # 添加规范化地域标签
            if json_article.规范化地域标签:
                region_tags.extend(json_article.规范化地域标签)
            
            # 去重
            region_tags = list(set(region_tags))
            
            content_dict = {
                "title": json_article.标题,
                "content": json_article.文章内容,
                "type": content_type,  # 🔥 基于basic_info_tags生成
                "source": json_article.来源机构,
                "publish_time": publish_time,
                "link": json_article.链接,
                "basic_info_tags": basic_info_tags,
                "region_tags": region_tags,
                "energy_type_tags": energy_type_tags,
                "business_field_tags": business_field_tags,
                "beneficiary_tags": beneficiary_tags,
                "policy_measure_tags": policy_measure_tags,
                "importance_tags": importance_tags,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "view_count": 0
            }
            
            return content_dict
            
        except Exception as e:
            logger.error(f"转换JSON文章失败: {str(e)}")
            raise Exception(f"转换JSON文章失败: {str(e)}")
    
    async def batch_import_articles(self, articles: List[JsonArticle], admin_id: str, 
                                  auto_parse_tags: bool = True, overwrite_existing: bool = False) -> Dict[str, Any]:
        """批量导入文章"""
        try:
            total_articles = len(articles)
            imported_count = 0
            updated_count = 0
            failed_count = 0
            failed_articles = []
            
            for i, json_article in enumerate(articles):
                try:
                    # 转换为Content格式
                    content_dict = self.convert_json_article_to_content(json_article)
                    
                    # 检查是否已存在相同标题的文章
                    existing_article = await self.content_collection.find_one({
                        "title": content_dict["title"]
                    })
                    
                    if existing_article:
                        if overwrite_existing:
                            # 更新现有文章
                            content_dict["updated_at"] = datetime.utcnow()
                            await self.content_collection.update_one(
                                {"_id": existing_article["_id"]},
                                {"$set": content_dict}
                            )
                            updated_count += 1
                            logger.info(f"更新文章: {content_dict['title']}")
                        else:
                            logger.info(f"跳过已存在的文章: {content_dict['title']}")
                            continue
                    else:
                        # 插入新文章
                        content_dict["_id"] = ObjectId()
                        await self.content_collection.insert_one(content_dict)
                        imported_count += 1
                        logger.info(f"导入新文章: {content_dict['title']}")
                        
                except Exception as e:
                    failed_count += 1
                    failed_articles.append({
                        "index": i,
                        "title": getattr(json_article, "标题", "Unknown"),
                        "error": str(e)
                    })
                    logger.error(f"导入文章失败 (索引 {i}): {str(e)}")
            
            result = {
                "success": True,
                "total_articles": total_articles,
                "imported_count": imported_count,
                "updated_count": updated_count,
                "failed_count": failed_count,
                "failed_articles": failed_articles,
                "message": f"批量导入完成: 新增 {imported_count} 篇，更新 {updated_count} 篇，失败 {failed_count} 篇"
            }
            
            logger.info(f"管理员 {admin_id} 批量导入文章完成: {result['message']}")
            return result
            
        except Exception as e:
            logger.error(f"批量导入文章失败: {str(e)}")
            return {
                "success": False,
                "total_articles": len(articles),
                "imported_count": 0,
                "updated_count": 0,
                "failed_count": len(articles),
                "failed_articles": [],
                "message": f"批量导入失败: {str(e)}"
            }
    
    async def get_articles_for_management(self, page: int = 1, page_size: int = 20, 
                                        content_type: Optional[str] = None,
                                        energy_type: Optional[str] = None,
                                        search_keyword: Optional[str] = None,
                                        tag_search: Optional[str] = None) -> Dict[str, Any]:
        """获取文章管理列表"""
        try:
            skip = (page - 1) * page_size
            
            # 构建查询条件
            query = {}
            
            # 🔥 文章类型筛选 - 统一使用type字段
            if content_type:
                query["type"] = content_type
            
            # 能源类型筛选
            if energy_type:
                query["energy_type_tags"] = {"$in": [energy_type]}
            
            # 关键词搜索
            if search_keyword:
                search_conditions = [
                    {"标题": {"$regex": search_keyword, "$options": "i"}},
                    {"文章内容": {"$regex": search_keyword, "$options": "i"}},
                    {"title": {"$regex": search_keyword, "$options": "i"}},
                    {"content": {"$regex": search_keyword, "$options": "i"}}
                ]
                
                if "$or" in query:
                    # 如果已经有$or条件，需要合并
                    query = {"$and": [query, {"$or": search_conditions}]}
                else:
                    query["$or"] = search_conditions
            
            # 标签搜索
            if tag_search:
                tag_conditions = [
                    {"basic_info_tags": {"$regex": tag_search, "$options": "i"}},
                    {"region_tags": {"$regex": tag_search, "$options": "i"}},
                    {"energy_type_tags": {"$regex": tag_search, "$options": "i"}},
                    {"business_field_tags": {"$regex": tag_search, "$options": "i"}},
                    {"beneficiary_tags": {"$regex": tag_search, "$options": "i"}},
                    {"policy_measure_tags": {"$regex": tag_search, "$options": "i"}},
                    {"importance_tags": {"$regex": tag_search, "$options": "i"}}
                ]
                
                if "$and" in query:
                    # 如果已经有$and条件，添加到其中
                    query["$and"].append({"$or": tag_conditions})
                elif "$or" in query:
                    # 如果有$or条件，需要用$and包装
                    query = {"$and": [query, {"$or": tag_conditions}]}
                else:
                    query["$or"] = tag_conditions
            
            logger.info(f"🔍 MongoDB查询条件: {query}")
            
            # 获取总数
            total_count = await self.content_collection.count_documents(query)
            logger.info(f"📊 查询结果总数: {total_count}")
            
            # 获取文章列表
            cursor = self.content_collection.find(query).sort("导入时间", -1).skip(skip).limit(page_size)
            articles = []
            
            async for doc in cursor:
                try:
                    # 中文字段名到英文字段名的映射
                    mapped_doc = {
                        "id": str(doc["_id"]),
                        "title": doc.get("标题") or doc.get("title", "无标题"),
                        "content": doc.get("文章内容") or doc.get("content", "无内容"),
                        "source": doc.get("来源机构") or doc.get("source", "未知来源"),
                        "link": doc.get("链接") or doc.get("link", ""),
                        "publish_time": doc.get("发布时间") or doc.get("publish_time", datetime.utcnow()),
                        
                        # 🔥 type字段 - 优先使用已有的type字段
                        "type": doc.get("type", "news"),
                        
                        # 标签字段（这些已经是英文字段名）
                        "basic_info_tags": doc.get("basic_info_tags", []),
                        "region_tags": doc.get("region_tags", []),
                        "energy_type_tags": doc.get("energy_type_tags", []),
                        "business_field_tags": doc.get("business_field_tags", []),
                        "beneficiary_tags": doc.get("beneficiary_tags", []),
                        "policy_measure_tags": doc.get("policy_measure_tags", []),
                        "importance_tags": doc.get("importance_tags", []),
                        
                        # 时间字段
                        "created_at": doc.get("导入时间") or doc.get("created_at", datetime.utcnow()),
                        "updated_at": doc.get("导入时间") or doc.get("updated_at", datetime.utcnow()),
                        "view_count": doc.get("view_count", 0)
                    }
                    
                    # 处理发布时间格式
                    if isinstance(mapped_doc["publish_time"], str):
                        try:
                            mapped_doc["publish_time"] = datetime.strptime(mapped_doc["publish_time"], "%Y-%m-%d")
                        except:
                            mapped_doc["publish_time"] = datetime.utcnow()
                    
                    # 创建Content对象
                    content = Content(**mapped_doc)
                    articles.append(content)
                    
                except Exception as e:
                    logger.warning(f"跳过无效文档 {doc.get('_id')}: {str(e)}")
                    continue
            
            logger.info(f"✅ 成功处理 {len(articles)} 篇文章")
            
            return {
                "items": articles,
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "has_next": (skip + len(articles)) < total_count
            }
            
        except Exception as e:
            logger.error(f"获取文章管理列表失败: {str(e)}")
            raise Exception(f"获取文章管理列表失败: {str(e)}")
    
    def _map_document_type(self, chinese_type: str) -> str:
        """将中文文档类型映射为英文类型"""
        type_mapping = {
            "政策法规": "policy",
            "行业资讯": "news", 
            "调价公告": "price",
            "交易公告": "announcement"
        }
        return type_mapping.get(chinese_type, "news") 