#!/usr/bin/env python3
"""
用户API路由模块
"""
import logging
from datetime import timedelta
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel

# 核心模块导入
from app.core.config import settings
from app.core.database import get_database
from app.core.security import create_access_token

# 模型导入
from app.models.user import UserCreate, UserLogin, UserProfile, UserTags, UserTagsResponse, TagUpdateRequest
from app.models.content import Content

# 服务导入
from app.services.user_service import UserService
from app.services.recommendation_service import RecommendationService
from app.services.content_service import ContentService

# 工具模块导入
from app.utils.region_mapper import RegionMapper
from app.utils.tag_processor import TagProcessor
from app.utils.energy_weight_system import EnergyWeightSystem

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class UserBehaviorRequest(BaseModel):
    action: str  # 'view', 'click', 'like', 'share'
    content_id: str
    duration: Optional[int] = None  # 浏览时长（秒）

class ContentListResponse(BaseModel):
    items: List[Content]
    total: int
    page: int
    page_size: int
    has_next: bool

class UserInsightsResponse(BaseModel):
    behavior_stats: Dict[str, int]
    total_reading_time: int
    average_reading_time: float
    preferred_content_types: Dict[str, int]
    activity_score: int
    engagement_level: str

class SupportedCitiesResponse(BaseModel):
    """支持的城市列表响应"""
    cities: List[str]
    regions: List[Dict[str, str]]
    total_cities: int

class UserRegionInfoResponse(BaseModel):
    """用户区域信息响应"""
    user_id: str
    city: Optional[str]
    city_code: Optional[str]
    province: Optional[str] 
    province_code: Optional[str]
    region: Optional[str]
    region_code: Optional[str]
    location_info: Optional[Dict[str, str]]

class DemoUser(BaseModel):
    """演示用户模型"""
    id: str
    demo_user_id: str
    username: str
    email: str
    description: str
    register_city: str

class DemoUsersResponse(BaseModel):
    """演示用户列表响应"""
    users: List[DemoUser]
    total: int

class TagsUpdateRequest(BaseModel):
    tags: List[dict]

class EnergySelectionRequest(BaseModel):
    energy_types: List[str]

@router.get("/supported-cities", response_model=SupportedCitiesResponse)
async def get_supported_cities():
    """获取支持的城市列表和区域信息"""
    try:
        cities = RegionMapper.get_all_cities()
        regions = RegionMapper.get_all_regions()
        
        return SupportedCitiesResponse(
            cities=sorted(cities),  # 按字母顺序排序
            regions=regions,
            total_cities=len(cities)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get supported cities: {str(e)}"
        )

@router.get("/cities-details")
async def get_cities_details():
    """获取所有城市的详细信息（包括省份和区域）"""
    try:
        cities = RegionMapper.get_all_cities()
        cities_details = []
        
        for city in cities:
            location_info = RegionMapper.get_full_location_info(city)
            cities_details.append({
                "city": city,
                "province": location_info.get("province", "未知省份"),
                "region": location_info.get("region", "未知地区"),
                "province_code": location_info.get("province_code", ""),
                "region_code": location_info.get("region_code", "")
            })
        
        return {
            "cities": sorted(cities_details, key=lambda x: x["city"]),
            "total": len(cities_details)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cities details: {str(e)}"
        )

