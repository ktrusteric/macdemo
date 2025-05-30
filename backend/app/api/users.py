from fastapi import APIRouter, HTTPException, Depends, status, Query
from app.models.user import UserCreate, UserLogin, UserProfile, UserTags, UserTagsResponse, TagUpdateRequest
from app.models.content import Content
from app.services.user_service import UserService
from app.services.recommendation_service import RecommendationService
from app.core.security import create_access_token
from app.core.database import get_database
from app.utils.region_mapper import RegionMapper
from datetime import timedelta
from app.core.config import settings
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

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
        
        # 从请求中提取用户基础信息
        user_data = UserCreate(
            email=request.get("email"),
            username=request.get("username"), 
            password=request.get("password"),
            register_city=request.get("register_city")
        )
        
        # 提取能源类型
        energy_types = request.get("energy_types", [])
        
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
            register_city=user_db.register_city
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
            from app.services.content_service import ContentService
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
                if getattr(content, 'type', None) == content_type
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