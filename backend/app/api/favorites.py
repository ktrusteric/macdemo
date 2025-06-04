from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any

from app.core.database import get_database
from app.models.user_behavior import FavoriteRequest, FavoriteResponse, UserBehaviorStats
from app.services.favorite_service import FavoriteService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/add", response_model=FavoriteResponse)
async def add_favorite(
    request: FavoriteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    添加收藏文章
    """
    favorite_service = FavoriteService(db)
    result = await favorite_service.add_favorite(current_user.id, request.content_id)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )
    
    return result

@router.delete("/remove/{content_id}", response_model=FavoriteResponse)
async def remove_favorite(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    取消收藏文章
    """
    favorite_service = FavoriteService(db)
    result = await favorite_service.remove_favorite(current_user.id, content_id)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )
    
    return result

@router.get("/list", response_model=List[Dict[str, Any]])
async def get_user_favorites(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    获取用户收藏的文章列表
    """
    favorite_service = FavoriteService(db)
    favorites = await favorite_service.get_user_favorites(current_user.id, limit)
    return favorites

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_user_favorites(
    query: str = "",
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    搜索用户收藏的文章
    """
    favorite_service = FavoriteService(db)
    favorites = await favorite_service.search_user_favorites(current_user.id, query, limit)
    return favorites

@router.get("/check/{content_id}")
async def check_favorite_status(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    检查文章是否已收藏
    """
    favorite_service = FavoriteService(db)
    is_favorited = await favorite_service.is_favorited(current_user.id, content_id)
    return {"is_favorited": is_favorited}

@router.get("/stats", response_model=UserBehaviorStats)
async def get_user_behavior_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    获取用户收藏行为统计
    """
    favorite_service = FavoriteService(db)
    stats = await favorite_service.get_user_behavior_stats(current_user.id)
    return stats

@router.get("/count")
async def get_user_favorites_count(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    获取用户收藏总数
    """
    favorite_service = FavoriteService(db)
    count = await favorite_service.get_user_favorites_count(current_user.id)
    return {"count": count} 