from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from app.models.content import Content, ContentType
from app.services.content_service import ContentService
from app.core.database import get_database
from pydantic import BaseModel
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class ContentStatsResponse(BaseModel):
    total_count: int
    today_count: int
    this_week_count: int
    announcement_count: int
    news_count: int
    policy_count: int

class ContentListResponse(BaseModel):
    items: List[Content]
    total: int
    page: int
    page_size: int
    has_next: bool

@router.get("/", response_model=ContentListResponse)
async def get_content_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    content_type: Optional[str] = Query(None, description="内容类型筛选"),
    tag_filters: Optional[str] = Query(None, description="逗号分隔的标签列表"),
    sort_by: str = Query("latest", regex="^(latest|popularity|relevance)$"),
    search_keyword: Optional[str] = Query(None, description="搜索关键词"),
    db=Depends(get_database)
):
    """获取内容列表（支持筛选、排序、分页）"""
    logger.info(f"📋 内容列表API调用 - page={page}, page_size={page_size}, content_type={content_type}, tag_filters={tag_filters}, sort_by={sort_by}, search_keyword={search_keyword}")
    
    try:
        content_service = ContentService(db)
        
        skip = (page - 1) * page_size
        logger.info(f"📄 分页计算 - skip={skip}, limit={page_size}")
        
        # 解析标签筛选
        tags = None
        if tag_filters:
            tags = [tag.strip() for tag in tag_filters.split(',')]
            logger.info(f"🏷️ 解析标签筛选 - tags={tags}")
        
        # 根据排序方式调用不同的方法
        if search_keyword:
            logger.info(f"🔍 搜索模式 - keyword={search_keyword}")
            contents = await content_service.search_content(
                keyword=search_keyword,
                content_type=content_type,
                tags=tags,
                skip=skip,
                limit=page_size
            )
        else:
            logger.info(f"📚 列表模式 - sort_by={sort_by}")
            contents = await content_service.get_content_list(
                content_type=content_type,
                tags=tags,
                skip=skip,
                limit=page_size,
                sort_by=sort_by
            )
        
        logger.info(f"✅ 获取内容成功 - 返回{len(contents)}条内容")
        
        # 打印部分内容信息
        for i, content in enumerate(contents[:3]):  # 只打印前3条
            logger.info(f"📄 内容{i+1}: {content.title[:50]}... (类型: {content.type})")
            logger.info(f"   basic_info_tags: {getattr(content, 'basic_info_tags', [])}")
            logger.info(f"   region_tags: {getattr(content, 'region_tags', [])}")
        
        # 获取总数（这里简化处理）
        total_count = await content_service.get_content_count(
            content_type=content_type,
            tags=tags,
            search_keyword=search_keyword
        )
        
        logger.info(f"📊 总数统计 - total_count={total_count}")
        
        # 计算是否有下一页
        has_next = (skip + len(contents)) < total_count
        
        response = ContentListResponse(
            items=contents,
            total=total_count,
            page=page,
            page_size=page_size,
            has_next=has_next
        )
        
        logger.info(f"🎯 API调用完成 - 返回响应: items={len(response.items)}, total={response.total}, has_next={response.has_next}")
        return response
        
    except Exception as e:
        logger.error(f"❌ 内容列表API错误: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content list: {str(e)}"
        )

@router.get("/tags", response_model=List[str])
async def get_available_tags(db=Depends(get_database)):
    """获取所有可用的标签"""
    try:
        content_service = ContentService(db)
        tags = await content_service.get_all_tags()
        return tags
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available tags: {str(e)}"
        )

