from typing import List, Optional, Dict, Any
from pymongo.database import Database
from bson import ObjectId
from app.models.content import Content, ContentType
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ContentService:
    def __init__(self, database: Database):
        self.db = database
        self.collection = self.db.content

    async def create_content(self, content: Content) -> Content:
        """创建内容"""
        try:
            content_dict = content.dict()
            content_dict['_id'] = ObjectId()
            
            result = await self.collection.insert_one(content_dict)
            content.id = str(result.inserted_id)
            
            return content
        except Exception as e:
            raise Exception(f"Failed to create content: {str(e)}")

    def _map_document_to_content(self, document: dict) -> Content:
        """将数据库文档映射为Content对象（支持中英文字段）"""
        try:
            # 智能字段映射：优先使用英文字段，如果不存在则使用中文字段
            mapped_doc = {
                "id": str(document["_id"]),
                
                # 标题字段 - 优先英文，后备中文
                "title": document.get("title") or document.get("标题", "无标题"),
                
                # 内容字段 - 优先英文，后备中文
                "content": document.get("content") or document.get("文章内容", "无内容"),
                
                # 来源字段 - 优先英文，后备中文
                "source": document.get("source") or document.get("来源机构", "未知来源"),
                
                # 链接字段 - 优先英文，后备中文
                "link": document.get("link") or document.get("链接", ""),
                
                # 发布时间 - 优先英文，后备中文，最后默认当前时间
                "publish_time": self._parse_publish_time(document),
                
                # 处理文档类型映射 - 优先英文，后备中文
                "type": document.get("type") or self._map_document_type(document.get("文档类型", "行业资讯")),
                
                # 标签字段（都是英文字段名）
                "basic_info_tags": self._ensure_list(document.get("basic_info_tags", [])),
                "region_tags": self._ensure_list(document.get("region_tags", [])),
                "energy_type_tags": self._ensure_list(document.get("energy_type_tags", [])),
                "business_field_tags": self._ensure_list(document.get("business_field_tags", [])),
                "beneficiary_tags": self._ensure_list(document.get("beneficiary_tags", [])),
                "policy_measure_tags": self._ensure_list(document.get("policy_measure_tags", [])),
                "importance_tags": self._ensure_list(document.get("importance_tags", [])),
                
                # 时间字段 - 优先英文，后备中文
                "created_at": self._parse_datetime(document.get("created_at") or document.get("导入时间")),
                "updated_at": self._parse_datetime(document.get("updated_at") or document.get("导入时间")),
                "view_count": max(0, int(document.get("view_count", 0)))  # 确保非负数
            }
            
            return Content(**mapped_doc)
            
        except Exception as e:
            error_msg = f"Failed to map document to content: {str(e)}"
            logger.error(f"{error_msg} - Document ID: {document.get('_id', 'Unknown')}")
            raise Exception(error_msg)
    
    def _parse_publish_time(self, document: dict) -> datetime:
        """解析发布时间字段"""
        # 尝试多个时间字段
        time_candidates = [
            document.get("publish_time"),
            document.get("发布时间"),
            document.get("发布日期"),
            document.get("created_at"),
            document.get("导入时间")
        ]
        
        for time_value in time_candidates:
            if time_value:
                parsed_time = self._parse_datetime(time_value)
                if parsed_time:
                    return parsed_time
        
        # 所有解析都失败，返回当前时间
        return datetime.utcnow()
    
    def _parse_datetime(self, time_value) -> datetime:
        """解析datetime字段"""
        if not time_value:
            return datetime.utcnow()
        
        if isinstance(time_value, datetime):
            return time_value
        
        if isinstance(time_value, str):
            try:
                # 尝试标准日期格式 YYYY-MM-DD
                return datetime.strptime(time_value, "%Y-%m-%d")
            except ValueError:
                try:
                    # 尝试ISO格式解析
                    return datetime.fromisoformat(time_value.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        # 尝试其他常见格式
                        return datetime.strptime(time_value[:19], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        logger.warning(f"无法解析时间格式: {time_value}")
                        return datetime.utcnow()
        
        return datetime.utcnow()
    
    def _ensure_list(self, value) -> list:
        """确保值是列表格式"""
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if item and str(item).strip()]
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        try:
            # 尝试转换为字符串再包装为列表
            return [str(value).strip()] if str(value).strip() else []
        except:
            return []

    def _map_document_type(self, chinese_type: str) -> str:
        """将中文文档类型映射为英文类型"""
        type_mapping = {
            "政策法规": "policy",
            "行业资讯": "news", 
            "调价公告": "price",
            "交易公告": "announcement"
        }
        return type_mapping.get(chinese_type, "news")

    async def get_content_by_id(self, content_id: str) -> Optional[Content]:
        """根据ID获取内容"""
        try:
            document = await self.collection.find_one({"_id": ObjectId(content_id)})
            if document:
                return self._map_document_to_content(document)
            return None
        except Exception as e:
            raise Exception(f"Failed to get content by id: {str(e)}")

    async def get_content_list(
        self,
        content_type: str = None,
        tags: List[str] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "latest"
    ) -> List[Content]:
        """获取内容列表"""
        try:
            # 构建查询条件
            query = {}
            
            # 内容类型筛选（使用basic_info_tags字段）
            if content_type:
                # 将英文类型映射到中文标签进行查询
                reverse_type_mapping = {
                    "policy": "政策法规",
                    "news": "行业资讯",
                    "price": "调价公告", 
                    "announcement": "交易公告"
                }
                chinese_type = reverse_type_mapping.get(content_type, content_type)
                query["basic_info_tags"] = chinese_type
            
            # 标签筛选
            if tags:
                tag_conditions = []
                tag_fields = [
                    'basic_info_tags', 'region_tags', 'energy_type_tags',
                    'business_field_tags', 'beneficiary_tags', 
                    'policy_measure_tags', 'importance_tags'
                ]
                
                for field in tag_fields:
                    tag_conditions.append({field: {"$in": tags}})
                
                if tag_conditions:
                    query["$or"] = tag_conditions
            
            # 排序设置
            sort_field = "导入时间" if sort_by == "latest" else "发布时间"
            sort_order = -1  # 降序
            
            contents = []
            cursor = self.collection.find(query).sort([(sort_field, sort_order)]).skip(skip).limit(limit)
            
            async for document in cursor:
                try:
                    content = self._map_document_to_content(document)
                    contents.append(content)
                except Exception as e:
                    logger.warning(f"跳过无效文档 {document.get('_id')}: {str(e)}")
                    continue
            
            return contents
        except Exception as e:
            raise Exception(f"Failed to get content list: {str(e)}")

    async def get_content_count(
        self,
        content_type: str = None,
        tags: List[str] = None,
        search_keyword: str = None
    ) -> int:
        """获取内容总数"""
        try:
            query = {}
            
            if content_type:
                query["type"] = content_type
            
            if search_keyword:
                query["$or"] = [
                    {"title": {"$regex": search_keyword, "$options": "i"}},
                    {"content": {"$regex": search_keyword, "$options": "i"}}
                ]
            
            if tags:
                tag_queries = []
                for tag in tags:
                    tag_queries.extend([
                        {"basic_info_tags": tag},
                        {"region_tags": tag},
                        {"energy_type_tags": tag},
                        {"business_field_tags": tag},
                        {"beneficiary_tags": tag},
                        {"policy_measure_tags": tag},
                        {"importance_tags": tag}
                    ])
                if "$or" in query:
                    # 如果已经有搜索条件，需要结合
                    query = {"$and": [query, {"$or": tag_queries}]}
                else:
                    query["$or"] = tag_queries
            
            count = await self.collection.count_documents(query)
            return count
        except Exception as e:
            raise Exception(f"Failed to get content count: {str(e)}")

    async def get_search_count(
        self,
        keyword: str,
        content_type: str = None,
        tags: List[str] = None
    ) -> int:
        """获取搜索结果总数"""
        return await self.get_content_count(
            content_type=content_type,
            tags=tags,
            search_keyword=keyword
        )

    async def get_all_tags(self) -> List[str]:
        """获取所有可用的标签"""
        try:
            pipeline = [
                {
                    "$project": {
                        "all_tags": {
                            "$concatArrays": [
                                "$basic_info_tags",
                                "$region_tags", 
                                "$energy_type_tags",
                                "$business_field_tags",
                                "$beneficiary_tags",
                                "$policy_measure_tags",
                                "$importance_tags"
                            ]
                        }
                    }
                },
                {"$unwind": "$all_tags"},
                {"$group": {"_id": "$all_tags"}},
                {"$sort": {"_id": 1}}
            ]
            
            tags = []
            async for doc in self.collection.aggregate(pipeline):
                if doc['_id']:  # 过滤空标签
                    tags.append(doc['_id'])
            
            return tags
        except Exception as e:
            raise Exception(f"Failed to get all tags: {str(e)}")

    async def increment_view_count(self, content_id: str) -> None:
        """增加内容浏览次数"""
        try:
            await self.collection.update_one(
                {"_id": ObjectId(content_id)},
                {"$inc": {"view_count": 1}}
            )
        except Exception as e:
            raise Exception(f"Failed to increment view count: {str(e)}")

    async def search_content(
        self,
        keyword: str,
        content_type: str = None,
        tags: List[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Content]:
        """搜索内容"""
        try:
            query = {
                "$or": [
                    {"标题": {"$regex": keyword, "$options": "i"}},
                    {"文章内容": {"$regex": keyword, "$options": "i"}}
                ]
            }
            
            # 添加内容类型筛选
            if content_type:
                reverse_type_mapping = {
                    "policy": "政策法规",
                    "news": "行业资讯",
                    "price": "调价公告", 
                    "announcement": "交易公告"
                }
                chinese_type = reverse_type_mapping.get(content_type, content_type)
                query["basic_info_tags"] = chinese_type
            
            # 添加标签筛选
            if tags:
                tag_queries = []
                for tag in tags:
                    tag_queries.extend([
                        {"basic_info_tags": tag},
                        {"region_tags": tag},
                        {"energy_type_tags": tag},
                        {"business_field_tags": tag},
                        {"beneficiary_tags": tag},
                        {"policy_measure_tags": tag},
                        {"importance_tags": tag}
                    ])
                query = {"$and": [query, {"$or": tag_queries}]}
            
            contents = []
            cursor = self.collection.find(query).sort([("发布时间", -1)]).skip(skip).limit(limit)
            
            async for document in cursor:
                try:
                    content = self._map_document_to_content(document)
                    contents.append(content)
                except Exception as e:
                    logger.warning(f"跳过无效文档 {document.get('_id')}: {str(e)}")
                    continue
            
            return contents
        except Exception as e:
            raise Exception(f"Failed to search content: {str(e)}")

    async def get_content_by_user_tags(
        self,
        user_tags: List[str],
        skip: int = 0,
        limit: int = 20
    ) -> List[Content]:
        """根据用户标签获取推荐内容"""
        try:
            # 构建复杂的标签匹配查询
            tag_conditions = []
            tag_fields = [
                'basic_info_tags', 'region_tags', 'energy_type_tags',
                'business_field_tags', 'beneficiary_tags', 
                'policy_measure_tags', 'importance_tags'
            ]
            
            for field in tag_fields:
                tag_conditions.append({field: {"$in": user_tags}})
            
            query = {"$or": tag_conditions}
            
            # 使用聚合管道计算匹配分数
            pipeline = [
                {"$match": query},
                {
                    "$addFields": {
                        "match_score": {
                            "$sum": [
                                {"$size": {"$setIntersection": ["$basic_info_tags", user_tags]}},
                                {"$size": {"$setIntersection": ["$region_tags", user_tags]}},
                                {"$size": {"$setIntersection": ["$energy_type_tags", user_tags]}},
                                {"$size": {"$setIntersection": ["$business_field_tags", user_tags]}},
                                {"$size": {"$setIntersection": ["$beneficiary_tags", user_tags]}},
                                {"$size": {"$setIntersection": ["$policy_measure_tags", user_tags]}},
                                {"$size": {"$setIntersection": ["$importance_tags", user_tags]}}
                            ]
                        }
                    }
                },
                {"$sort": {"match_score": -1, "发布时间": -1}},
                {"$skip": skip},
                {"$limit": limit}
            ]
            
            contents = []
            async for document in self.collection.aggregate(pipeline):
                try:
                    content = self._map_document_to_content(document)
                    contents.append(content)
                except Exception as e:
                    logger.warning(f"跳过无效文档 {document.get('_id')}: {str(e)}")
                    continue
            
            return contents
        except Exception as e:
            raise Exception(f"Failed to get content by user tags: {str(e)}")

    async def get_content_by_tags(
        self,
        basic_info_tags: List[str] = None,
        region_tags: List[str] = None,
        energy_type_tags: List[str] = None,
        business_field_tags: List[str] = None,
        beneficiary_tags: List[str] = None,
        policy_measure_tags: List[str] = None,
        importance_tags: List[str] = None,
        limit: int = 10
    ) -> List[Content]:
        """根据分类标签获取内容"""
        try:
            # 构建查询条件 - 使用$and确保所有指定的标签都匹配
            tag_conditions = []
            
            if basic_info_tags:
                tag_conditions.append({"basic_info_tags": {"$in": basic_info_tags}})
            if region_tags:
                tag_conditions.append({"region_tags": {"$in": region_tags}})
            if energy_type_tags:
                tag_conditions.append({"energy_type_tags": {"$in": energy_type_tags}})
            if business_field_tags:
                tag_conditions.append({"business_field_tags": {"$in": business_field_tags}})
            if beneficiary_tags:
                tag_conditions.append({"beneficiary_tags": {"$in": beneficiary_tags}})
            if policy_measure_tags:
                tag_conditions.append({"policy_measure_tags": {"$in": policy_measure_tags}})
            if importance_tags:
                tag_conditions.append({"importance_tags": {"$in": importance_tags}})
            
            if not tag_conditions:
                # 如果没有标签条件，返回最新内容
                return await self.get_content_list(limit=limit, sort_by="latest")
            
            # 使用$and查询确保所有指定标签都匹配
            if len(tag_conditions) == 1:
                query = tag_conditions[0]
            else:
                query = {"$and": tag_conditions}
            
            contents = []
            cursor = self.collection.find(query).sort([("发布时间", -1)]).limit(limit)
            
            async for document in cursor:
                try:
                    content = self._map_document_to_content(document)
                    contents.append(content)
                except Exception as e:
                    logger.warning(f"跳过无效文档 {document.get('_id')}: {str(e)}")
                    continue
            
            return contents
        except Exception as e:
            raise Exception(f"Failed to get content by tags: {str(e)}") 