@router.post("/register", response_model=UserProfile)
async def register_user(
    request: dict,
    db = Depends(get_database)
):
    """注册新用户（基于城市自动生成区域标签）"""
    try:
        user_service = UserService(db)
        
        # 🔥 提取能源类型
        energy_types = request.get("energy_types", [])
        
        # 从请求中提取用户基础信息
        user_data = UserCreate(
            email=request.get("email"),
            username=request.get("username"), 
            password=request.get("password"),
            register_city=request.get("register_city"),
            energy_types=energy_types  # 🔥 传递能源类型到UserCreate
        )
        
        user_db = await user_service.create_user(user_data, energy_types)
        
        # 获取用户可访问功能
        access_features = await user_service.get_access_features(user_db.role)
        
        return UserProfile(
            id=user_db.id,
            email=user_db.email,
            username=user_db.username,
            role=user_db.role,
            is_active=user_db.is_active,
            created_at=user_db.created_at,
            has_initial_tags=True,
            access_features=access_features,
            register_city=user_db.register_city,
            register_info=user_db.register_info  # 🔥 返回注册信息
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.get("/{user_id}/region-info", response_model=UserRegionInfoResponse)
async def get_user_region_info(
    user_id: str,
    db = Depends(get_database)
):
    """获取用户的区域信息（包括注册城市和对应区域）"""
    try:
        user_service = UserService(db)
        region_info = await user_service.get_user_region_info(user_id)
        
        return UserRegionInfoResponse(
            user_id=user_id,
            city=region_info["city"],
            city_code=region_info["city_code"],
            province=region_info["province"],
            province_code=region_info["province_code"],
            region=region_info["region"],
            region_code=region_info["region_code"],
            location_info=region_info["location_info"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user region info: {str(e)}"
        )

@router.post("/login")
async def login(user_login: UserLogin, db=Depends(get_database)):
    """用户登录"""
    logger.info(f"🔐 用户登录尝试 - email: {user_login.email}")
    
    try:
        user_service = UserService(db)
        
        # 验证用户凭证
        logger.info(f"🔍 验证用户凭证...")
        user = await user_service.authenticate_user(user_login.email, user_login.password)
        
        if not user:
            logger.warning(f"❌ 登录失败 - 用户名或密码错误: {user_login.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        logger.info(f"✅ 用户验证成功 - user_id: {user.id}, username: {user.username}")
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}, 
            expires_delta=access_token_expires
        )
        
        logger.info(f"🎫 访问令牌创建成功 - 有效期: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}分钟")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "register_city": user.register_city
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 登录过程错误: {str(e)}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/{user_id}/tags", response_model=UserTagsResponse)
async def get_user_tags(user_id: str, db=Depends(get_database)):
    """获取用户标签"""
    logger.info(f"🏷️ 获取用户标签 - user_id: {user_id}")
    
    try:
        user_service = UserService(db)
        
        logger.info(f"🔍 查询用户标签...")
        user_tags = await user_service.get_user_tags(user_id)
        
        if not user_tags:
            logger.warning(f"⚠️ 用户标签不存在，创建默认标签 - user_id: {user_id}")
            # 用户标签不存在，返回空标签
            user_tags = UserTags(user_id=user_id, tags=[])
        
        logger.info(f"✅ 用户标签获取成功 - 标签数量: {len(user_tags.tags)}")
        
        # 按标签类别统计
        tag_stats = {}
        for tag in user_tags.tags:
            category = tag.category
            if category not in tag_stats:
                tag_stats[category] = 0
            tag_stats[category] += 1
        
        logger.info(f"📊 标签统计: {tag_stats}")
        
        # 打印部分标签详情
        for i, tag in enumerate(user_tags.tags[:10]):  # 只打印前10个
            logger.info(f"🏷️ 标签{i+1}: {tag.category}:{tag.name} (权重:{tag.weight}, 来源:{tag.source})")
        
        return UserTagsResponse(
            data=user_tags,
            message="User tags retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ 获取用户标签错误: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user tags: {str(e)}"
        )

@router.put("/{user_id}/tags", response_model=UserTagsResponse)
async def update_user_tags(user_id: str, tag_request: TagUpdateRequest, db=Depends(get_database)):
    """更新用户标签"""
    logger.info(f"📝 更新用户标签 - user_id: {user_id}, 新标签数量: {len(tag_request.tags)}")
    
    try:
        user_service = UserService(db)
        
        # 打印新标签详情
        for i, tag in enumerate(tag_request.tags[:5]):  # 只打印前5个
            logger.info(f"🆕 新标签{i+1}: {tag.category}:{tag.name} (权重:{tag.weight})")
        
        logger.info(f"💾 保存用户标签...")
        updated_tags = await user_service.update_user_tags(user_id, tag_request.tags)
        
        if not updated_tags:
            logger.error(f"❌ 更新用户标签失败 - user_id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or failed to update tags"
            )
        
        logger.info(f"✅ 用户标签更新成功 - 最终标签数量: {len(updated_tags.tags)}")
        
        return UserTagsResponse(
            data=updated_tags,
            message="User tags updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 更新用户标签错误: {str(e)}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user tags: {str(e)}"
        )

@router.post("/{user_id}/tags/reset", response_model=UserTagsResponse)
async def reset_user_tags(user_id: str, db=Depends(get_database)):
    """🔥 重置用户标签到注册时的原始配置"""
    logger.info(f"🔄 重置用户标签 - user_id: {user_id}")
    
    try:
        user_service = UserService(db)
        
        logger.info(f"🔍 获取用户注册信息并重置标签...")
        reset_tags = await user_service.reset_user_tags_to_registration(user_id)
        
        if not reset_tags:
            logger.error(f"❌ 重置用户标签失败 - user_id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or failed to reset tags"
            )
        
        logger.info(f"✅ 用户标签重置成功 - 最终标签数量: {len(reset_tags.tags)}")
        
        # 统计重置后的标签分布
        tag_stats = {}
        for tag in reset_tags.tags:
            category = tag.category
            if category not in tag_stats:
                tag_stats[category] = 0
            tag_stats[category] += 1
        
        logger.info(f"📊 重置后标签分布: {tag_stats}")
        
        return UserTagsResponse(
            data=reset_tags,
            message="User tags reset to registration configuration successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 重置用户标签错误: {str(e)}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset user tags: {str(e)}"
        )

@router.get("/{user_id}/recommendations", response_model=ContentListResponse)
async def get_user_recommendations(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    tag_filters: Optional[str] = Query(None, description="逗号分隔的标签列表"),
    content_type: Optional[str] = Query(None, description="内容类型筛选"),
    db=Depends(get_database)
):
    """获取用户个性化推荐内容"""
    print(f"🔍 推荐API调用开始: user_id={user_id}, page={page}, page_size={page_size}")
    
    try:
        # 1. 创建推荐服务实例
        print("📊 创建推荐服务实例...")
        recommendation_service = RecommendationService(db)
        
        # 2. 计算分页参数
        skip = (page - 1) * page_size
        print(f"📄 分页参数: skip={skip}, limit={page_size}")
        
        # 3. 获取推荐内容
        print("🎯 获取推荐内容...")
        try:
            recommendations = await recommendation_service.get_user_recommendations(
                user_id=user_id,
                skip=skip,
                limit=page_size
            )
            print(f"✅ 成功获取 {len(recommendations)} 条推荐内容")
        except Exception as rec_error:
            print(f"❌ 推荐服务失败: {str(rec_error)}")
            # 如果推荐服务失败，返回默认内容
            content_service = ContentService(db)
            recommendations = await content_service.get_content_list(
                skip=skip,
                limit=page_size,
                sort_by="latest"
            )
            print(f"🔄 使用默认内容: {len(recommendations)} 条")
        
        # 4. 应用筛选条件
        if tag_filters:
            print(f"🏷️ 应用标签筛选: {tag_filters}")
            filter_tags = [tag.strip() for tag in tag_filters.split(',')]
            filtered_recommendations = []
            
            for content in recommendations:
                try:
                    content_tags = (
                        getattr(content, 'basic_info_tags', []) +
                        getattr(content, 'region_tags', []) +
                        getattr(content, 'energy_type_tags', []) +
                        getattr(content, 'business_field_tags', []) +
                        getattr(content, 'beneficiary_tags', []) +
                        getattr(content, 'policy_measure_tags', []) +
                        getattr(content, 'importance_tags', [])
                    )
                    
                    if any(tag in filter_tags for tag in content_tags):
                        filtered_recommendations.append(content)
                except Exception as filter_error:
                    print(f"⚠️ 标签筛选错误: {str(filter_error)}")
                    # 筛选失败时保留原内容
                    filtered_recommendations.append(content)
            
            recommendations = filtered_recommendations
            print(f"🔍 筛选后内容数量: {len(recommendations)}")

        if content_type:
            print(f"📋 应用内容类型筛选: {content_type}")
            recommendations = [
                content for content in recommendations
                if getattr(content, 'content_type', None) == content_type
            ]
            print(f"📑 筛选后内容数量: {len(recommendations)}")
        
        # 5. 构建响应
        total = max(len(recommendations), 50)  # 简化总数计算
        has_next = len(recommendations) == page_size
        
        print(f"📊 返回推荐结果: {len(recommendations)} 条")
        return ContentListResponse(
            items=recommendations,
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next
        )
        
    except Exception as e:
        print(f"❌ 推荐API错误: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        # 返回空结果而不是抛出异常
        return ContentListResponse(
            items=[],
            total=0,
            page=page,
            page_size=page_size if 'page_size' in locals() else 10,
            has_next=False
        )

@router.get("/{user_id}/tiered-recommendations")
async def get_user_tiered_recommendations(
    user_id: str,
    primary_limit: int = Query(6, ge=1, le=20, description="精准推荐数量"),
    secondary_limit: int = Query(4, ge=1, le=20, description="扩展推荐数量"),
    db=Depends(get_database)
):
    """获取用户分级推荐内容：精准推荐 + 扩展推荐"""
    print(f"🎯 分级推荐API调用: user_id={user_id}, primary={primary_limit}, secondary={secondary_limit}")
    
    try:
        # 创建推荐服务实例
        recommendation_service = RecommendationService(db)
        
        # 获取分级推荐内容
        tiered_result = await recommendation_service.get_tiered_recommendations(
            user_id=user_id,
            primary_limit=primary_limit,
            secondary_limit=secondary_limit
        )
        
        print(f"✅ 分级推荐成功: 精准{tiered_result['total_primary']}篇，扩展{tiered_result['total_secondary']}篇")
        
        return {
            "status": "success",
            "data": {
                "primary_recommendations": [
                    {
                        "id": content.id,
                        "title": content.title,
                        "content": content.content[:200] + "..." if len(content.content) > 200 else content.content,
                        "type": content.type,
                        "source": content.source,
                        "publish_time": content.publish_time,
                        "link": content.link,
                        "relevance_score": getattr(content, 'relevance_score', 0.0),
                        "basic_info_tags": getattr(content, 'basic_info_tags', []),
                        "region_tags": getattr(content, 'region_tags', []),
                        "energy_type_tags": getattr(content, 'energy_type_tags', []),
                        "business_field_tags": getattr(content, 'business_field_tags', []),
                        "beneficiary_tags": getattr(content, 'beneficiary_tags', []),
                        "policy_measure_tags": getattr(content, 'policy_measure_tags', []),
                        "importance_tags": getattr(content, 'importance_tags', [])
                    }
                    for content in tiered_result["primary_recommendations"]
                ],
                "secondary_recommendations": [
                    {
                        "id": content.id,
                        "title": content.title,
                        "content": content.content[:200] + "..." if len(content.content) > 200 else content.content,
                        "type": content.type,
                        "source": content.source,
                        "publish_time": content.publish_time,
                        "link": content.link,
                        "relevance_score": getattr(content, 'relevance_score', 0.0),
                        "basic_info_tags": getattr(content, 'basic_info_tags', []),
                        "region_tags": getattr(content, 'region_tags', []),
                        "energy_type_tags": getattr(content, 'energy_type_tags', []),
                        "business_field_tags": getattr(content, 'business_field_tags', []),
                        "beneficiary_tags": getattr(content, 'beneficiary_tags', []),
                        "policy_measure_tags": getattr(content, 'policy_measure_tags', []),
                        "importance_tags": getattr(content, 'importance_tags', [])
                    }
                    for content in tiered_result["secondary_recommendations"]
                ],
                "stats": {
                    "total_primary": tiered_result["total_primary"],
                    "total_secondary": tiered_result["total_secondary"],
                    "primary_tags_used": tiered_result.get("primary_tags_used", []),
                    "secondary_tags_used": tiered_result.get("secondary_tags_used", [])
                }
            }
        }
        
    except Exception as e:
        print(f"❌ 分级推荐API错误: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": f"获取分级推荐失败: {str(e)}",
            "data": {
                "primary_recommendations": [],
                "secondary_recommendations": [],
                "stats": {
                    "total_primary": 0,
                    "total_secondary": 0,
                    "primary_tags_used": [],
                    "secondary_tags_used": []
                }
            }
        }

@router.post("/behavior")
async def record_user_behavior(
    behavior: UserBehaviorRequest,
    user_id: str = Query(..., description="用户ID"),
    db=Depends(get_database)
):
    """记录用户行为"""
    try:
        recommendation_service = RecommendationService(db)
        
        await recommendation_service.record_user_behavior(
            user_id=user_id,
            action=behavior.action,
            content_id=behavior.content_id,
            duration=behavior.duration
        )
        
        return {"success": True, "message": "User behavior recorded successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record behavior: {str(e)}"
        )

@router.get("/{user_id}/insights", response_model=UserInsightsResponse)
async def get_user_insights(
    user_id: str,
    db=Depends(get_database)
):
    """获取用户行为洞察"""
    try:
        recommendation_service = RecommendationService(db)
        insights = await recommendation_service.get_user_behavior_insights(user_id)
        
        return UserInsightsResponse(**insights)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user insights: {str(e)}"
        )

@router.get("/{user_id}/similar-content/{content_id}")
async def get_similar_content(
    user_id: str,
    content_id: str,
    limit: int = Query(5, ge=1, le=20),
    db=Depends(get_database)
):
    """获取相似内容推荐"""
    try:
        recommendation_service = RecommendationService(db)
        similar_content = await recommendation_service.get_similar_content(
            content_id=content_id,
            limit=limit
        )
        
        return {
            "success": True,
            "data": similar_content,
            "message": "Similar content retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get similar content: {str(e)}"
        )

@router.get("/demo-users", response_model=DemoUsersResponse)
async def get_demo_users(db=Depends(get_database)):
    """获取演示用户列表（用于前端用户切换功能）"""
    try:
        user_service = UserService(db)
        demo_users = await user_service.get_demo_users()
        
        return DemoUsersResponse(
            users=demo_users,
            total=len(demo_users)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get demo users: {str(e)}"
        )

@router.get("/demo-users/{demo_user_id}/tags", response_model=UserTagsResponse)
async def get_demo_user_tags(
    demo_user_id: str,
    db=Depends(get_database)
):
    """根据演示用户ID获取用户标签"""
    try:
        user_service = UserService(db)
        user_tags = await user_service.get_demo_user_tags(demo_user_id)
        
        if not user_tags:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Demo user tags not found"
            )
        
        return UserTagsResponse(
            data=user_tags,
            message="User tags retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get demo user tags: {str(e)}"
        )

