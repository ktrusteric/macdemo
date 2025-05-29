from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from app.models.content import Content, ContentType
from app.services.content_service import ContentService
from app.core.database import get_database
from pydantic import BaseModel

router = APIRouter()

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
    try:
        content_service = ContentService(db)
        
        skip = (page - 1) * page_size
        
        # 解析标签筛选
        tags = None
        if tag_filters:
            tags = [tag.strip() for tag in tag_filters.split(',')]
        
        # 根据排序方式调用不同的方法
        if search_keyword:
            contents = await content_service.search_content(
                keyword=search_keyword,
                content_type=content_type,
                tags=tags,
                skip=skip,
                limit=page_size
            )
        else:
            contents = await content_service.get_content_list(
                content_type=content_type,
                tags=tags,
                skip=skip,
                limit=page_size,
                sort_by=sort_by
            )
        
        # 获取总数（这里简化处理）
        total_count = await content_service.get_content_count(
            content_type=content_type,
            tags=tags,
            search_keyword=search_keyword
        )
        
        # 计算是否有下一页
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