from typing import List, Dict, Any
from pymongo.database import Database
from datetime import datetime, timedelta
from app.models.user import UserTags, UserTag
from app.models.content import Content
from app.services.user_service import UserService
from app.services.content_service import ContentService

class RecommendationService:
    def __init__(self, database: Database):
        self.db = database
        self.user_service = UserService(database)
        self.content_service = ContentService(database)
        self.user_behavior_collection = self.db.user_behavior

    async def get_user_recommendations(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Content]:
        """获取用户个性化推荐内容"""
        try:
            # 获取用户标签
            user_tags = await self.user_service.get_user_tags(user_id)
            
            if not user_tags or not user_tags.tags:
                # 如果用户没有标签，尝试确保用户有标签
                try:
                    user_tags = await self.user_service.ensure_user_has_tags(user_id)
                except:
                    # 如果仍然无法获取标签，返回最新内容
                    print(f"用户 {user_id} 无法获取标签，返回最新内容")
                    return await self.content_service.get_content_list(skip=skip, limit=limit)
            
            print(f"🎯 推荐服务为用户 {user_id} 找到 {len(user_tags.tags)} 个标签")
            
            # 基于用户行为调整标签权重
            adjusted_tags = await self.adjust_tag_weights_by_behavior(user_id, user_tags.tags)
            
            # 提取用户所有标签名称
            tag_names = [tag.name for tag in adjusted_tags]
            print(f"📋 推荐服务使用标签: {tag_names}")
            
            # 根据用户标签获取推荐内容
            recommended_content = await self.content_service.get_content_by_user_tags(
                user_tags=tag_names,
                skip=skip,
                limit=limit
            )
            
            print(f"📊 根据标签找到 {len(recommended_content)} 条匹配内容")
            
            # 计算相关性分数（使用优化的权重分级系统）
            for content in recommended_content:
                content.relevance_score = await self.calculate_content_relevance_score_v2(
                    UserTags(user_id=user_id, tags=adjusted_tags),
                    content
                )
            
            # 按相关性排序
            recommended_content.sort(key=lambda x: x.relevance_score or 0, reverse=True)
            
            return recommended_content
        except Exception as e:
            print(f"❌ 推荐服务错误: {str(e)}")
            raise Exception(f"Failed to get user recommendations: {str(e)}")

    async def record_user_behavior(
        self,
        user_id: str,
        action: str,
        content_id: str,
        duration: int = None
    ) -> None:
        """记录用户行为"""
        try:
            behavior_data = {
                "user_id": user_id,
                "action": action,
                "content_id": content_id,
                "timestamp": datetime.utcnow(),
                "duration": duration
            }
            
            await self.user_behavior_collection.insert_one(behavior_data)
            
            # 如果是查看行为，更新内容的浏览次数
            if action == 'view':
                await self.content_service.increment_view_count(content_id)
                
        except Exception as e:
            raise Exception(f"Failed to record user behavior: {str(e)}")

    async def adjust_tag_weights_by_behavior(
        self,
        user_id: str,
        user_tags: List[UserTag]
    ) -> List[UserTag]:
        """根据用户行为调整标签权重"""
        try:
            # 获取最近30天的用户行为
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            behaviors = await self.user_behavior_collection.find({
                "user_id": user_id,
                "timestamp": {"$gte": thirty_days_ago}
            }).to_list(length=None)
            
            if not behaviors:
                return user_tags
            
            # 统计每个标签的行为次数
            tag_behavior_counts = {}
            
            for behavior in behaviors:
                content = await self.content_service.get_content_by_id(behavior["content_id"])
                if not content:
                    continue
                    
                # 收集内容的所有标签
                content_tags = (
                    content.basic_info_tags +
                    content.region_tags +
                    content.energy_type_tags +
                    content.business_field_tags +
                    content.beneficiary_tags +
                    content.policy_measure_tags +
                    content.importance_tags
                )
                
                # 为每个标签增加行为计数
                for tag_name in content_tags:
                    if tag_name not in tag_behavior_counts:
                        tag_behavior_counts[tag_name] = 0
                    
                    # 不同行为的权重不同
                    weight_multiplier = {
                        'view': 1.0,
                        'click': 1.5,
                        'like': 2.0,
                        'share': 3.0
                    }.get(behavior["action"], 1.0)
                    
                    tag_behavior_counts[tag_name] += weight_multiplier
            
            # 调整用户标签权重
            adjusted_tags = []
            for tag in user_tags:
                new_weight = tag.weight
                
                # 根据行为频次调整权重
                if tag.name in tag_behavior_counts:
                    behavior_count = tag_behavior_counts[tag.name]
                    # 行为越多，权重增加越多（但有上限）
                    weight_boost = min(behavior_count * 0.1, 2.0)
                    new_weight = min(tag.weight + weight_boost, 10.0)
                
                adjusted_tags.append(UserTag(
                    category=tag.category,
                    name=tag.name,
                    weight=new_weight,
                    source=tag.source,
                    created_at=tag.created_at
                ))
            
            return adjusted_tags
            
        except Exception as e:
            raise Exception(f"Failed to adjust tag weights: {str(e)}")

    async def get_user_behavior_insights(self, user_id: str) -> Dict[str, Any]:
        """获取用户行为洞察"""
        try:
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            # 获取最近7天的行为数据
            recent_behaviors = await self.user_behavior_collection.find({
                "user_id": user_id,
                "timestamp": {"$gte": seven_days_ago}
            }).to_list(length=None)
            
            # 统计各类行为
            behavior_stats = {
                'view': 0,
                'click': 0,
                'like': 0,
                'share': 0
            }
            
            total_reading_time = 0
            content_types = {}
            
            for behavior in recent_behaviors:
                action = behavior.get('action', 'view')
                if action in behavior_stats:
                    behavior_stats[action] += 1
                
                if behavior.get('duration'):
                    total_reading_time += behavior['duration']
                
                # 统计浏览的内容类型
                content = await self.content_service.get_content_by_id(behavior["content_id"])
                if content:
                    content_type = content.type
                    content_types[content_type] = content_types.get(content_type, 0) + 1
            
            # 计算活跃度评分
            activity_score = (
                behavior_stats['view'] * 1 +
                behavior_stats['click'] * 2 +
                behavior_stats['like'] * 3 +
                behavior_stats['share'] * 4
            )
            
            return {
                'behavior_stats': behavior_stats,
                'total_reading_time': total_reading_time,
                'average_reading_time': total_reading_time / max(behavior_stats['view'], 1),
                'preferred_content_types': content_types,
                'activity_score': activity_score,
                'engagement_level': self._calculate_engagement_level(activity_score)
            }
            
        except Exception as e:
            raise Exception(f"Failed to get user insights: {str(e)}")

    def _calculate_engagement_level(self, activity_score: int) -> str:
        """计算用户参与度等级"""
        if activity_score >= 100:
            return 'high'
        elif activity_score >= 50:
            return 'medium'
        elif activity_score >= 20:
            return 'low'
        else:
            return 'minimal'

    async def calculate_content_relevance_score_v2(
        self,
        user_tags: UserTags,
        content: Content
    ) -> float:
        """计算内容与用户标签的相关性分数 - v2版本，使用新的权重分级系统"""
        try:
            if not user_tags.tags:
                return 0.0
            
            total_score = 0.0
            matched_tags = 0
            tag_dict = {tag.name: tag.weight for tag in user_tags.tags}
            
            # 🎯 新的标签权重配置（v2版本）
            TAG_WEIGHT_CONFIG_V2 = {
                "region_tags": 3.0,      # 地域标签权重最高
                "energy_type_tags": 2.5, # 能源类型权重第二
                "basic_info_tags": 1.0,  # 基础信息标签保持原权重
                "business_field_tags": 0.7,  # 业务标签权重降低
                "policy_measure_tags": 0.7,  # 政策标签权重降低
                "importance_tags": 0.5,      # 重要性标签权重最低
                "beneficiary_tags": 0.5      # 受益主体权重最低
            }
            
            # 按标签类别分别计算权重分数
            tag_categories = [
                ("basic_info_tags", "basic_info_tags"),
                ("region_tags", "region_tags"),
                ("energy_type_tags", "energy_type_tags"),
                ("business_field_tags", "business_field_tags"),
                ("policy_measure_tags", "policy_measure_tags"),
                ("importance_tags", "importance_tags"),
                ("beneficiary_tags", "beneficiary_tags")
            ]
            
            for content_field, category_key in tag_categories:
                content_tags = getattr(content, content_field, [])
                category_multiplier = TAG_WEIGHT_CONFIG_V2.get(category_key, 1.0)
                
                for content_tag in content_tags:
                    if content_tag in tag_dict:
                        # 基础分数 = 用户标签权重 × 类别增强系数
                        base_score = tag_dict[content_tag] * category_multiplier
                        total_score += base_score
                        matched_tags += 1
            
            if matched_tags == 0:
                return 0.0
            
            # 计算时效性因子
            time_factor = self._calculate_time_factor(content.publish_time)
            
            # 计算标签匹配度（给予地域和能源类型更高权重）
            region_match = len([tag for tag in content.region_tags if tag in tag_dict])
            energy_match = len([tag for tag in content.energy_type_tags if tag in tag_dict])
            
            # 如果地域或能源类型匹配，给予额外加分
            bonus_factor = 1.0
            if region_match > 0:
                bonus_factor += 0.4  # 地域匹配额外40%加分（提升）
            if energy_match > 0:
                bonus_factor += 0.3  # 能源类型匹配额外30%加分（提升）
            
            # 计算总标签数（用于匹配度计算）
            all_content_tags = (
                content.basic_info_tags +
                content.region_tags +
                content.energy_type_tags +
                content.business_field_tags +
                getattr(content, 'beneficiary_tags', []) +
                getattr(content, 'policy_measure_tags', []) +
                content.importance_tags
            )
            
            # 基础匹配度
            tag_match_factor = matched_tags / max(len(all_content_tags), 1)
            
            # 最终评分 = (标签权重分数 × 时效性因子 × 匹配度因子 × 奖励因子) / 标准化因子
            final_score = (total_score * time_factor * tag_match_factor * bonus_factor) / 20.0
            
            return min(final_score, 1.0)
        except Exception as e:
            raise Exception(f"Failed to calculate relevance score v2: {str(e)}")

    def _calculate_time_factor(self, publish_time: str) -> float:
        """计算时效性因子"""
        try:
            publish_date = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
            now = datetime.utcnow().replace(tzinfo=publish_date.tzinfo)
            days_diff = (now - publish_date).days
            
            # 7天内的内容给予满分
            if days_diff <= 7:
                return 1.0
            # 30天内的内容逐渐降权
            elif days_diff <= 30:
                return 1.0 - (days_diff - 7) * 0.02  # 每天降权2%
            # 超过30天的内容给予基础分
            else:
                return 0.5
        except:
            return 0.8  # 默认值

    async def get_trending_content(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> List[Content]:
        """获取热门内容"""
        try:
            # 获取最新的重要内容
            pipeline = [
                {
                    "$match": {
                        "$or": [
                            {"importance_tags": {"$in": ["国家级", "权威发布", "重要政策"]}},
                            {"basic_info_tags": {"$in": ["政策法规", "行业资讯"]}}
                        ]
                    }
                },
                {"$sort": {"publish_time": -1}},
                {"$skip": skip},
                {"$limit": limit}
            ]
            
            contents = []
            async for document in self.content_service.collection.aggregate(pipeline):
                document['id'] = str(document['_id'])
                contents.append(Content(**document))
            
            return contents
        except Exception as e:
            raise Exception(f"Failed to get trending content: {str(e)}")

    async def get_similar_content(
        self,
        content_id: str,
        limit: int = 5
    ) -> List[Content]:
        """获取相似内容"""
        try:
            # 获取原始内容
            original_content = await self.content_service.get_content_by_id(content_id)
            if not original_content:
                return []
            
            # 收集原始内容的所有标签
            all_tags = (
                original_content.basic_info_tags +
                original_content.region_tags +
                original_content.energy_type_tags +
                original_content.business_field_tags +
                original_content.beneficiary_tags +
                original_content.policy_measure_tags +
                original_content.importance_tags
            )
            
            if not all_tags:
                return []
            
            # 查找具有相似标签的内容
            similar_content = await self.content_service.get_content_by_user_tags(
                user_tags=all_tags,
                skip=0,
                limit=limit + 1  # 多取一个，因为可能包含原始内容
            )
            
            # 过滤掉原始内容
            return [c for c in similar_content if c.id != content_id][:limit]
        except Exception as e:
            raise Exception(f"Failed to get similar content: {str(e)}")

    async def get_tiered_recommendations(
        self,
        user_id: str,
        primary_limit: int = 6,
        secondary_limit: int = 4
    ) -> dict:
        """获取分级推荐内容：精准推荐（一级权重）+ 扩展推荐（二级权重）"""
        try:
            # 获取用户标签
            user_tags = await self.user_service.get_user_tags(user_id)
            
            if not user_tags or not user_tags.tags:
                try:
                    user_tags = await self.user_service.ensure_user_has_tags(user_id)
                except:
                    return {
                        "primary_recommendations": [],
                        "secondary_recommendations": [],
                        "total_primary": 0,
                        "total_secondary": 0
                    }
            
            print(f"🎯 分级推荐为用户 {user_id} 处理 {len(user_tags.tags)} 个标签")
            
            # 分离一级和二级权重标签
            primary_tags = []  # 地域、能源类型
            secondary_tags = []  # 其他标签
            
            for tag in user_tags.tags:
                if tag.category in ["region", "energy_type"]:
                    primary_tags.append(tag.name)
                else:
                    secondary_tags.append(tag.name)
            
            print(f"📍 一级权重标签（地域+能源）: {primary_tags}")
            print(f"📋 二级权重标签（业务+政策等）: {secondary_tags}")
            
            # 获取精准推荐（基于一级权重标签）
            primary_recommendations = []
            if primary_tags:
                primary_recommendations = await self.content_service.get_content_by_user_tags(
                    user_tags=primary_tags,
                    skip=0,
                    limit=primary_limit
                )
                
                # 计算精准推荐的相关性分数
                for content in primary_recommendations:
                    content.relevance_score = await self.calculate_primary_relevance_score(
                        primary_tags, content
                    )
                
                primary_recommendations.sort(key=lambda x: x.relevance_score or 0, reverse=True)
            
            # 获取扩展推荐（基于二级权重标签，排除已推荐的内容）
            secondary_recommendations = []
            if secondary_tags:
                # 获取已推荐的内容ID，避免重复
                recommended_ids = {rec.id for rec in primary_recommendations}
                
                all_secondary = await self.content_service.get_content_by_user_tags(
                    user_tags=secondary_tags,
                    skip=0,
                    limit=secondary_limit + len(recommended_ids)  # 多取一些以备筛选
                )
                
                # 筛选掉已在精准推荐中的内容
                secondary_recommendations = [
                    content for content in all_secondary 
                    if content.id not in recommended_ids
                ][:secondary_limit]
                
                # 计算扩展推荐的相关性分数
                for content in secondary_recommendations:
                    content.relevance_score = await self.calculate_secondary_relevance_score(
                        secondary_tags, content
                    )
                
                secondary_recommendations.sort(key=lambda x: x.relevance_score or 0, reverse=True)
            
            print(f"✅ 分级推荐完成: 精准{len(primary_recommendations)}篇，扩展{len(secondary_recommendations)}篇")
            
            return {
                "primary_recommendations": primary_recommendations,
                "secondary_recommendations": secondary_recommendations,
                "total_primary": len(primary_recommendations),
                "total_secondary": len(secondary_recommendations),
                "primary_tags_used": primary_tags,
                "secondary_tags_used": secondary_tags
            }
            
        except Exception as e:
            print(f"❌ 分级推荐服务错误: {str(e)}")
            raise Exception(f"Failed to get tiered recommendations: {str(e)}")

    async def calculate_primary_relevance_score(
        self,
        primary_tags: List[str],
        content: Content
    ) -> float:
        """计算精准推荐的相关性分数（仅基于一级权重标签）"""
        try:
            if not primary_tags:
                return 0.0
            
            total_score = 0.0
            matched_tags = 0
            
            # 地域标签匹配（权重×3.0）
            region_matches = len([tag for tag in content.region_tags if tag in primary_tags])
            if region_matches > 0:
                total_score += region_matches * 3.0
                matched_tags += region_matches
            
            # 能源类型标签匹配（权重×2.5）
            energy_matches = len([tag for tag in content.energy_type_tags if tag in primary_tags])
            if energy_matches > 0:
                total_score += energy_matches * 2.5
                matched_tags += energy_matches
            
            if matched_tags == 0:
                return 0.0
            
            # 时效性因子
            time_factor = self._calculate_time_factor(content.publish_time)
            
            # 特殊奖励：地域+能源类型双重匹配
            bonus_factor = 1.0
            if region_matches > 0 and energy_matches > 0:
                bonus_factor = 1.5  # 双重匹配50%奖励
            
            # 精准推荐分数计算
            final_score = (total_score * time_factor * bonus_factor) / 10.0
            
            return min(final_score, 1.0)
        except Exception as e:
            return 0.0

    async def calculate_secondary_relevance_score(
        self,
        secondary_tags: List[str],
        content: Content
    ) -> float:
        """计算扩展推荐的相关性分数（基于二级权重标签）"""
        try:
            if not secondary_tags:
                return 0.0
            
            total_score = 0.0
            matched_tags = 0
            
            # 二级权重标签匹配计算
            tag_categories = [
                ("basic_info_tags", 1.0),
                ("business_field_tags", 0.7),
                ("policy_measure_tags", 0.7),
                ("importance_tags", 0.5),
                ("beneficiary_tags", 0.5)
            ]
            
            for content_field, weight in tag_categories:
                content_tags = getattr(content, content_field, [])
                matches = len([tag for tag in content_tags if tag in secondary_tags])
                if matches > 0:
                    total_score += matches * weight
                    matched_tags += matches
            
            if matched_tags == 0:
                return 0.0
            
            # 时效性因子
            time_factor = self._calculate_time_factor(content.publish_time)
            
            # 扩展推荐分数计算（相对保守，避免干扰）
            final_score = (total_score * time_factor) / 8.0
            
            return min(final_score, 0.8)  # 扩展推荐最高分数限制在0.8
        except Exception as e:
            return 0.0 