@router.get("/provinces-with-cities")
async def get_provinces_with_cities():
    """获取省份及其城市的结构化数据"""
    try:
        provinces_data = RegionMapper.get_provinces_with_cities()
        
        return {
            "provinces": provinces_data,
            "total_provinces": len(provinces_data),
            "total_cities": sum(p["city_count"] for p in provinces_data)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get provinces with cities: {str(e)}"
        )

@router.get("/debug-imports")
async def debug_imports():
    """调试导入问题"""
    try:
        result = {}
        
        # 测试各个导入
        print("🔍 测试导入...")
        
        # 1. 测试EnergyWeightSystem
        try:
            from app.utils.energy_weight_system import EnergyWeightSystem
            products = EnergyWeightSystem.get_all_energy_products()
            result["energy_system"] = f"成功: {len(products)}个产品"
            print(f"✅ EnergyWeightSystem: {len(products)}个产品")
        except Exception as e:
            result["energy_system"] = f"失败: {str(e)}"
            print(f"❌ EnergyWeightSystem: {str(e)}")
        
        # 2. 测试RegionMapper
        try:
            from app.utils.region_mapper import RegionMapper
            provinces = RegionMapper.get_provinces_with_cities()
            result["region_mapper"] = f"成功: {len(provinces)}个省份"
            print(f"✅ RegionMapper: {len(provinces)}个省份")
        except Exception as e:
            result["region_mapper"] = f"失败: {str(e)}"
            print(f"❌ RegionMapper: {str(e)}")
        
        # 3. 测试ContentService
        try:
            # 直接引用已导入的ContentService
            print(f"✅ ContentService类: {ContentService}")
            result["content_service"] = f"成功: {ContentService.__name__}"
        except Exception as e:
            result["content_service"] = f"失败: {str(e)}"
            print(f"❌ ContentService: {str(e)}")
        
        # 4. 测试所有导入的变量是否存在
        imports_status = {}
        test_imports = [
            "EnergyWeightSystem", "RegionMapper", "ContentService", 
            "UserService", "RecommendationService"
        ]
        
        for import_name in test_imports:
            try:
                import_obj = globals().get(import_name)
                if import_obj:
                    imports_status[import_name] = f"存在: {type(import_obj)}"
                else:
                    imports_status[import_name] = "不存在"
            except Exception as e:
                imports_status[import_name] = f"错误: {str(e)}"
        
        result["imports_status"] = imports_status
        
        return {
            "status": "debug_complete",
            "results": result,
            "globals_keys": list(globals().keys())[:20]  # 前20个全局变量
        }
        
    except Exception as e:
        import traceback
        return {
            "status": "debug_error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/tag-options")
