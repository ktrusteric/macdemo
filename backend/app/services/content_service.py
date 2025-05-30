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
            
            # 添加分类统计日志
            if not content_type and not tags:  # 只在获取全部内容时统计
                print("📊 内容分类统计:")
                
                # 按type字段统计
                type_stats = {}
                basic_info_stats = {}
                
                async for doc in self.collection.find({}):
                    doc_type = doc.get('type')
                    basic_info_tags = doc.get('basic_info_tags', [])
                    
                    # 统计type
                    if doc_type:
                        type_stats[doc_type] = type_stats.get(doc_type, 0) + 1
                    
                    # 统计basic_info_tags
                    for tag in basic_info_tags:
                        basic_info_stats[tag] = basic_info_stats.get(tag, 0) + 1
                
                print(f"  📈 行情咨询 (行业资讯): {basic_info_stats.get('行业资讯', 0)}篇")
                print(f"  📋 政策法规 (政策法规): {basic_info_stats.get('政策法规', 0)}篇")
                print(f"  📢 交易公告 (交易公告): {basic_info_stats.get('交易公告', 0)}篇")
                print(f"  💰 调价公告 (调价公告): {basic_info_stats.get('调价公告', 0)}篇")
                print(f"  📊 总公告数: {basic_info_stats.get('交易公告', 0) + basic_info_stats.get('调价公告', 0)}篇")
                print(f"  📚 总文章数: {sum(type_stats.values())}篇")
                print(f"  🏷️ 按type统计: {type_stats}")
            
            cursor = self.collection.find(query).sort(sort_condition).skip(skip).limit(limit)
            
            async for document in cursor:
                # 正确处理 MongoDB ObjectId
                if '_id' in document:
                    document['id'] = str(document['_id'])
                    del document['_id']  # 删除原始的 _id 字段
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
                # 正确处理 MongoDB ObjectId
                if '_id' in document:
                    document['id'] = str(document['_id'])
                    del document['_id']  # 删除原始的 _id 字段
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
                # 正确处理 MongoDB ObjectId
                if '_id' in document:
                    document['id'] = str(document['_id'])
                    del document['_id']  # 删除原始的 _id 字段
                contents.append(Content(**document))
            
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
            # 构建查询条件
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
            
            # 使用$or查询匹配任一标签
            query = {"$or": tag_conditions}
            
            contents = []
            cursor = self.collection.find(query).sort([("publish_time", -1)]).limit(limit)
            
            async for document in cursor:
                # 正确处理 MongoDB ObjectId
                if '_id' in document:
                    document['id'] = str(document['_id'])
                    del document['_id']  # 删除原始的 _id 字段
                contents.append(Content(**document))
            
            return contents
        except Exception as e:
            raise Exception(f"Failed to get content by tags: {str(e)}") 