import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.core.config import settings
from app.core.database import db_manager
from app.models.ai_chat import (
    ChatSession, ChatMessage, MessageRole, AssistantType,
    ChatRequest, ChatResponse, ChatHistoryQuery
)

class AIChatService:
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self.db = db
        self.base_url = settings.AI_BACKEND_URL
        self.timeout = settings.AI_API_TIMEOUT
    
    @property
    def collection(self):
        """动态获取数据库集合"""
        database = self.db if self.db is not None else db_manager.database
        if database is None:
            raise RuntimeError("数据库连接未初始化")
        return database.ai_chat_sessions

    def get_ai_assistant_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取所有AI助手配置"""
        return {
            "customer_service": {
                "id": "9714d9bc-31ca-40b5-a720-4329f5fc4af7",
                "token": "e0dc8833077b48669a04ad4a70a7ebe2",
                "name": "客服助手",
                "description": "提供账户问题、功能咨询、技术支持、操作指导等服务",
                "features": ["账户问题", "功能咨询", "技术支持", "操作指导"],
                "avatar": "🤖",
                "color": "#1890FF"
            },
            "news_assistant": {
                "id": "158ab70e-2996-4cce-9822-6f8195a7cfa5",
                "token": "9bc6008decb94efeaee65dd076aab5e8",
                "name": "资讯助手",
                "description": "提供市场快讯、政策解读、行业分析、趋势预测等信息",
                "features": ["市场快讯", "政策解读", "行业分析", "趋势预测"],
                "avatar": "📰",
                "color": "#52C41A"
            },
            "trading_assistant": {
                "id": "1e72acc1-43a8-4cda-8d54-f409c9c5d5ed",
                "token": "18703d14357040c88f32ae5e4122c2d6",
                "name": "交易助手",
                "description": "提供策略建议、风险评估、交易分析、市场机会等服务",
                "features": ["策略建议", "风险评估", "交易分析", "市场机会"],
                "avatar": "💼",
                "color": "#FA8C16"
            }
        }

    async def get_or_create_session(
        self, 
        session_id: str, 
        assistant_type: AssistantType,
        user_id: Optional[str] = None,
        user_info: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """获取或创建聊天会话"""
        existing_session = await self.collection.find_one({
            "session_id": session_id,
            "assistant_type": assistant_type.value
        })
        
        if existing_session:
            # 转换消息格式
            messages = []
            for msg in existing_session.get("messages", []):
                messages.append(ChatMessage(
                    role=MessageRole(msg["role"]),
                    content=msg["content"],
                    timestamp=msg["timestamp"]
                ))
            
            return ChatSession(
                id=str(existing_session["_id"]),
                user_id=existing_session.get("user_id"),
                session_id=existing_session["session_id"],
                assistant_type=AssistantType(existing_session["assistant_type"]),
                assistant_name=existing_session["assistant_name"],
                messages=messages,
                user_info=existing_session.get("user_info"),
                created_at=existing_session["created_at"],
                updated_at=existing_session["updated_at"]
            )
        else:
            # 创建新会话
            assistant_configs = self.get_ai_assistant_configs()
            assistant_config = assistant_configs.get(assistant_type.value)
            
            if not assistant_config:
                raise ValueError(f"Unknown assistant type: {assistant_type.value}")
            
            new_session = ChatSession(
                user_id=user_id,
                session_id=session_id,
                assistant_type=assistant_type,
                assistant_name=assistant_config["name"],
                user_info=user_info
            )
            
            # 保存到数据库
            session_dict = new_session.dict(exclude={"id"})
            result = await self.collection.insert_one(session_dict)
            new_session.id = str(result.inserted_id)
            
            return new_session

    async def send_message(self, request: ChatRequest) -> ChatResponse:
        """发送消息给AI助手并保存聊天记录 - 现在主要用于会话管理"""
        try:
            # 获取或创建会话
            session = await self.get_or_create_session(
                session_id=request.session_id,
                assistant_type=request.assistant_type,
                user_id=request.user_id,
                user_info=request.user_info
            )
            
            # 创建用户消息
            user_message = ChatMessage(
                role=MessageRole.USER,
                content=request.message
            )
            
            # 获取助手配置
            assistant_configs = self.get_ai_assistant_configs()
            config = assistant_configs[request.assistant_type.value]
            
            # 注意：实际的AI对话将通过前端JavaScript SDK处理
            # 这里主要用于会话管理和消息记录
            
            # 创建助手消息占位符（实际回复将通过前端SDK获得）
            assistant_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content="[消息通过前端SDK处理]"  # 占位符，实际内容由前端更新
            )
            
            # 保存用户消息到会话
            await self.collection.update_one(
                {"_id": ObjectId(session.id)},
                {
                    "$push": {
                        "messages": user_message.dict()
                    },
                    "$set": {
                        "updated_at": datetime.utcnow(),
                        "user_id": request.user_id
                    }
                }
            )
            
            return ChatResponse(
                session_id=session.session_id,
                assistant_name=session.assistant_name,
                user_message=user_message,
                assistant_message=assistant_message,
                success=True
            )
            
        except Exception as e:
            print(f"AI聊天服务错误: {str(e)}")
            return ChatResponse(
                session_id=request.session_id,
                assistant_name="AI助手",
                user_message=ChatMessage(
                    role=MessageRole.USER,
                    content=request.message
                ),
                assistant_message=ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content="服务暂时不可用，请稍后重试。"
                ),
                success=False,
                error_message=str(e)
            )

    async def save_assistant_message(self, session_id: str, assistant_message: str) -> bool:
        """保存AI助手回复消息（由前端调用）"""
        try:
            message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=assistant_message
            )
            
            await self.collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {
                        "messages": message.dict()
                    },
                    "$set": {
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return True
        except Exception as e:
            print(f"保存助手消息失败: {str(e)}")
            return False

    async def save_user_message(self, session_id: str, user_message: str, user_id: Optional[str] = None, user_info: Optional[Dict[str, Any]] = None) -> bool:
        """保存用户发送的消息"""
        try:
            message = ChatMessage(
                role=MessageRole.USER,
                content=user_message
            )
            
            update_data = {
                "$push": {
                    "messages": message.dict()
                },
                "$set": {
                    "updated_at": datetime.utcnow()
                }
            }
            
            # 如果提供了用户信息，同时更新
            if user_id:
                update_data["$set"]["user_id"] = user_id
            if user_info:
                update_data["$set"]["user_info"] = user_info
            
            await self.collection.update_one(
                {"session_id": session_id},
                update_data
            )
            return True
        except Exception as e:
            print(f"保存用户消息失败: {str(e)}")
            return False

    async def get_session_history(self, session_id: str) -> Optional[ChatSession]:
        """获取指定会话的聊天历史"""
        session_doc = await self.collection.find_one({"session_id": session_id})
        
        if not session_doc:
            return None
        
        # 转换消息格式
        messages = []
        for msg in session_doc.get("messages", []):
            messages.append(ChatMessage(
                role=MessageRole(msg["role"]),
                content=msg["content"],
                timestamp=msg["timestamp"]
            ))
        
        return ChatSession(
            id=str(session_doc["_id"]),
            user_id=session_doc.get("user_id"),
            session_id=session_doc["session_id"],
            assistant_type=AssistantType(session_doc["assistant_type"]),
            assistant_name=session_doc["assistant_name"],
            messages=messages,
            user_info=session_doc.get("user_info"),
            created_at=session_doc["created_at"],
            updated_at=session_doc["updated_at"]
        )

    async def search_chat_history(self, query: ChatHistoryQuery) -> Tuple[List[ChatSession], int]:
        """搜索聊天历史记录"""
        filter_dict = {}
        
        # 构建查询条件
        if query.assistant_type:
            filter_dict["assistant_type"] = query.assistant_type.value
        
        if query.user_id:
            filter_dict["user_id"] = query.user_id
        
        if query.session_id:
            filter_dict["session_id"] = query.session_id
        
        if query.start_date or query.end_date:
            date_filter = {}
            if query.start_date:
                date_filter["$gte"] = query.start_date
            if query.end_date:
                date_filter["$lte"] = query.end_date
            filter_dict["created_at"] = date_filter
        
        # 关键词搜索（在消息内容中搜索）
        if query.keyword:
            filter_dict["$or"] = [
                {"messages.content": {"$regex": query.keyword, "$options": "i"}},
                {"assistant_name": {"$regex": query.keyword, "$options": "i"}}
            ]
        
        # 计算总数
        total = await self.collection.count_documents(filter_dict)
        
        # 分页查询
        skip = (query.page - 1) * query.page_size
        cursor = self.collection.find(filter_dict).sort("updated_at", -1).skip(skip).limit(query.page_size)
        
        sessions = []
        async for session_doc in cursor:
            # 转换消息格式
            messages = []
            for msg in session_doc.get("messages", []):
                messages.append(ChatMessage(
                    role=MessageRole(msg["role"]),
                    content=msg["content"],
                    timestamp=msg["timestamp"]
                ))
            
            # 获取用户名
            username = "匿名用户"
            if session_doc.get("user_id"):
                # 从用户表获取用户名
                user_collection = self.db.users if self.db else db_manager.database.users
                try:
                    # 处理UUID格式的用户ID，而不是ObjectId
                    user_doc = await user_collection.find_one({"_id": session_doc["user_id"]})
                    if user_doc:
                        username = user_doc.get("username", "未知用户")
                    else:
                        # 如果没找到，可能用户信息中包含用户名
                        if session_doc.get("user_info") and session_doc["user_info"].get("username"):
                            username = session_doc["user_info"]["username"]
                except Exception as e:
                    # 如果查询失败，尝试从user_info中获取用户名
                    if session_doc.get("user_info") and session_doc["user_info"].get("username"):
                        username = session_doc["user_info"]["username"]
                    else:
                        username = f"用户{session_doc['user_id'][:8]}"
            
            session = ChatSession(
                id=str(session_doc["_id"]),
                user_id=session_doc.get("user_id"),
                session_id=session_doc["session_id"],
                assistant_type=AssistantType(session_doc["assistant_type"]),
                assistant_name=session_doc["assistant_name"],
                messages=messages,
                user_info=session_doc.get("user_info"),
                created_at=session_doc["created_at"],
                updated_at=session_doc["updated_at"]
            )
            
            # 添加用户名到会话对象（扩展字段）
            session.username = username
            
            sessions.append(session)
        
        return sessions, total

    async def get_chat_statistics(self) -> Dict[str, Any]:
        """获取聊天统计信息"""
        pipeline = [
            {
                "$group": {
                    "_id": "$assistant_type",
                    "session_count": {"$sum": 1},
                    "message_count": {"$sum": {"$size": "$messages"}},
                    "last_activity": {"$max": "$updated_at"}
                }
            }
        ]
        
        stats = {}
        async for stat in self.collection.aggregate(pipeline):
            stats[stat["_id"]] = {
                "session_count": stat["session_count"],
                "message_count": stat["message_count"],
                "last_activity": stat["last_activity"]
            }
        
        # 总体统计
        total_sessions = await self.collection.count_documents({})
        total_messages = await self.collection.aggregate([
            {"$group": {"_id": None, "total": {"$sum": {"$size": "$messages"}}}}
        ]).to_list(1)
        
        stats["summary"] = {
            "total_sessions": total_sessions,
            "total_messages": total_messages[0]["total"] if total_messages else 0
        }
        
        return stats

    async def delete_session(self, session_id: str) -> bool:
        """删除指定的聊天会话"""
        try:
            result = await self.collection.delete_one({"session_id": session_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"删除会话失败: {e}")
            return False

    async def batch_delete_sessions(self, session_ids: List[str]) -> int:
        """批量删除聊天会话"""
        try:
            result = await self.collection.delete_many({"session_id": {"$in": session_ids}})
            return result.deleted_count
        except Exception as e:
            print(f"批量删除会话失败: {e}")
            return 0

    async def get_statistics(self) -> Dict[str, Any]:
        """获取聊天统计信息"""
        pipeline = [
            {
                "$group": {
                    "_id": "$assistant_type",
                    "session_count": {"$sum": 1},
                    "message_count": {"$sum": {"$size": "$messages"}},
                    "last_activity": {"$max": "$updated_at"}
                }
            }
        ]
        
        stats = {}
        async for stat in self.collection.aggregate(pipeline):
            stats[stat["_id"]] = {
                "session_count": stat["session_count"],
                "message_count": stat["message_count"],
                "last_activity": stat["last_activity"]
            }
        
        # 总体统计
        total_sessions = await self.collection.count_documents({})
        total_messages = await self.collection.aggregate([
            {"$group": {"_id": None, "total": {"$sum": {"$size": "$messages"}}}}
        ]).to_list(1)
        
        stats["summary"] = {
            "total_sessions": total_sessions,
            "total_messages": total_messages[0]["total"] if total_messages else 0
        }
        
        return stats 