async def get_tag_options(
    database = Depends(get_database)
):
    """获取所有标签选项配置"""
    try:
        # 🔥 简化版本，只返回基本的能源类型标签
        print("📍 开始获取标签选项...")
        
        # 直接从能源权重系统获取能源类型标签
        print("📍 获取能源产品...")
        all_energy_products = EnergyWeightSystem.get_all_energy_products()
        energy_type_tags = [product["name"] for product in all_energy_products]
        print(f"📍 获取到 {len(energy_type_tags)} 个能源产品")
        
        # 获取其他预设标签选项
        print("📍 设置基础标签...")
        basic_info_tags = ["政策法规", "行业资讯", "交易公告", "调价公告", "研报分析"]
        business_field_tags = [
            "市场动态", "价格变化", "交易信息", "科技创新", 
            "政策解读", "国际合作", "投资支持", "民营经济发展", 
            "市场准入优化", "公平竞争"
        ]
        beneficiary_tags = [
            "能源企业", "政府机构", "交易方", "民营企业", 
            "国有企业", "外资企业", "LNG交易方"
        ]
        policy_measure_tags = [
            "市场监管", "技术合作", "竞价规则", "投资支持", 
            "市场准入", "创新投融资", "风险管控", "市场准入措施", 
            "价格调整", "区域价格调整"
        ]
        importance_tags = [
            "国家级", "权威发布", "重要政策", "行业影响", 
            "常规公告", "国际影响"
        ]
        
        print("📍 获取地区数据...")
        # 获取地区标签数据
        provinces_data = RegionMapper.get_provinces_with_cities()
        all_cities = []
        all_provinces = []
        
        for province_info in provinces_data:
            all_provinces.append(province_info["name"])
            all_cities.extend(province_info["cities"])
        
        all_regions = [region["name"] for region in RegionMapper.get_all_regions()]
        
        cities_by_region = {}
        for region in RegionMapper.get_all_regions():
            cities_by_region[region["name"]] = RegionMapper.get_cities_by_region(region["code"])
        
        region_tags = {
            "cities": sorted(list(set(all_cities))),
            "provinces": sorted(list(set(all_provinces))),
            "regions": sorted(all_regions),
            "cities_by_region": cities_by_region,
            "total_cities": len(set(all_cities)),
            "total_provinces": len(set(all_provinces)),
            "total_regions": len(all_regions)
        }
        
        # 内容类型映射
        content_type_map = {
            "policy": "政策法规",
            "news": "行业资讯", 
            "price": "调价公告",
            "announcement": "交易公告",
            "report": "研报分析"
        }
        
        print("📍 构造响应数据...")
        result = {
            "energy_type_tags": energy_type_tags,
            "basic_info_tags": basic_info_tags,
            "business_field_tags": business_field_tags,
            "beneficiary_tags": beneficiary_tags,
            "policy_measure_tags": policy_measure_tags,
            "importance_tags": importance_tags,
            "region_tags": region_tags,
            "content_type_map": content_type_map
        }
        
        print(f"📍 返回成功，包含 {len(energy_type_tags)} 个能源标签")
        return result
        
    except Exception as e:
        print(f"❌ 标签选项获取错误: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tag options: {str(e)}"
        )