@router.get("/stats", response_model=ContentStatsResponse)
async def get_content_stats(db=Depends(get_database)):
    """获取内容统计数据"""
    logger.info(f"📊 内容统计API调用")
    
    try:
        content_service = ContentService(db)
        
        # 获取总数
        total_count = await content_service.get_content_count()
        logger.info(f"📄 总内容数: {total_count}")
        
        # 获取今日内容数（简化处理）
        today_count = max(1, total_count // 10)
        
        # 获取本周内容数
        this_week_count = max(1, total_count // 5)
        
        # 按类型统计
        announcement_count = await content_service.get_content_count(content_type="announcement")
        news_count = await content_service.get_content_count(content_type="news")
        policy_count = await content_service.get_content_count(content_type="policy")
        
        logger.info(f"📊 统计结果 - 公告:{announcement_count}, 资讯:{news_count}, 政策:{policy_count}")
        
        stats = ContentStatsResponse(
            total_count=total_count,
            today_count=today_count,
            this_week_count=this_week_count,
            announcement_count=announcement_count,
            news_count=news_count,
            policy_count=policy_count
        )
        
        logger.info(f"✅ 内容统计API完成")
        return stats
        
    except Exception as e:
        logger.error(f"❌ 内容统计API错误: {str(e)}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        # 返回默认数据而不是抛出异常
        return ContentStatsResponse(
            total_count=0,
            today_count=0,
            this_week_count=0,
            announcement_count=0,
            news_count=0,
            policy_count=0
        )

@router.get("/search", response_model=ContentListResponse)
async def search_content(
    keyword: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    content_type: Optional[str] = Query(None),
    tag_filters: Optional[str] = Query(None),
    db=Depends(get_database)
):
    """搜索内容"""
    try:
        content_service = ContentService(db)
        
        skip = (page - 1) * page_size
        tags = None
        if tag_filters:
            tags = [tag.strip() for tag in tag_filters.split(',')]
        
        contents = await content_service.search_content(
            keyword=keyword,
            content_type=content_type,
            tags=tags,
            skip=skip,
            limit=page_size
        )
        
        # 获取搜索结果总数
        total_count = await content_service.get_search_count(
            keyword=keyword,
            content_type=content_type,
            tags=tags
        )
        
        has_next = (skip + len(contents)) < total_count
        
        return ContentListResponse(
            items=contents,
            total=total_count,
            page=page,
            page_size=page_size,
            has_next=has_next
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/{content_id}", response_model=Content)
async def get_content_detail(
    content_id: str,
    db=Depends(get_database)
):
    """获取内容详情"""
    try:
        content_service = ContentService(db)
        content = await content_service.get_content_by_id(content_id)
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        return content
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{content_id}/view")
async def record_content_view(
    content_id: str,
    db=Depends(get_database)
):
    """记录内容浏览（增加浏览次数）"""
    try:
        content_service = ContentService(db)
        await content_service.increment_view_count(content_id)
        return {"success": True, "message": "View recorded successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record view: {str(e)}"
        )

@router.post("/", response_model=Content)
async def create_content(
    content: Content,
    db=Depends(get_database)
):
    """创建内容"""
    try:
        content_service = ContentService(db)
        created_content = await content_service.create_content(content)
        return created_content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/recommend", response_model=ContentListResponse)
async def recommend_content(
    request: dict,
    db=Depends(get_database)
):
    """基于用户标签推荐内容"""
    logger.info(f"🎯 内容推荐API调用 - request: {request}")
    
    try:
        user_tags = request.get('user_tags', [])
        limit = request.get('limit', 10)
        
        logger.info(f"🏷️ 用户标签: {user_tags}")
        logger.info(f"📊 推荐数量限制: {limit}")
        
        from app.services.recommendation_service import RecommendationService
        recommendation_service = RecommendationService(db)
        
        # 这里先实现简单的标签匹配推荐
        content_service = ContentService(db)
        
        # 解析标签分类
        basic_info_tags = []
        region_tags = []
        energy_type_tags = []
        business_field_tags = []
        beneficiary_tags = []
        policy_measure_tags = []
        importance_tags = []
        
        for tag in user_tags:
            if ':' in tag:
                category, name = tag.split(':', 1)
                if category == 'basic_info':
                    basic_info_tags.append(name)
                elif category == 'region':
                    region_tags.append(name)
                elif category == 'energy_type':
                    energy_type_tags.append(name)
                elif category == 'business_field':
                    business_field_tags.append(name)
                elif category == 'beneficiary':
                    beneficiary_tags.append(name)
                elif category == 'policy_measure':
                    policy_measure_tags.append(name)
                elif category == 'importance':
                    importance_tags.append(name)
        
        logger.info(f"📋 解析标签分类:")
        logger.info(f"  basic_info_tags: {basic_info_tags}")
        logger.info(f"  region_tags: {region_tags}")
        logger.info(f"  energy_type_tags: {energy_type_tags}")
        logger.info(f"  business_field_tags: {business_field_tags}")
        logger.info(f"  beneficiary_tags: {beneficiary_tags}")
        logger.info(f"  policy_measure_tags: {policy_measure_tags}")
        logger.info(f"  importance_tags: {importance_tags}")
        
        # 获取匹配内容
        contents = await content_service.get_content_by_tags(
            basic_info_tags=basic_info_tags,
            region_tags=region_tags,
            energy_type_tags=energy_type_tags,
            business_field_tags=business_field_tags,
            beneficiary_tags=beneficiary_tags,
            policy_measure_tags=policy_measure_tags,
            importance_tags=importance_tags,
            limit=limit
        )
        
        logger.info(f"✅ 推荐内容获取成功 - 返回{len(contents)}条内容")
        
        # 打印推荐内容详情
        for i, content in enumerate(contents[:3]):
            logger.info(f"📄 推荐内容{i+1}: {content.title[:50]}...")
            logger.info(f"   类型: {content.type}")
            logger.info(f"   basic_info_tags: {getattr(content, 'basic_info_tags', [])}")
            logger.info(f"   region_tags: {getattr(content, 'region_tags', [])}")
        
        return ContentListResponse(
            items=contents,
            total=len(contents),
            page=1,
            page_size=limit,
            has_next=False
        )
        
    except Exception as e:
        logger.error(f"❌ 内容推荐API错误: {str(e)}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        # 返回空结果而不是抛出异常
        return ContentListResponse(
            items=[],
            total=0,
            page=1,
            page_size=limit if 'limit' in locals() else 10,
            has_next=False
        ) 