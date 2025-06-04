from datetime import datetime
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import logging

from app.models.user_behavior import UserFavorite, UserBehaviorStats, FavoriteResponse
from app.models.content import Content
from app.models.user import UserTag, TagCategory, TagSource
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

class FavoriteService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.favorites_collection = db.user_favorites
        self.content_collection = db.content
        self.user_service = UserService(db)
    
    async def add_favorite(self, user_id: str, content_id: str) -> FavoriteResponse:
        """
        添加收藏并学习标签
        """
        try:
            # 检查是否已经收藏
            existing = await self.favorites_collection.find_one({
                "user_id": user_id,
                "content_id": content_id
            })
            
            if existing:
                return FavoriteResponse(
                    success=False,
                    message="文章已经收藏过了",
                    total_favorites=await self.get_user_favorites_count(user_id)
                )
            
            # 获取文章内容
            content_doc = await self.content_collection.find_one({"_id": ObjectId(content_id)})
            if not content_doc:
                return FavoriteResponse(
                    success=False,
                    message="文章不存在",
                    total_favorites=await self.get_user_favorites_count(user_id)
                )
            
            # 创建收藏记录
            favorite = UserFavorite(
                user_id=user_id,
                content_id=content_id,
                energy_type_tags=content_doc.get("energy_type_tags", []),
                region_tags=content_doc.get("region_tags", []),
                business_field_tags=content_doc.get("business_field_tags", [])
            )
            
            # 保存收藏记录
            result = await self.favorites_collection.insert_one(favorite.dict(exclude={"id"}))
            
            # 学习标签
            learned_tags = await self._learn_tags_from_content(user_id, content_doc)
            
            # 更新收藏记录的学习状态
            await self.favorites_collection.update_one(
                {"_id": result.inserted_id},
                {
                    "$set": {
                        "tags_learned": True,
                        "learned_at": datetime.now()
                    }
                }
            )
            
            total_favorites = await self.get_user_favorites_count(user_id)
            
            return FavoriteResponse(
                success=True,
                message="收藏成功，已学习相关标签",
                learned_tags=learned_tags,
                total_favorites=total_favorites
            )
            
        except Exception as e:
            logger.error(f"添加收藏失败: {str(e)}")
            return FavoriteResponse(
                success=False,
                message=f"收藏失败: {str(e)}",
                total_favorites=await self.get_user_favorites_count(user_id)
            )
    
    async def remove_favorite(self, user_id: str, content_id: str) -> FavoriteResponse:
        """
        取消收藏（不删除已学习的标签）
        """
        try:
            result = await self.favorites_collection.delete_one({
                "user_id": user_id,
                "content_id": content_id
            })
            
            if result.deleted_count == 0:
                return FavoriteResponse(
                    success=False,
                    message="该文章未收藏或已取消收藏",
                    total_favorites=await self.get_user_favorites_count(user_id)
                )
            
            total_favorites = await self.get_user_favorites_count(user_id)
            
            return FavoriteResponse(
                success=True,
                message="取消收藏成功",
                total_favorites=total_favorites
            )
            
        except Exception as e:
            logger.error(f"取消收藏失败: {str(e)}")
            return FavoriteResponse(
                success=False,
                message=f"取消收藏失败: {str(e)}",
                total_favorites=await self.get_user_favorites_count(user_id)
            )
    
    async def get_user_favorites(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取用户收藏的文章列表
        """
        try:
            # 聚合查询，关联文章内容
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$sort": {"favorited_at": -1}},
                {"$limit": limit},
                {
                    "$addFields": {
                        "content_object_id": {"$toObjectId": "$content_id"}
                    }
                },
                {
                    "$lookup": {
                        "from": "content",
                        "localField": "content_object_id",
                        "foreignField": "_id",
                        "as": "content"
                    }
                },
                {"$unwind": "$content"},
                {
                    "$project": {
                        "content_id": 1,
                        "favorited_at": 1,
                        "title": "$content.title",
                        "publish_date": {"$ifNull": ["$content.publish_date", "$content.publish_time"]},  # 优先使用publish_date字段
                        "source": "$content.source",
                        "type": "$content.type",
                        "energy_type_tags": "$content.energy_type_tags",
                        "region_tags": "$content.region_tags",
                        "link": "$content.link"
                    }
                }
            ]
            
            cursor = self.favorites_collection.aggregate(pipeline)
            favorites = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                favorites.append(doc)
            
            return favorites
            
        except Exception as e:
            logger.error(f"获取用户收藏列表失败: {str(e)}")
            return []
    
    async def search_user_favorites(self, user_id: str, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        搜索用户收藏的文章
        """
        try:
            # 构建搜索条件
            search_conditions = []
            
            if query and query.strip():
                query = query.strip()
                # 构建文本搜索条件
                text_search = {
                    "$or": [
                        {"content.title": {"$regex": query, "$options": "i"}},  # 标题搜索
                        {"content.source": {"$regex": query, "$options": "i"}},  # 来源搜索
                        {"content.energy_type_tags": {"$regex": query, "$options": "i"}},  # 能源类型搜索
                        {"content.region_tags": {"$regex": query, "$options": "i"}},  # 地区搜索
                        {"content.business_field_tags": {"$regex": query, "$options": "i"}},  # 业务领域搜索
                    ]
                }
                search_conditions.append(text_search)
            
            # 聚合查询管道
            pipeline = [
                {"$match": {"user_id": user_id}},
                {
                    "$addFields": {
                        "content_object_id": {"$toObjectId": "$content_id"}
                    }
                },
                {
                    "$lookup": {
                        "from": "content",
                        "localField": "content_object_id",
                        "foreignField": "_id",
                        "as": "content"
                    }
                },
                {"$unwind": "$content"}
            ]
            
            # 添加搜索条件
            if search_conditions:
                pipeline.append({"$match": {"$and": search_conditions}})
            
            # 添加排序和限制
            pipeline.extend([
                {"$sort": {"favorited_at": -1}},
                {"$limit": limit},
                {
                    "$project": {
                        "content_id": 1,
                        "favorited_at": 1,
                        "title": "$content.title",
                        "publish_date": {"$ifNull": ["$content.publish_date", "$content.publish_time"]},
                        "source": "$content.source",
                        "type": "$content.type",
                        "energy_type_tags": "$content.energy_type_tags",
                        "region_tags": "$content.region_tags",
                        "business_field_tags": "$content.business_field_tags",
                        "link": "$content.link"
                    }
                }
            ])
            
            cursor = self.favorites_collection.aggregate(pipeline)
            favorites = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                favorites.append(doc)
            
            logger.info(f"用户 {user_id} 搜索收藏: '{query}', 结果数量: {len(favorites)}")
            return favorites
            
        except Exception as e:
            logger.error(f"搜索用户收藏失败: {str(e)}")
            return []
    
    async def get_user_favorites_count(self, user_id: str) -> int:
        """获取用户收藏总数"""
        try:
            return await self.favorites_collection.count_documents({"user_id": user_id})
        except Exception as e:
            logger.error(f"获取收藏总数失败: {str(e)}")
            return 0
    
    async def is_favorited(self, user_id: str, content_id: str) -> bool:
        """检查文章是否已收藏"""
        try:
            result = await self.favorites_collection.find_one({
                "user_id": user_id,
                "content_id": content_id
            })
            return result is not None
        except Exception as e:
            logger.error(f"检查收藏状态失败: {str(e)}")
            return False
    
    async def _learn_tags_from_content(self, user_id: str, content_doc: Dict) -> Dict[str, List[str]]:
        """
        从收藏的文章中学习标签
        """
        learned_tags = {
            "energy_types": [],
            "regions": [],
            "business_fields": []
        }
        
        try:
            # 获取当前用户标签
            current_user_tags = await self.user_service.get_user_tags(user_id)
            if not current_user_tags:
                return learned_tags
            
            # 当前用户已有的标签名称集合
            existing_tag_names = {tag.name for tag in current_user_tags.tags}
            
            # 学习能源类型标签
            energy_tags = content_doc.get("energy_type_tags", [])
            for energy_tag in energy_tags:
                if energy_tag and energy_tag not in existing_tag_names:
                    # 添加新的能源类型标签，权重设为2.0（收藏行为权重）
                    await self.user_service.add_user_tag(
                        user_id=user_id,
                        tag_name=energy_tag,
                        category=TagCategory.ENERGY_TYPE,
                        weight=2.0,
                        source=TagSource.AI_GENERATED  # 标记为AI生成（基于收藏行为）
                    )
                    learned_tags["energy_types"].append(energy_tag)
                    logger.info(f"用户 {user_id} 从收藏中学习能源标签: {energy_tag}")
            
            # 学习地域标签（城市和省份优先级较高）
            region_tags = content_doc.get("region_tags", [])
            for region_tag in region_tags:
                if region_tag and region_tag not in existing_tag_names and region_tag != "全国":
                    # 判断标签类型并设置相应权重
                    category, weight = self._determine_region_category_and_weight(region_tag)
                    
                    await self.user_service.add_user_tag(
                        user_id=user_id,
                        tag_name=region_tag,
                        category=category,
                        weight=weight,
                        source=TagSource.AI_GENERATED
                    )
                    learned_tags["regions"].append(region_tag)
                    logger.info(f"用户 {user_id} 从收藏中学习地域标签: {region_tag} ({category.value})")
            
            # 学习业务领域标签（权重较低）
            business_tags = content_doc.get("business_field_tags", [])
            for business_tag in business_tags[:2]:  # 只学习前2个，避免标签过多
                if business_tag and business_tag not in existing_tag_names:
                    await self.user_service.add_user_tag(
                        user_id=user_id,
                        tag_name=business_tag,
                        category=TagCategory.BUSINESS_FIELD,
                        weight=1.0,  # 业务标签权重较低
                        source=TagSource.AI_GENERATED
                    )
                    learned_tags["business_fields"].append(business_tag)
                    logger.info(f"用户 {user_id} 从收藏中学习业务标签: {business_tag}")
            
        except Exception as e:
            logger.error(f"学习标签失败: {str(e)}")
        
        return learned_tags
    
    def _determine_region_category_and_weight(self, region_tag: str) -> tuple:
        """
        根据地域标签确定分类和权重
        """
        # 城市标签（高权重）
        major_cities = ["北京", "上海", "广州", "深圳", "天津", "重庆", "杭州", "南京", "苏州", "武汉", "成都", "西安"]
        if region_tag in major_cities:
            return TagCategory.CITY, 3.0
        
        # 省份标签（中等权重）
        provinces = ["北京市", "上海市", "天津市", "重庆市", "河北省", "山西省", "辽宁省", "吉林省", "黑龙江省",
                   "江苏省", "浙江省", "安徽省", "福建省", "江西省", "山东省", "河南省", "湖北省", "湖南省",
                   "广东省", "海南省", "四川省", "贵州省", "云南省", "陕西省", "甘肃省", "青海省", "台湾省",
                   "内蒙古自治区", "广西壮族自治区", "西藏自治区", "宁夏回族自治区", "新疆维吾尔自治区", "香港特别行政区", "澳门特别行政区"]
        if region_tag in provinces or any(prov in region_tag for prov in ["省", "市", "自治区", "特别行政区"]):
            return TagCategory.PROVINCE, 2.0
        
        # 地区标签（较低权重）
        return TagCategory.REGION, 1.0
    
    async def get_user_behavior_stats(self, user_id: str) -> UserBehaviorStats:
        """
        获取用户行为统计
        """
        try:
            # 统计收藏总数
            total_favorites = await self.get_user_favorites_count(user_id)
            
            # 统计能源类型兴趣分布
            energy_pipeline = [
                {"$match": {"user_id": user_id}},
                {"$unwind": "$energy_type_tags"},
                {"$group": {"_id": "$energy_type_tags", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            energy_interests = {}
            async for doc in self.favorites_collection.aggregate(energy_pipeline):
                energy_interests[doc["_id"]] = doc["count"]
            
            # 统计地域兴趣分布
            region_pipeline = [
                {"$match": {"user_id": user_id}},
                {"$unwind": "$region_tags"},
                {"$group": {"_id": "$region_tags", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            region_interests = {}
            async for doc in self.favorites_collection.aggregate(region_pipeline):
                region_interests[doc["_id"]] = doc["count"]
            
            # 获取最后活动时间
            last_favorite = await self.favorites_collection.find_one(
                {"user_id": user_id},
                sort=[("favorited_at", -1)]
            )
            last_activity = last_favorite["favorited_at"] if last_favorite else None
            
            return UserBehaviorStats(
                user_id=user_id,
                total_favorites=total_favorites,
                energy_type_interests=energy_interests,
                region_interests=region_interests,
                last_activity=last_activity
            )
            
        except Exception as e:
            logger.error(f"获取用户行为统计失败: {str(e)}")
            return UserBehaviorStats(user_id=user_id) 