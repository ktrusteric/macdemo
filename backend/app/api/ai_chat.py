from fastapi import APIRouter, HTTPException, Depends, status, Request
from typing import List, Dict, Any, Optional
from app.services.ai_chat_service import AIChatService
from app.models.ai_chat import (
    ChatRequest, ChatResponse, ChatSession, 
    ChatHistoryQuery, AssistantType
)

router = APIRouter()

def get_ai_chat_service() -> AIChatService:
    """获取AI聊天服务实例"""
    return AIChatService()

@router.get("/assistants", response_model=Dict[str, Dict[str, Any]])
async def get_ai_assistants(chat_service: AIChatService = Depends(get_ai_chat_service)):
    """获取所有AI助手配置"""
    try:
        return chat_service.get_ai_assistant_configs()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取AI助手配置失败: {str(e)}"
        )

@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    http_request: Request,
    chat_service: AIChatService = Depends(get_ai_chat_service)
):
    """发送聊天消息"""
    try:
        # 获取客户端信息
        if not request.user_info:
            request.user_info = {}
        
        # 添加客户端信息
        request.user_info.update({
            "ip": http_request.client.host if http_request.client else "unknown",
            "user_agent": http_request.headers.get("user-agent", "unknown"),
            "timestamp": str(http_request.state.request_time) if hasattr(http_request.state, 'request_time') else None
        })
        
        response = await chat_service.send_message(request)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送消息失败: {str(e)}"
        )

@router.get("/sessions/{session_id}", response_model=Optional[ChatSession])
async def get_session_history(
    session_id: str,
    chat_service: AIChatService = Depends(get_ai_chat_service)
):
    """获取指定会话的聊天历史"""
    try:
        session = await chat_service.get_session_history(session_id)
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话历史失败: {str(e)}"
        )

@router.post("/history/search")
async def search_chat_history(
    query: ChatHistoryQuery,
    chat_service: AIChatService = Depends(get_ai_chat_service)
):
    """搜索聊天历史记录"""
    try:
        sessions, total = await chat_service.search_chat_history(query)
        return {
            "sessions": sessions,
            "total": total,
            "page": query.page,
            "page_size": query.page_size,
            "total_pages": (total + query.page_size - 1) // query.page_size
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索聊天历史失败: {str(e)}"
        )

@router.get("/statistics")
async def get_chat_statistics(
    chat_service: AIChatService = Depends(get_ai_chat_service)
):
    """获取聊天统计信息"""
    try:
        stats = await chat_service.get_chat_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )

@router.post("/sessions/create-with-user")
async def create_session_with_user(
    request: Dict[str, Any],
    chat_service: AIChatService = Depends(get_ai_chat_service)
):
    """创建带用户信息的会话"""
    try:
        session_id = request.get("session_id")
        assistant_type = request.get("assistant_type")
        user_id = request.get("user_id")
        user_info = request.get("user_info", {})
        
        if not session_id or not assistant_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_id和assistant_type是必需的"
            )
        
        session = await chat_service.get_or_create_session(
            session_id=session_id,
            assistant_type=AssistantType(assistant_type),
            user_id=user_id,
            user_info=user_info
        )
        return {"success": True, "session": session.dict()}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建会话失败: {str(e)}"
        )

@router.post("/sessions/{session_id}/save-user-message")
async def save_user_message(
    session_id: str,
    request: Dict[str, Any],
    chat_service: AIChatService = Depends(get_ai_chat_service)
):
    """保存用户发送的消息"""
    try:
        message = request.get("message", "")
        user_id = request.get("user_id")
        user_info = request.get("user_info", {})
        
        success = await chat_service.save_user_message(session_id, message, user_id, user_info)
        return {"success": success, "session_id": session_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存用户消息失败: {str(e)}"
        )

@router.post("/sessions/{session_id}/save-message")
async def save_assistant_message(
    session_id: str,
    request: Dict[str, Any],
    chat_service: AIChatService = Depends(get_ai_chat_service)
):
    """保存AI助手回复消息"""
    try:
        message = request.get("message", "")
        success = await chat_service.save_assistant_message(session_id, message)
        return {"success": success, "session_id": session_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存消息失败: {str(e)}"
        )

@router.delete("/sessions/batch")
async def batch_delete_sessions(
    request: Dict[str, List[str]],
    chat_service: AIChatService = Depends(get_ai_chat_service)
):
    """批量删除聊天会话"""
    try:
        session_ids = request.get("session_ids", [])
        if not session_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_ids参数不能为空"
            )
        
        deleted_count = await chat_service.batch_delete_sessions(session_ids)
        return {
            "success": True, 
            "message": f"成功删除 {deleted_count} 个会话",
            "deleted_count": deleted_count,
            "total_requested": len(session_ids)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量删除会话失败: {str(e)}"
        )

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    chat_service: AIChatService = Depends(get_ai_chat_service)
):
    """删除指定的聊天会话"""
    try:
        success = await chat_service.delete_session(session_id)
        if success:
            return {"success": True, "message": "会话删除成功", "session_id": session_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除会话失败: {str(e)}"
        )

# 测试DELETE路由 - 用于调试
@router.delete("/test-delete/{item_id}")
async def test_delete_route(item_id: str):
    """测试DELETE路由是否工作"""
    return {"message": f"DELETE路由工作正常", "item_id": item_id}

# 管理员专用API
@router.get("/admin/sessions")
async def admin_get_all_sessions(
    page: int = 1,
    page_size: int = 20,
    assistant_type: Optional[str] = None,
    keyword: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    chat_service: AIChatService = Depends(get_ai_chat_service)
):
    """管理员获取所有聊天会话（分页）"""
    try:
        from datetime import datetime
        
        # 构建查询参数
        query = ChatHistoryQuery(
            page=page,
            page_size=page_size,
            keyword=keyword
        )
        
        if assistant_type:
            try:
                query.assistant_type = AssistantType(assistant_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的助手类型: {assistant_type}"
                )
        
        if start_date:
            try:
                query.start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无效的开始日期格式"
                )
        
        if end_date:
            try:
                query.end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无效的结束日期格式"
                )
        
        sessions, total = await chat_service.search_chat_history(query)
        return {
            "sessions": sessions,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话列表失败: {str(e)}"
        )

@router.get("/admin/statistics/detailed")
async def admin_get_detailed_statistics(
    chat_service: AIChatService = Depends(get_ai_chat_service)
):
    """管理员获取详细统计信息"""
    try:
        from datetime import datetime, timedelta
        
        # 获取基础统计
        stats = await chat_service.get_chat_statistics()
        
        # 获取最近7天的活动统计
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_query = ChatHistoryQuery(
            start_date=seven_days_ago,
            page=1,
            page_size=1000  # 获取大量数据用于统计
        )
        
        recent_sessions, _ = await chat_service.search_chat_history(recent_query)
        
        # 按日期分组统计
        daily_stats = {}
        for session in recent_sessions:
            date_key = session.created_at.strftime('%Y-%m-%d')
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    "sessions": 0,
                    "messages": 0,
                    "assistants": set()
                }
            daily_stats[date_key]["sessions"] += 1
            daily_stats[date_key]["messages"] += len(session.messages)
            daily_stats[date_key]["assistants"].add(session.assistant_type.value)
        
        # 转换set为list
        for date_key in daily_stats:
            daily_stats[date_key]["assistants"] = list(daily_stats[date_key]["assistants"])
        
        stats["daily_stats"] = daily_stats
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取详细统计信息失败: {str(e)}"
        ) 