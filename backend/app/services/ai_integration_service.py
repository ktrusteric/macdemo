import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.models.content import Content, ContentTag

class AIIntegrationService:
    def __init__(self):
        self.base_url = settings.AI_BACKEND_URL
        self.timeout = settings.AI_API_TIMEOUT

    async def generate_content_tags(self, content: Content) -> List[ContentTag]:
        """调用AI服务生成内容标签"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/auto-tagging",
                    json={
                        "title": content.title,
                        "content": content.content,
                        "content_type": content.type
                    }
                )
                response.raise_for_status()
                
                ai_response = response.json()
                return self._parse_ai_tags(ai_response)
        except httpx.TimeoutException:
            raise Exception("AI service timeout")
        except httpx.HTTPStatusError as e:
            raise Exception(f"AI service error: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to generate tags: {str(e)}")

    def _parse_ai_tags(self, ai_response: Dict[str, Any]) -> List[ContentTag]:
        """解析AI返回的标签数据"""
        tags = []
        for tag_data in ai_response.get("tags", []):
            category = self._map_ai_category(tag_data.get("category"))
            if category:
                tags.append(ContentTag(
                    category=category,
                    name=tag_data.get("name"),
                    confidence=tag_data.get("confidence", 0.8)
                ))
        return tags

    def _map_ai_category(self, ai_category: str) -> Optional[str]:
        """映射AI返回的分类到系统分类"""
        category_mapping = {
            "基础信息": "basic_info",
            "地域": "region",
            "能源类型": "energy_type",
            "业务领域": "business_field",
            "受益主体": "beneficiary",
            "政策措施": "policy_measure",
            "重要性": "importance"
        }
        return category_mapping.get(ai_category)

    async def load_ai_assistant(self, assistant_config: Dict[str, Any]) -> Dict[str, Any]:
        """加载AI助手配置"""
        return {
            "bot_config": {
                "id": assistant_config["id"],
                "token": assistant_config["token"],
                "size": "normal",
                "theme": "dark",
                "host": self.base_url,
                "user_context": assistant_config.get("user_context", {})
            }
        }
    
    def get_ai_assistant_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取所有AI助手配置"""
        return {
            "customer_service": {
                "id": "9714d9bc-31ca-40b5-a720-4329f5fc4af7",
                "token": "e0dc8833077b48669a04ad4a70a7ebe2",
                "name": "客服助手",
                "description": "提供账户问题、功能咨询、技术支持、操作指导等服务",
                "features": ["账户问题", "功能咨询", "技术支持", "操作指导"]
            },
            "news_assistant": {
                "id": "158ab70e-2996-4cce-9822-6f8195a7cfa5",
                "token": "9bc6008decb94efeaee65dd076aab5e8",
                "name": "资讯助手",
                "description": "提供市场快讯、政策解读、行业分析、趋势预测等信息",
                "features": ["市场快讯", "政策解读", "行业分析", "趋势预测"]
            },
            "trading_assistant": {
                "id": "1e72acc1-43a8-4cda-8d54-f409c9c5d5ed",
                "token": "18703d14357040c88f32ae5e4122c2d6",
                "name": "交易助手",
                "description": "提供策略建议、风险评估、交易分析、市场机会等服务",
                "features": ["策略建议", "风险评估", "交易分析", "市场机会"]
            }
        }

    async def chat_with_assistant(
        self, 
        assistant_type: str, 
        message: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """与AI助手对话"""
        try:
            assistant_configs = self.get_ai_assistant_configs()
            if assistant_type not in assistant_configs:
                raise ValueError(f"Unknown assistant type: {assistant_type}")
            
            config = assistant_configs[assistant_type]
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "bot_id": config["id"],
                        "token": config["token"],
                        "message": message,
                        "user_context": user_context or {}
                    }
                )
                response.raise_for_status()
                
                return response.json()
        except Exception as e:
            raise Exception(f"Failed to chat with assistant: {str(e)}") 