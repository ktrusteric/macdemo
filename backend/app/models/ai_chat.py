from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class AssistantType(str, Enum):
    """AI助手类型枚举"""
    CUSTOMER_SERVICE = "customer_service"
    NEWS_ASSISTANT = "news_assistant"
    TRADING_ASSISTANT = "trading_assistant"

class MessageRole(str, Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessage(BaseModel):
    """聊天消息数据模型"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    """聊天会话数据模型"""
    id: Optional[str] = None
    user_id: Optional[str] = None  # 可选，支持匿名用户
    session_id: str  # 前端生成的会话ID
    assistant_type: AssistantType
    assistant_name: str
    messages: list[ChatMessage] = []
    user_info: Optional[Dict[str, Any]] = None  # 用户信息（IP、设备等）
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    username: Optional[str] = None  # 用户名（扩展字段，用于显示）

class ChatHistoryQuery(BaseModel):
    """聊天记录查询参数"""
    assistant_type: Optional[AssistantType] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    keyword: Optional[str] = None  # 搜索关键词
    page: int = 1
    page_size: int = 20

class ChatRequest(BaseModel):
    """聊天请求数据模型"""
    session_id: str
    assistant_type: AssistantType
    message: str
    user_id: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """聊天响应数据模型"""
    session_id: str
    assistant_name: str
    user_message: ChatMessage
    assistant_message: ChatMessage
    success: bool = True
    error_message: Optional[str] = None 