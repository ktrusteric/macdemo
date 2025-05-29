from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any
from pydantic import BaseModel
from app.services.ai_integration_service import AIIntegrationService
from app.core.database import get_database

router = APIRouter()

class ChatRequest(BaseModel):
    assistant_type: str
    message: str
    user_context: Dict[str, Any] = {}

@router.get("/assistants", response_model=Dict[str, Dict[str, Any]])
async def get_ai_assistants():
    """获取所有AI助手配置"""
    try:
        ai_service = AIIntegrationService()
        assistants = ai_service.get_ai_assistant_configs()
        return assistants
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/assistants/{assistant_type}", response_model=Dict[str, Any])
async def get_ai_assistant_config(assistant_type: str):
    """获取指定AI助手配置"""
    try:
        ai_service = AIIntegrationService()
        assistants = ai_service.get_ai_assistant_configs()
        
        if assistant_type not in assistants:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assistant type '{assistant_type}' not found"
            )
        
        config = assistants[assistant_type]
        return await ai_service.load_ai_assistant(config)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/chat", response_model=Dict[str, Any])
async def chat_with_assistant(request: ChatRequest):
    """与AI助手对话"""
    try:
        ai_service = AIIntegrationService()
        response = await ai_service.chat_with_assistant(
            assistant_type=request.assistant_type,
            message=request.message,
            user_context=request.user_context
        )
        return response
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