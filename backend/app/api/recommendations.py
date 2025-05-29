from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List
from app.models.content import Content
from app.services.recommendation_service import RecommendationService
from app.core.database import get_database

router = APIRouter()

@router.get("/{user_id}", response_model=List[Content])
async def get_user_recommendations(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db=Depends(get_database)
):
    """获取用户个性化推荐"""
    try:
        recommendation_service = RecommendationService(db)
        recommendations = await recommendation_service.get_user_recommendations(
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/trending/all", response_model=List[Content])
async def get_trending_content(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db=Depends(get_database)
):
    """获取热门内容"""
    try:
        recommendation_service = RecommendationService(db)
        trending = await recommendation_service.get_trending_content(
            skip=skip,
            limit=limit
        )
        return trending
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/similar/{content_id}", response_model=List[Content])
async def get_similar_content(
    content_id: str,
    limit: int = Query(5, ge=1, le=20),
    db=Depends(get_database)
):
    """获取相似内容"""
    try:
        recommendation_service = RecommendationService(db)
        similar_content = await recommendation_service.get_similar_content(
            content_id=content_id,
            limit=limit
        )
        return similar_content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 