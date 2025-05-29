from typing import List, Optional, Dict, Any
from pymongo.database import Database
from bson import ObjectId
from app.models.content import Content, ContentType
from datetime import datetime

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

    async def get_content_by_id(self, content_id: str) -> Optional[Content]:
        """通过ID获取内容"""
        try:
            document = await self.collection.find_one({"_id": ObjectId(content_id)})
            if not document:
                return None
            
            document['id'] = str(document['_id'])
            return Content(**document)
        except Exception as e:
            raise Exception(f"Failed to get content: {str(e)}")

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
            query = {}
            
            if content_type:
                query["type"] = content_type
            
            # 构建标签查询
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
                query["$or"] = tag_queries
            
            # 构建排序条件
            sort_conditions = {
                "latest": [("publish_time", -1)],
                "popularity": [("view_count", -1), ("publish_time", -1)],
                "relevance": [("publish_time", -1)]  # 默认按时间排序，相关性由推荐算法处理
            }
            sort_condition = sort_conditions.get(sort_by, [("publish_time", -1)])
            
            contents = []
            cursor = self.collection.find(query).sort(sort_condition).skip(skip).limit(limit)
            
            async for document in cursor:
                document['id'] = str(document['_id'])
                contents.append(Content(**document))
            
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
                    {"title": {"$regex": keyword, "$options": "i"}},
                    {"content": {"$regex": keyword, "$options": "i"}}
                ]
            }
            
            # 添加内容类型筛选
            if content_type:
                query["type"] = content_type
            
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
            cursor = self.collection.find(query).sort([("publish_time", -1)]).skip(skip).limit(limit)
            
            async for document in cursor:
                document['id'] = str(document['_id'])
                contents.append(Content(**document))
            
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
                {"$sort": {"match_score": -1, "publish_time": -1}},
                {"$skip": skip},
                {"$limit": limit}
            ]
            
            contents = []
            async for document in self.collection.aggregate(pipeline):
                document['id'] = str(document['_id'])
                contents.append(Content(**document))
            
            return contents
        except Exception as e:
            raise Exception(f"Failed to get content by user tags: {str(e)}") 