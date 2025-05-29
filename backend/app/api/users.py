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
async def login_user(
    login: UserLogin,
    db = Depends(get_database)
):
    """用户登录"""
    try:
        user_service = UserService(db)
        user = await user_service.authenticate_user(login.email, login.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        
        # 获取用户可访问功能
        access_features = await user_service.get_access_features(user.role)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active,
                "has_initial_tags": True,
                "access_features": access_features,
                "register_city": user.register_city
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/{user_id}/tags", response_model=UserTagsResponse)
async def get_user_tags(
    user_id: str,
    db=Depends(get_database)
):
    """获取用户标签（自动初始化如果不存在）"""
    try:
        user_service = UserService(db)
        
        # 尝试获取用户标签
        user_tags = await user_service.get_user_tags(user_id)
        
        # 如果没有标签，尝试确保用户有标签
        if not user_tags or not user_tags.tags:
            try:
                user_tags = await user_service.ensure_user_has_tags(user_id)
                message = "User tags initialized and retrieved successfully"
            except Exception as init_error:
                print(f"无法为用户 {user_id} 初始化标签: {init_error}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User tags not found and could not be initialized"
                )
        else:
            message = "User tags retrieved successfully"
        
        return UserTagsResponse(
            data=user_tags,
            message=message
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{user_id}/tags", response_model=UserTagsResponse)
async def update_user_tags(
    user_id: str,
    request: TagUpdateRequest,
    db=Depends(get_database)
):
    """更新用户标签"""
    try:
        user_service = UserService(db)
        updated_tags = await user_service.update_user_tags(user_id, request.tags)
        
        return UserTagsResponse(
            data=updated_tags,
            message="User tags updated successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{user_id}/recommendations", response_model=ContentListResponse)
async def get_user_recommendations(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
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
        
        response = ContentListResponse(
            items=recommendations,
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next
        )
        
        print(f"✅ 推荐API调用成功: 返回 {len(recommendations)} 条内容")
        return response
        
    except Exception as e:
        error_msg = f"推荐服务错误: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"📍 错误类型: {type(e).__name__}")
        
        # 返回空的推荐结果而不是抛出异常
        return ContentListResponse(
            items=[],
            total=0,
            page=page,
            page_size=page_size,
            has_next=False
        )

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
            success=True,
            data=user_tags,
            message="Demo user tags retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get demo user tags: {str(e)}"
        )