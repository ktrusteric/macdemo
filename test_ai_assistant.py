#!/usr/bin/env python3
"""
AI智能助手系统 - 快速功能测试脚本
用于验证后端API服务是否正常运行
"""

import asyncio
import httpx
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8001/api/v1/ai-chat"
TEST_TIMEOUT = 10

class AIAssistantTester:
    def __init__(self):
        self.session_id = f"test_session_{int(datetime.now().timestamp())}"
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
    
    async def test_get_assistants(self):
        """测试获取AI助手配置"""
        print("🤖 测试获取AI助手配置...")
        try:
            response = await self.client.get(f"{BASE_URL}/assistants")
            if response.status_code == 200:
                data = response.json()
                print("✅ 助手配置获取成功:")
                for key, assistant in data.items():
                    print(f"   - {assistant['name']} ({assistant['avatar']}): {assistant['description']}")
                return True
            else:
                print(f"❌ 获取助手配置失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 获取助手配置异常: {e}")
            return False
    
    async def test_send_message(self, assistant_type: str, message: str):
        """测试发送聊天消息"""
        print(f"💬 测试发送消息给 {assistant_type}...")
        try:
            payload = {
                "session_id": self.session_id,
                "assistant_type": assistant_type,
                "message": message,
                "user_info": {
                    "ip": "127.0.0.1",
                    "user_agent": "Test Script",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            response = await self.client.post(f"{BASE_URL}/chat", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 消息发送成功:")
                print(f"   用户: {data['user_message']['content']}")
                print(f"   助手: {data['assistant_message']['content'][:100]}...")
                return True
            else:
                print(f"❌ 发送消息失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 发送消息异常: {e}")
            return False
    
    async def test_get_session_history(self):
        """测试获取会话历史"""
        print("📜 测试获取会话历史...")
        try:
            response = await self.client.get(f"{BASE_URL}/sessions/{self.session_id}")
            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"✅ 会话历史获取成功: {len(data['messages'])} 条消息")
                    return True
                else:
                    print("ℹ️ 会话历史为空")
                    return True
            else:
                print(f"❌ 获取会话历史失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 获取会话历史异常: {e}")
            return False
    
    async def test_search_history(self):
        """测试搜索聊天历史"""
        print("🔍 测试搜索聊天历史...")
        try:
            payload = {
                "page": 1,
                "page_size": 10,
                "keyword": "test"
            }
            
            response = await self.client.post(f"{BASE_URL}/history/search", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 历史搜索成功: 找到 {data['total']} 条记录")
                return True
            else:
                print(f"❌ 搜索历史失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 搜索历史异常: {e}")
            return False
    
    async def test_statistics(self):
        """测试获取统计信息"""
        print("📊 测试获取统计信息...")
        try:
            response = await self.client.get(f"{BASE_URL}/statistics")
            if response.status_code == 200:
                data = response.json()
                print("✅ 统计信息获取成功:")
                if 'summary' in data:
                    summary = data['summary']
                    print(f"   总会话数: {summary.get('total_sessions', 0)}")
                    print(f"   总消息数: {summary.get('total_messages', 0)}")
                return True
            else:
                print(f"❌ 获取统计信息失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 获取统计信息异常: {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始AI智能助手系统功能测试...\n")
        
        results = []
        
        # 1. 测试获取助手配置
        results.append(await self.test_get_assistants())
        print()
        
        # 2. 测试发送消息给不同助手
        test_messages = [
            ("customer_service", "你好，我需要帮助"),
            ("news_assistant", "最新的能源政策有哪些？"),
            ("trading_assistant", "天然气市场行情如何？")
        ]
        
        for assistant_type, message in test_messages:
            results.append(await self.test_send_message(assistant_type, message))
            print()
            # 等待一下避免请求过快
            await asyncio.sleep(1)
        
        # 3. 测试获取会话历史
        results.append(await self.test_get_session_history())
        print()
        
        # 4. 测试搜索历史
        results.append(await self.test_search_history())
        print()
        
        # 5. 测试统计信息
        results.append(await self.test_statistics())
        print()
        
        # 总结测试结果
        successful_tests = sum(results)
        total_tests = len(results)
        
        print("=" * 50)
        print(f"测试完成！成功 {successful_tests}/{total_tests} 项测试")
        
        if successful_tests == total_tests:
            print("🎉 所有测试通过！AI智能助手系统运行正常。")
        else:
            print("⚠️ 部分测试失败，请检查系统配置和服务状态。")
        
        print("\n📋 测试说明:")
        print("- 确保后端服务运行在 http://localhost:8001")
        print("- 确保MongoDB服务正常运行")
        print("- 如果AI服务测试失败，请检查网络连接")
        
        return successful_tests == total_tests
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()

async def main():
    """主函数"""
    tester = AIAssistantTester()
    try:
        success = await tester.run_all_tests()
        return 0 if success else 1
    finally:
        await tester.close()

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 