@router.get("/energy-hierarchy")
async def get_energy_hierarchy():
    """获取能源产品层级结构"""
    try:
        hierarchy = EnergyWeightSystem.get_energy_hierarchy_tree()
        all_products = EnergyWeightSystem.get_all_energy_products()
        categories = EnergyWeightSystem.get_all_categories()
        
        return {
            "hierarchy": hierarchy,
            "all_products": all_products,
            "categories": categories,
            "total_categories": len(categories),
            "total_products": len(all_products)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get energy hierarchy: {str(e)}"
        )

@router.post("/energy-weights")
async def get_energy_weights(request: EnergySelectionRequest):
    """获取能源产品权重配置"""
    try:
        recommendations = EnergyWeightSystem.recommend_energy_weights(request.energy_types)
        
        # 统计信息
        total_weight = sum(rec["recommended_weight"] for rec in recommendations)
        categories_covered = set(rec["category"] for rec in recommendations if rec["category"])
        
        return {
            "recommendations": recommendations,
            "statistics": {
                "total_energies": len(request.energy_types),
                "total_weight": total_weight,
                "categories_covered": list(categories_covered),
                "categories_count": len(categories_covered)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get energy weights: {str(e)}"
        )

@router.post("/validate-energy-selection")
async def validate_energy_selection(request: EnergySelectionRequest):
    """验证和优化用户能源选择"""
    try:
        validation_result = EnergyWeightSystem.validate_energy_selection(request.energy_types)
        recommendations = EnergyWeightSystem.recommend_energy_weights(request.energy_types)
        
        return {
            "validation": validation_result,
            "recommendations": recommendations,
            "optimization_suggestions": validation_result["suggestions"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate energy selection: {str(e)}"
        )

@router.get("/{user_id}/smart-recommendations", response_model=ContentListResponse)
async def get_user_smart_recommendations(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db=Depends(get_database)
):
    """🔥 智能推荐API：精准权重匹配优先 + 时间排序"""
    print(f"🧠 智能推荐API调用: user_id={user_id}, page={page}, page_size={page_size}")
    
    try:
        # 创建推荐服务实例
        recommendation_service = RecommendationService(db)
        
        # 计算分页参数
        skip = (page - 1) * page_size
        print(f"📄 分页参数: skip={skip}, limit={page_size}")
        
        # 🔥 使用新的智能推荐算法
        print("🎯 调用智能推荐算法...")
        recommendations = await recommendation_service.get_smart_recommendations(
            user_id=user_id,
            skip=skip,
            limit=page_size
        )
        
        print(f"✅ 智能推荐成功返回 {len(recommendations)} 条内容")
        
        # 🔥 API层面的最终去重保障
        unique_recommendations = []
        seen_ids = set()
        
        print(f"🔍 API层去重检查: 输入 {len(recommendations)} 条推荐")
        
        for i, content in enumerate(recommendations):
            content_id = content.id
            print(f"   检查第{i+1}条: ID={content_id}, Title={content.title[:30]}...")
            
            if content_id not in seen_ids:
                unique_recommendations.append(content)
                seen_ids.add(content_id)
                print(f"   ✅ 添加到唯一列表 (当前{len(unique_recommendations)}条)")
            else:
                print(f"   ⚠️ API层去重：跳过重复内容 {content.title[:30]}... (ID: {content_id})")
        
        final_recommendations = unique_recommendations
        print(f"🎯 API层去重完成: {len(recommendations)} → {len(final_recommendations)}条唯一内容")
        
        # 构建响应
        total = max(len(final_recommendations), 50)  # 简化总数计算
        has_next = len(final_recommendations) == page_size
        
        print(f"📊 智能推荐API完成: {len(final_recommendations)} 条内容")
        return ContentListResponse(
            items=final_recommendations,
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next
        )
        
    except Exception as e:
        print(f"❌ 智能推荐API错误: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        
        # 回退到普通推荐
        try:
            recommendation_service = RecommendationService(db)
            skip = (page - 1) * page_size
            recommendations = await recommendation_service.get_user_recommendations(
                user_id=user_id,
                skip=skip,
                limit=page_size
            )
            return ContentListResponse(
                items=recommendations,
                total=50,
                page=page,
                page_size=page_size,
                has_next=len(recommendations) == page_size
            )
        except:
            # 最后的回退：返回空结果
            return ContentListResponse(
                items=[],
                total=0,
                page=page,
                page_size=page_size,
                has_next=False
            )

@router.get("/{user_id}/recommendations-by-type/{content_type}", response_model=ContentListResponse)
async def get_user_recommendations_by_type(
    user_id: str,
    content_type: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db=Depends(get_database)
):
    """🎯 按内容类型获取智能推荐：行情/政策/公告独立推荐逻辑"""
    print(f"🎯 按类型推荐API: user_id={user_id}, type={content_type}")
    
    try:
        # 创建推荐服务实例
        recommendation_service = RecommendationService(db)
        
        # 计算分页参数
        skip = (page - 1) * page_size
        
        # 🔥 根据内容类型调用对应的智能推荐逻辑
        if content_type == "market":
            # 行情推荐：行业资讯类内容
            recommendations = await recommendation_service.get_smart_recommendations_by_type(
                user_id=user_id,
                content_types=["news"],
                basic_info_tags=["行业资讯"],
                skip=skip,
                limit=page_size
            )
        elif content_type == "policy":
            # 政策推荐：政策法规类内容
            recommendations = await recommendation_service.get_smart_recommendations_by_type(
                user_id=user_id,
                content_types=["policy"],
                basic_info_tags=["政策法规"],
                skip=skip,
                limit=page_size
            )
        elif content_type == "announcement":
            # 公告推荐：交易公告+调价公告
            recommendations = await recommendation_service.get_smart_recommendations_by_type(
                user_id=user_id,
                content_types=["announcement", "price"],
                basic_info_tags=["交易公告", "调价公告"],
                skip=skip,
                limit=page_size
            )
        else:
            # 全部推荐：使用智能推荐
            recommendations = await recommendation_service.get_smart_recommendations(
                user_id=user_id,
                skip=skip,
                limit=page_size
            )
        
        print(f"✅ 按类型推荐成功: {content_type} - {len(recommendations)}条")
        
        # 🔥 API层面的最终去重保障
        unique_recommendations = []
        seen_ids = set()
        
        print(f"🔍 API层去重检查: 输入 {len(recommendations)} 条推荐")
        
        for i, content in enumerate(recommendations):
            content_id = content.id
            print(f"   检查第{i+1}条: ID={content_id}, Title={content.title[:30]}...")
            
            if content_id not in seen_ids:
                unique_recommendations.append(content)
                seen_ids.add(content_id)
                print(f"   ✅ 添加到唯一列表 (当前{len(unique_recommendations)}条)")
            else:
                print(f"   ⚠️ API层去重：跳过重复内容 {content.title[:30]}... (ID: {content_id})")
        
        final_recommendations = unique_recommendations
        print(f"🎯 API层去重完成: {len(recommendations)} → {len(final_recommendations)}条唯一内容")
        
        # 构建响应
        total = max(len(final_recommendations), 50)
        has_next = len(final_recommendations) == page_size
        
        return ContentListResponse(
            items=final_recommendations,
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next
        )
        
    except Exception as e:
        print(f"❌ 按类型推荐API错误: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        
        # 回退到空结果
        return ContentListResponse(
            items=[],
            total=0,
            page=page,
            page_size=page_size,
            has_next=False
        )