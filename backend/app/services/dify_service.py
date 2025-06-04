import httpx
import json
import logging
from typing import Dict, Any, List
from ..core.config import settings

logger = logging.getLogger(__name__)

class DifyService:
    def __init__(self):
        self.base_url = "http://14.103.245.50"
        self.workflow_id = "YjWVMhiqPWMiPyBa"
        self.api_key = "app-tMMggTYFEfVrRPnkyhd8Ltap"
        self.endpoint = f"{self.base_url}/v1/workflows/run"
        
    async def generate_article_tags(self, article_content: str) -> Dict[str, List[str]]:
        """
        调用Dify工作流API生成文章标签
        
        Args:
            article_content: 文章内容
            
        Returns:
            Dict: 包含6大类标签的字典
        """
        try:
            logger.info(f"🤖 开始调用Dify API生成标签，文章长度: {len(article_content)}")
            
            # 准备请求数据
            request_data = {
                "inputs": {
                    "query": article_content
                },
                "response_mode": "blocking",
                "user": "energy-system-admin"
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 发送请求
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.endpoint,
                    json=request_data,
                    headers=headers
                )
            
            if response.status_code != 200:
                logger.error(f"❌ Dify API调用失败: {response.status_code} - {response.text}")
                raise Exception(f"Dify API调用失败: {response.status_code}")
            
            result = response.json()
            logger.info(f"✅ Dify API调用成功，状态: {result.get('workflow_run_id', 'unknown')}")
            
            # 解析返回的标签数据
            if 'data' in result and 'outputs' in result['data']:
                outputs = result['data']['outputs']
                tags_data = self._parse_tags_output(outputs)
                
                logger.info(f"🏷️ 标签解析成功: {len(tags_data)} 个标签类别")
                return tags_data
            else:
                logger.warning("⚠️ Dify API返回格式异常，使用空标签")
                return self._get_empty_tags()
                
        except Exception as e:
            logger.error(f"❌ 调用Dify API生成标签失败: {str(e)}")
            # 返回空标签而不是抛出异常，确保文章创建不受影响
            return self._get_empty_tags()
    
    def _parse_tags_output(self, outputs: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        解析Dify工作流输出的标签数据
        
        Args:
            outputs: Dify工作流的输出数据
            
        Returns:
            Dict: 标准化的标签数据
        """
        try:
            # 尝试从不同可能的输出字段获取标签数据
            tags_text = None
            
            # 方法1: 直接获取text字段
            if 'text' in outputs:
                tags_text = outputs['text']
            
            # 方法2: 从其他可能的字段获取
            elif 'result' in outputs:
                tags_text = outputs['result']
            elif 'output' in outputs:
                tags_text = outputs['output']
            
            if not tags_text:
                logger.warning("⚠️ 无法从Dify输出中提取标签文本")
                return self._get_empty_tags()
            
            # 尝试解析JSON格式的标签
            try:
                # 如果返回的是Unicode编码的JSON，先解码
                if isinstance(tags_text, str) and '\\u' in tags_text:
                    tags_text = tags_text.encode().decode('unicode_escape')
                
                # 解析JSON
                if isinstance(tags_text, str):
                    tags_data = json.loads(tags_text)
                else:
                    tags_data = tags_text
                
                # 标准化标签数据
                standardized_tags = {
                    'region_tags': self._extract_tag_list(tags_data.get('地域标签', [])),
                    'energy_type_tags': self._extract_tag_list(tags_data.get('能源品种标签', [])),
                    'business_field_tags': self._extract_tag_list(tags_data.get('业务领域/主题标签', [])),
                    'beneficiary_tags': self._extract_tag_list(tags_data.get('受益主体标签', [])),
                    'policy_measure_tags': self._extract_tag_list(tags_data.get('关键措施/政策标签', [])),
                    'importance_tags': self._extract_tag_list(tags_data.get('重要性/影响力标签', []))
                }
                
                # 过滤空标签
                for key in standardized_tags:
                    standardized_tags[key] = [tag for tag in standardized_tags[key] if tag and tag.strip()]
                
                logger.info(f"🎯 标签解析详情: {standardized_tags}")
                return standardized_tags
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON解析失败: {str(e)}")
                logger.error(f"原始文本: {tags_text}")
                return self._get_empty_tags()
                
        except Exception as e:
            logger.error(f"❌ 标签输出解析失败: {str(e)}")
            return self._get_empty_tags()
    
    def _extract_tag_list(self, tag_data) -> List[str]:
        """
        提取标签列表，处理各种可能的数据格式
        
        Args:
            tag_data: 标签数据（可能是字符串、列表等）
            
        Returns:
            List[str]: 标签列表
        """
        if not tag_data:
            return []
        
        if isinstance(tag_data, list):
            return [str(tag).strip() for tag in tag_data if tag and str(tag).strip()]
        elif isinstance(tag_data, str):
            # 尝试分割字符串（可能用逗号、分号等分隔）
            if ',' in tag_data:
                return [tag.strip() for tag in tag_data.split(',') if tag.strip()]
            elif '；' in tag_data:
                return [tag.strip() for tag in tag_data.split('；') if tag.strip()]
            elif ';' in tag_data:
                return [tag.strip() for tag in tag_data.split(';') if tag.strip()]
            else:
                return [tag_data.strip()] if tag_data.strip() else []
        else:
            return [str(tag_data).strip()] if str(tag_data).strip() else []
    
    def _get_empty_tags(self) -> Dict[str, List[str]]:
        """
        返回空的标签数据结构
        
        Returns:
            Dict: 空的标签数据
        """
        return {
            'region_tags': [],
            'energy_type_tags': [],
            'business_field_tags': [],
            'beneficiary_tags': [],
            'policy_measure_tags': [],
            'importance_tags': []
        }

# 创建全局实例
dify_service = DifyService() 