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
        """计算内容与用户的相关性分数V2 - 标签权重优先，时间调节"""
        
        if not user_tags or not user_tags.tags:
            return 0.0
        
        # 收集内容的所有标签
        content_all_tags = self._get_all_content_tags(content)
        
        if not content_all_tags:
            return 0.0
        
        # 🔥 权重类别优先级配置
        WEIGHT_MULTIPLIERS = {
            "region": 3.0,      # 地域标签 - 最高优先级
            "city": 3.0,        # 城市标签 - 最高优先级  
            "province": 2.0,    # 省份标签
            "energy_type": 2.5, # 能源类型标签 - 第二优先级
            "basic_info": 1.0,  # 基础信息标签
            "business_field": 0.8,  # 业务领域标签
            "policy_measure": 0.8,  # 政策措施标签
            "beneficiary": 0.6,     # 受益主体标签
            "importance": 0.6       # 重要性标签
        }
        
        # 计算标签权重分数
        total_score = 0.0
        matched_tags = 0
        highest_tag_weight = 0.0  # 🔥 记录最高标签权重
        energy_type_matched = False  # 🔥 记录是否匹配能源类型
        energy_type_score = 0.0     # 🔥 记录能源类型得分
        
        for user_tag in user_tags.tags:
            tag_name = user_tag.name
            tag_category = user_tag.category
            tag_weight = getattr(user_tag, 'weight', 1.0)
            
            # 检查标签是否在内容中
            if tag_name in content_all_tags:
                matched_tags += 1
                
                # 获取权重乘法器
                multiplier = WEIGHT_MULTIPLIERS.get(tag_category, 1.0)
                
                # 🔥 计算最终得分：用户标签权重 × 权重乘法器
                tag_score = tag_weight * multiplier
                
                # 记录最高权重标签
                if tag_weight > highest_tag_weight:
                    highest_tag_weight = tag_weight
                
                # 🎯 记录能源类型匹配
                if tag_category == "energy_type":
                    energy_type_matched = True
                    energy_type_score = tag_score
                    print(f"🔍 能源标签权重计算: {tag_name} = {tag_weight} × {multiplier} = {tag_score}")
                
                total_score += tag_score
        
        # 🎯 精准标签匹配奖励系统
        if energy_type_matched and highest_tag_weight >= 4.0:
            # 高权重能源类型标签额外奖励
            precision_bonus = energy_type_score * 0.8  # 🔥 提升到80%精准匹配奖励
            total_score += precision_bonus
            print(f"🎯 精准能源标签奖励: +{precision_bonus:.2f} (总分: {total_score:.2f})")
            
            # 🎯 能源类型优先权：如果用户有高权重能源标签且内容精准匹配，额外奖励
            if highest_tag_weight >= 5.0:
                super_precision_bonus = energy_type_score * 0.3  # 30%超级精准奖励
                total_score += super_precision_bonus
                print(f"🔥 超级精准能源标签奖励: +{super_precision_bonus:.2f} (总分: {total_score:.2f})")
        
        # 🎯 权重优先逻辑：标签权重分层 + 时间调节
        if highest_tag_weight >= 4.0:
            # 高权重标签（≥4.0）：标签权重为主，时间为辅
            time_factor = self._calculate_time_factor_light(content.publish_time) if hasattr(content, 'publish_time') and content.publish_time else 1.0
            final_score = total_score + (time_factor - 1.0) * 2.0  # 时间只作为微调因子
        elif highest_tag_weight >= 2.0:
            # 中权重标签（2.0-4.0）：平衡权重和时间
            time_factor = self._calculate_time_factor(content.publish_time) if hasattr(content, 'publish_time') and content.publish_time else 1.0
            final_score = total_score * (0.8 + 0.2 * time_factor)  # 权重80%，时间20%
        else:
            # 低权重标签（<2.0）：时间权重相对较高
            time_factor = self._calculate_time_factor(content.publish_time) if hasattr(content, 'publish_time') and content.publish_time else 1.0
            final_score = total_score * time_factor  # 传统的时间权重
        
        return final_score

    def _calculate_time_factor_light(self, publish_time: str) -> float:
        """计算轻量时效性因子（用于高权重标签的微调）"""
        try:
            publish_date = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
            now = datetime.utcnow().replace(tzinfo=publish_date.tzinfo)
            days_diff = (now - publish_date).days
            
            # 高权重标签的时间因子范围缩小：0.9-1.1
            if days_diff <= 3:
                return 1.1  # 3天内微调加分
            elif days_diff <= 7:
                return 1.0  # 一周内标准分
            elif days_diff <= 30:
                return 0.95  # 一月内轻微减分
            else:
                return 0.9   # 超过一月小幅减分
        except:
            return 1.0  # 默认值

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
                {"$sort": {"publish_date": -1}},
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

    async def get_smart_recommendations(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Content]:
        """
        🔥 智能推荐算法：精准权重匹配优先 + 时间排序
        
        算法逻辑：
        1. 按标签权重精准度分层
        2. 每层内部按时间排序
        3. 高权重精准匹配优先显示
        4. 真正实现千人千面推荐
        
        Args:
            user_id: 用户ID
            skip: 跳过数量
            limit: 返回数量限制
            
        Returns:
            List[Content]: 智能推荐的内容列表
        """
        try:
            print(f"🧠 开始智能推荐 - 用户: {user_id}")
            
            # 获取用户标签
            user_tags = await self.user_service.get_user_tags(user_id)
            
            if not user_tags or not user_tags.tags:
                try:
                    user_tags = await self.user_service.ensure_user_has_tags(user_id)
                except:
                    print(f"❌ 用户 {user_id} 无标签，返回最新内容")
                    return await self.content_service.get_content_list(skip=skip, limit=limit)
            
            print(f"🏷️ 用户标签数量: {len(user_tags.tags)}")
            
            # 根据用户行为调整标签权重
            adjusted_tags = await self.adjust_tag_weights_by_behavior(user_id, user_tags.tags)
            
            # 按标签权重排序，权重高的优先
            adjusted_tags.sort(key=lambda x: x.weight, reverse=True)
            
            # 🔥 分层推荐策略
            recommendations = []
            used_content_ids = set()
            
            print(f"🎯 开始分层推荐，初始used_content_ids: {len(used_content_ids)}")
            
            # 第一层：最高权重标签精准匹配（权重 >= 4.0）
            high_weight_tags = [tag for tag in adjusted_tags if tag.weight >= 4.0]
            if high_weight_tags:
                print(f"🔥 第一层：高权重标签 ({len(high_weight_tags)}个)")
                for tag in high_weight_tags:
                    print(f"   🏷️ {tag.name} (权重: {tag.weight})")
                
                print(f"🔍 第一层前used_content_ids: {used_content_ids}")
                first_tier = await self._get_precise_content_by_tags(
                    high_weight_tags,
                    used_content_ids,
                    max_per_tag=3  # 每个高权重标签最多3篇
                )
                recommendations.extend(first_tier)
                print(f"🔍 第一层后used_content_ids: {used_content_ids}")
                print(f"   ✅ 第一层推荐: {len(first_tier)}篇")
            
            # 第二层：中等权重标签匹配（权重 2.0-4.0）
            if len(recommendations) < limit:
                medium_weight_tags = [tag for tag in adjusted_tags if 2.0 <= tag.weight < 4.0]
                if medium_weight_tags:
                    print(f"🟡 第二层：中权重标签 ({len(medium_weight_tags)}个)")
                    
                    print(f"🔍 第二层前used_content_ids: {used_content_ids}")
                    second_tier = await self._get_precise_content_by_tags(
                        medium_weight_tags,
                        used_content_ids,
                        max_per_tag=2  # 每个中权重标签最多2篇
                    )
                    recommendations.extend(second_tier)
                    print(f"🔍 第二层后used_content_ids: {used_content_ids}")
                    print(f"   ✅ 第二层推荐: {len(second_tier)}篇")
            
            # 第三层：低权重标签匹配（权重 < 2.0）
            if len(recommendations) < limit:
                low_weight_tags = [tag for tag in adjusted_tags if tag.weight < 2.0]
                if low_weight_tags:
                    print(f"🔵 第三层：低权重标签 ({len(low_weight_tags)}个)")
                    
                    print(f"🔍 第三层前used_content_ids: {used_content_ids}")
                    third_tier = await self._get_precise_content_by_tags(
                        low_weight_tags,
                        used_content_ids,
                        max_per_tag=1  # 每个低权重标签最多1篇
                    )
                    recommendations.extend(third_tier)
                    print(f"🔍 第三层后used_content_ids: {used_content_ids}")
                    print(f"   ✅ 第三层推荐: {len(third_tier)}篇")
            
            # 第四层：如果还不够，补充最新内容
            if len(recommendations) < limit:
                print(f"📰 第四层：补充最新内容")
                remaining_limit = limit - len(recommendations)
                latest_content = await self.content_service.get_content_list(
                    skip=0, 
                    limit=remaining_limit * 2  # 多取一些用于过滤
                )
                
                # 过滤掉已推荐的内容
                for content in latest_content:
                    if content.id not in used_content_ids and len(recommendations) < limit:
                        recommendations.append(content)
                        used_content_ids.add(content.id)
                
                print(f"   ✅ 第四层补充: {len(recommendations) - len(recommendations)}篇")
            
            # 应用分页
            if skip > 0:
                recommendations = recommendations[skip:]
            recommendations = recommendations[:limit]
            
            # 为每个推荐内容计算最终相关性分数
            for content in recommendations:
                content.relevance_score = await self.calculate_content_relevance_score_v2(
                    user_tags, content
                )
            
            # 🎯 关键修改：按相关性分数重新排序整个推荐列表
            recommendations.sort(key=lambda x: x.relevance_score or 0, reverse=True)
            
            print(f"🎯 智能推荐完成: 返回 {len(recommendations)} 篇内容")
            
            # 输出推荐内容的标签匹配情况
            for i, content in enumerate(recommendations[:5]):  # 只显示前5篇
                content_tags = self._get_all_content_tags(content)
                matched_user_tags = [tag.name for tag in adjusted_tags if tag.name in content_tags]
                print(f"   📄 {i+1}. {content.title[:50]}...")
                print(f"       🏷️ 匹配标签: {matched_user_tags}")
                print(f"       ⭐ 相关性: {content.relevance_score:.2f}")
                print(f"       📅 时间: {content.publish_time}")
            
            # 🎯 推荐服务层最终去重保障（在排序后）
            unique_recommendations = []
            seen_ids = set()
            
            print(f"🔍 推荐服务层最终去重: 输入 {len(recommendations)} 条推荐")
            
            for i, content in enumerate(recommendations):
                content_id = content.id
                if content_id not in seen_ids:
                    unique_recommendations.append(content)
                    seen_ids.add(content_id)
                    print(f"   ✅ 保留第{i+1}条: {content.title[:30]}... (ID: {content_id})")
                else:
                    print(f"   ❌ 推荐服务层去重：跳过第{i+1}条重复内容: {content.title[:30]}... (ID: {content_id})")
            
            final_recommendations = unique_recommendations
            print(f"🎯 推荐服务层去重完成: {len(recommendations)} → {len(final_recommendations)} 条唯一推荐")
            
            print(f"🎯 智能推荐完成: 返回 {len(final_recommendations)} 篇内容")
            
            # 输出推荐内容的标签匹配情况
            for i, content in enumerate(final_recommendations[:3]):  # 只显示前3篇
                content_tags = self._get_all_content_tags(content)
                matched_user_tags = [tag.name for tag in adjusted_tags if tag.name in content_tags]
                print(f"   📄 {i+1}. {content.title[:50]}...")
                print(f"       🏷️ 匹配标签: {matched_user_tags}")
                print(f"       ⭐ 相关性: {content.relevance_score:.2f}")
                print(f"       📅 时间: {content.publish_time}")
            
            return final_recommendations
            
        except Exception as e:
            print(f"❌ 智能推荐失败: {str(e)}")
            import traceback
            traceback.print_exc()
            # 回退到普通推荐
            return await self.get_user_recommendations(user_id, skip, limit)

    async def _get_precise_content_by_tags(
        self,
        tags: List[UserTag],
        used_content_ids: set,
        max_per_tag: int = 2
    ) -> List[Content]:
        """
        🎯 根据标签精准获取内容
        
        Args:
            tags: 用户标签列表
            used_content_ids: 已使用的内容ID集合
            max_per_tag: 每个标签最多返回多少篇内容
            
        Returns:
            List[Content]: 匹配的内容列表（按相关性分数排序）
        """
        content_list = []
        
        for tag in tags:
            print(f"🔍 搜索标签: {tag.name} (权重: {tag.weight})")
            
            # 根据标签搜索内容
            tag_content = await self.content_service.get_content_by_user_tags(
                user_tags=[tag.name],
                skip=0,
                limit=max_per_tag * 3  # 多取一些用于过滤
            )
            
            # 过滤已使用的内容
            filtered_content = []
            for content in tag_content:
                if content.id not in used_content_ids:
                    filtered_content.append(content)
                    used_content_ids.add(content.id)
            
            # 只取前 max_per_tag 篇
            selected_content = filtered_content[:max_per_tag]
            content_list.extend(selected_content)
            
            print(f"   ✅ 找到 {len(selected_content)} 篇内容 (总共 {len(tag_content)} 篇)")
            
            # 显示匹配的内容信息
            for content in selected_content:
                print(f"      📄 {content.title[:30]}... ({content.publish_time})")
        
        return content_list

    def _get_all_content_tags(self, content: Content) -> List[str]:
        """获取内容的所有标签"""
        all_tags = []
        
        # 收集所有标签字段
        tag_fields = [
            'basic_info_tags', 'region_tags', 'energy_type_tags',
            'business_field_tags', 'beneficiary_tags', 
            'policy_measure_tags', 'importance_tags'
        ]
        
        for field in tag_fields:
            if hasattr(content, field):
                field_tags = getattr(content, field, [])
                if field_tags:
                    all_tags.extend(field_tags)
        
        # 去重
        return list(set(all_tags))

    async def get_smart_recommendations_by_type(
        self,
        user_id: str,
        content_types: List[str],
        basic_info_tags: List[str],
        skip: int = 0,
        limit: int = 10
    ) -> List[Content]:
        """
        🎯 按内容类型的智能推荐：权重优先 + 时间调节
        
        Args:
            user_id: 用户ID
            content_types: 内容类型列表 ['news', 'policy', 'announcement', 'price']
            basic_info_tags: 基础信息标签列表 ['行业资讯', '政策法规', '交易公告', '调价公告'] 
            skip: 跳过数量
            limit: 返回数量限制
            
        Returns:
            List[Content]: 按类型筛选的智能推荐内容
        """
        try:
            print(f"🎯 按类型智能推荐 - 用户: {user_id}, 类型: {content_types}, 标签: {basic_info_tags}")
            
            # 获取用户标签
            user_tags = await self.user_service.get_user_tags(user_id)
            
            if not user_tags or not user_tags.tags:
                try:
                    user_tags = await self.user_service.ensure_user_has_tags(user_id)
                except:
                    print(f"❌ 用户 {user_id} 无标签，返回空内容")
                    return []
            
            print(f"🏷️ 用户标签数量: {len(user_tags.tags)}")
            
            # 根据用户行为调整标签权重
            adjusted_tags = await self.adjust_tag_weights_by_behavior(user_id, user_tags.tags)
            
            # 按标签权重排序，权重高的优先
            adjusted_tags.sort(key=lambda x: x.weight, reverse=True)
            
            # 🔥 构建类型筛选查询条件
            type_filter = {
                "$or": [
                    {"type": {"$in": content_types}},
                    {"basic_info_tags": {"$in": basic_info_tags}}
                ]
            }
            
            print(f"🔍 类型筛选条件: {type_filter}")
            
            # 🔥 分层推荐策略（仅在指定类型内）
            recommendations = []
            used_content_ids = set()
            
            print(f"🎯 开始分层推荐，初始used_content_ids: {len(used_content_ids)}")
            
            # 第一层：最高权重标签精准匹配（权重 >= 4.0）
            high_weight_tags = [tag for tag in adjusted_tags if tag.weight >= 4.0]
            if high_weight_tags:
                print(f"🔥 第一层：高权重标签 ({len(high_weight_tags)}个)")
                for tag in high_weight_tags:
                    print(f"   🏷️ {tag.name} (权重: {tag.weight})")
                
                print(f"🔍 第一层前used_content_ids: {used_content_ids}")
                first_tier = await self._get_precise_content_by_tags_and_type(
                    high_weight_tags,
                    used_content_ids,
                    type_filter,
                    max_per_tag=3
                )
                recommendations.extend(first_tier)
                print(f"🔍 第一层后used_content_ids: {used_content_ids}")
                print(f"   ✅ 第一层推荐: {len(first_tier)}篇")
            
            # 第二层：中等权重标签匹配（权重 2.0-4.0）
            if len(recommendations) < limit:
                medium_weight_tags = [tag for tag in adjusted_tags if 2.0 <= tag.weight < 4.0]
                if medium_weight_tags:
                    print(f"🟡 第二层：中权重标签 ({len(medium_weight_tags)}个)")
                    
                    print(f"🔍 第二层前used_content_ids: {used_content_ids}")
                    second_tier = await self._get_precise_content_by_tags_and_type(
                        medium_weight_tags,
                        used_content_ids,
                        type_filter,
                        max_per_tag=2
                    )
                    recommendations.extend(second_tier)
                    print(f"🔍 第二层后used_content_ids: {used_content_ids}")
                    print(f"   ✅ 第二层推荐: {len(second_tier)}篇")
            
            # 第三层：低权重标签匹配（权重 < 2.0）
            if len(recommendations) < limit:
                low_weight_tags = [tag for tag in adjusted_tags if tag.weight < 2.0]
                if low_weight_tags:
                    print(f"🔵 第三层：低权重标签 ({len(low_weight_tags)}个)")
                    
                    print(f"🔍 第三层前used_content_ids: {used_content_ids}")
                    third_tier = await self._get_precise_content_by_tags_and_type(
                        low_weight_tags,
                        used_content_ids,
                        type_filter,
                        max_per_tag=1
                    )
                    recommendations.extend(third_tier)
                    print(f"🔍 第三层后used_content_ids: {used_content_ids}")
                    print(f"   ✅ 第三层推荐: {len(third_tier)}篇")
            
            # 第四层：如果还不够，补充该类型的最新内容
            if len(recommendations) < limit:
                print(f"📰 第四层：补充该类型最新内容")
                remaining_limit = limit - len(recommendations)
                
                # 查询该类型的最新内容
                latest_content_cursor = self.content_service.collection.find(type_filter).sort("publish_time", -1)
                latest_content_docs = await latest_content_cursor.to_list(length=remaining_limit * 2)
                
                # 🔥 修复重复问题：检查used_content_ids
                added_count = 0
                for doc in latest_content_docs:
                    content_id = str(doc['_id'])
                    
                    # 确保内容不重复且数量不超限
                    if content_id not in used_content_ids and len(recommendations) < limit:
                        doc['id'] = content_id
                        content = Content(**doc)
                        recommendations.append(content)
                        used_content_ids.add(content_id)
                        added_count += 1
                        
                        print(f"      ✅ 补充内容: {content.title[:30]}... (ID: {content_id})")
                    else:
                        if content_id in used_content_ids:
                            print(f"      ⚠️ 内容已存在，跳过: {doc.get('title', 'Unknown')[:30]}... (ID: {content_id})")
                
                print(f"   ✅ 第四层补充: {added_count}篇新内容")
            
            # 应用分页
            if skip > 0:
                recommendations = recommendations[skip:]
            recommendations = recommendations[:limit]
            
            # 为每个推荐内容计算最终相关性分数
            for content in recommendations:
                content.relevance_score = await self.calculate_content_relevance_score_v2(
                    user_tags, content
                )
            
            # 🎯 关键：按相关性分数重新排序整个推荐列表
            recommendations.sort(key=lambda x: x.relevance_score or 0, reverse=True)
            
            # 🔥 推荐服务层最终去重保障（在排序后）
            unique_recommendations = []
            seen_ids = set()
            
            print(f"🔍 推荐服务层最终去重: 输入 {len(recommendations)} 条推荐")
            
            for i, content in enumerate(recommendations):
                content_id = content.id
                if content_id not in seen_ids:
                    unique_recommendations.append(content)
                    seen_ids.add(content_id)
                    print(f"   ✅ 保留第{i+1}条: {content.title[:30]}... (ID: {content_id})")
                else:
                    print(f"   ❌ 推荐服务层去重：跳过第{i+1}条重复内容: {content.title[:30]}... (ID: {content_id})")
            
            final_recommendations = unique_recommendations
            print(f"🎯 推荐服务层去重完成: {len(recommendations)} → {len(final_recommendations)} 条唯一推荐")
            
            print(f"🎯 按类型智能推荐完成: 返回 {len(final_recommendations)} 篇 {content_types} 类型内容")
            
            # 输出推荐内容的标签匹配情况
            for i, content in enumerate(final_recommendations[:3]):  # 只显示前3篇
                content_tags = self._get_all_content_tags(content)
                matched_user_tags = [tag.name for tag in adjusted_tags if tag.name in content_tags]
                print(f"   📄 {i+1}. {content.title[:50]}...")
                print(f"       🏷️ 匹配标签: {matched_user_tags}")
                print(f"       ⭐ 相关性: {content.relevance_score:.2f}")
                print(f"       📅 时间: {content.publish_time}")
                print(f"       🏷️ 类型: {content.type}")
            
            return final_recommendations
            
        except Exception as e:
            print(f"❌ 按类型智能推荐失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    async def _get_precise_content_by_tags_and_type(
        self,
        tags: List[UserTag],
        used_content_ids: set,
        type_filter: dict,
        max_per_tag: int = 2
    ) -> List[Content]:
        """
        🎯 根据标签和类型精准获取内容
        
        Args:
            tags: 用户标签列表
            used_content_ids: 已使用的内容ID集合
            type_filter: 类型筛选条件
            max_per_tag: 每个标签最多返回多少篇内容
            
        Returns:
            List[Content]: 匹配的内容列表
        """
        content_list = []
        
        for tag in tags:
            print(f"🔍 搜索标签: {tag.name} (权重: {tag.weight}) 在指定类型中")
            
            # 构建查询条件：标签匹配 + 类型筛选
            query = {
                "$and": [
                    type_filter,  # 类型筛选
                    {
                        "$or": [
                            {"basic_info_tags": tag.name},
                            {"region_tags": tag.name},
                            {"energy_type_tags": tag.name},
                            {"business_field_tags": tag.name},
                            {"beneficiary_tags": tag.name},
                            {"policy_measure_tags": tag.name},
                            {"importance_tags": tag.name}
                        ]
                    }
                ]
            }
            
            # 查询匹配的内容
            content_cursor = self.content_service.collection.find(query).sort("publish_time", -1)
            content_docs = await content_cursor.to_list(length=max_per_tag * 3)
            
            # 🔥 简化去重逻辑：只检查used_content_ids，确保内容不重复
            tag_content_count = 0  # 该标签已添加的内容数量
            
            for doc in content_docs:
                content_id = str(doc['_id'])
                
                # 🎯 关键修复：只检查used_content_ids，避免重复逻辑
                if content_id not in used_content_ids:
                    doc['id'] = content_id
                    content = Content(**doc)
                    content_list.append(content)
                    used_content_ids.add(content_id)
                    tag_content_count += 1
                    
                    print(f"      ✅ 添加内容: {content.title[:30]}... (ID: {content_id})")
                    
                    # 该标签达到最大数量限制，停止添加
                    if tag_content_count >= max_per_tag:
                        break
                else:
                    print(f"      ⚠️ 内容已存在，跳过: {doc.get('title', 'Unknown')[:30]}... (ID: {content_id})")
            
            print(f"   ✅ 标签 {tag.name} 找到 {tag_content_count} 篇新内容")
        
        print(f"🎯 按标签和类型搜索完成，总共找到 {len(content_list)} 篇内容")
        return content_list 