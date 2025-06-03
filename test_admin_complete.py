#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上海石油天然气交易中心信息门户系统 - 管理员后台完整测试
验证管理员后台的全部功能正常运行
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:8001"
ADMIN_CREDENTIALS = [
    {"username": "superadmin", "password": "super123456"},
    {"username": "admin", "password": "admin123456"}
]

class AdminTestSuite:
    def __init__(self):
        self.session = None
        self.admin_token = None
        
    async def setup(self):
        """初始化测试环境"""
        self.session = aiohttp.ClientSession()
        print("🚀 管理员后台修复验证测试")
        print("=" * 50)
        
    async def cleanup(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()
    
    async def test_admin_login(self):
        """测试管理员登录"""
        print("\n1️⃣ 测试管理员登录功能")
        print("-" * 30)
        
        for i, creds in enumerate(ADMIN_CREDENTIALS):
            try:
                async with self.session.post(
                    f"{BASE_URL}/api/v1/admin/login",
                    json=creds
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if i == 0:  # 使用第一个管理员进行后续测试
                            self.admin_token = data.get('access_token')
                        print(f"✅ {creds['username']} 登录成功")
                        print(f"   Token: {data.get('access_token', 'N/A')[:20]}...")
                    else:
                        print(f"❌ {creds['username']} 登录失败: {resp.status}")
            except Exception as e:
                print(f"❌ {creds['username']} 登录异常: {e}")
        
        return self.admin_token is not None
    
    async def test_admin_stats(self):
        """测试管理员统计API"""
        print("\n2️⃣ 测试管理员统计数据")
        print("-" * 30)
        
        if not self.admin_token:
            print("❌ 无管理员Token，跳过测试")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            async with self.session.get(
                f"{BASE_URL}/api/v1/admin/stats",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ 管理员统计API响应成功")
                    print(f"   数据结构: {json.dumps(data, ensure_ascii=False, indent=2)}")
                    
                    # 验证关键数据
                    articles = data.get('articles', {})
                    users = data.get('users', {})
                    
                    print(f"\n📊 统计数据验证:")
                    print(f"   总文章数: {articles.get('total', 0)}")
                    print(f"   文章类型分布: {articles.get('by_type', {})}")
                    print(f"   总用户数: {users.get('total', 0)}")
                    print(f"   管理员数: {users.get('admins', 0)}")
                    print(f"   普通用户数: {users.get('regular_users', 0)}")
                    
                    # 验证数据合理性
                    if articles.get('total', 0) > 0:
                        print("✅ 文章数据正常")
                    else:
                        print("⚠️ 文章数据为空")
                        
                    if users.get('total', 0) >= 2:  # 至少有管理员
                        print("✅ 用户数据正常")
                    else:
                        print("⚠️ 用户数据异常")
                        
                    return True
                else:
                    print(f"❌ 管理员统计API失败: {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ 管理员统计API异常: {e}")
            return False
    
    async def test_user_management(self):
        """测试用户管理功能"""
        print("\n3️⃣ 测试用户管理功能")
        print("-" * 30)
        
        if not self.admin_token:
            print("❌ 无管理员Token，跳过测试")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # 测试获取演示用户
            async with self.session.get(
                f"{BASE_URL}/api/v1/users/demo-users",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ 演示用户API响应成功")
                    
                    # 修复：处理包装的响应格式
                    users_data = data.get('users', []) if isinstance(data, dict) else data
                    total_users = data.get('total', len(users_data)) if isinstance(data, dict) else len(data)
                    
                    print(f"   演示用户数量: {total_users}")
                    
                    if users_data:
                        # 测试获取第一个用户的标签
                        demo_user = users_data[0]
                        demo_user_id = demo_user.get('demo_user_id')
                        print(f"   测试用户: {demo_user.get('username')} ({demo_user_id})")
                        
                        async with self.session.get(
                            f"{BASE_URL}/api/v1/users/demo-users/{demo_user_id}/tags",
                            headers=headers
                        ) as tag_resp:
                            if tag_resp.status == 200:
                                tag_data = await tag_resp.json()
                                print(f"✅ 用户标签获取成功，标签数量: {len(tag_data)}")
                                return True
                            else:
                                print(f"❌ 用户标签获取失败: {tag_resp.status}")
                                return False
                    else:
                        print("⚠️ 无演示用户数据")
                        return False
                else:
                    print(f"❌ 演示用户API失败: {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ 用户管理功能异常: {e}")
            return False
    
    async def test_content_management(self):
        """测试内容管理功能"""
        print("\n4️⃣ 测试内容管理功能")
        print("-" * 30)
        
        if not self.admin_token:
            print("❌ 无管理员Token，跳过测试")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # 测试获取文章列表
            async with self.session.get(
                f"{BASE_URL}/api/v1/admin/articles",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ 文章管理API响应成功")
                    
                    # 修复：处理分页响应格式
                    if isinstance(data, dict) and 'items' in data:
                        articles = data['items']
                        total = data.get('total', len(articles))
                        print(f"   文章总数: {total}")
                        print(f"   当前页文章数: {len(articles)}")
                        if articles:
                            article = articles[0]
                            print(f"   示例文章: {article.get('title', 'N/A')[:30]}...")
                            print(f"   文章类型: {article.get('type', 'N/A')}")
                        return True
                    elif isinstance(data, list):
                        print(f"   文章数量: {len(data)}")
                        if data:
                            article = data[0]
                            print(f"   示例文章: {article.get('title', 'N/A')[:30]}...")
                            print(f"   文章类型: {article.get('type', 'N/A')}")
                        return True
                    else:
                        print("⚠️ 文章数据格式异常")
                        print(f"   数据类型: {type(data)}")
                        print(f"   数据内容: {str(data)[:100]}...")
                        return False
                else:
                    print(f"❌ 文章管理API失败: {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ 内容管理功能异常: {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        await self.setup()
        
        results = {
            'admin_login': False,
            'admin_stats': False,
            'user_management': False,
            'content_management': False
        }
        
        try:
            # 执行测试
            results['admin_login'] = await self.test_admin_login()
            results['admin_stats'] = await self.test_admin_stats()
            results['user_management'] = await self.test_user_management()
            results['content_management'] = await self.test_content_management()
            
            # 生成测试报告
            print("\n" + "=" * 50)
            print("📋 测试结果汇总")
            print("=" * 50)
            
            total_tests = len(results)
            passed_tests = sum(results.values())
            
            for test_name, result in results.items():
                status = "✅ 通过" if result else "❌ 失败"
                print(f"{test_name.replace('_', ' ').title()}: {status}")
            
            print(f"\n通过率: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
            
            if passed_tests == total_tests:
                print("\n🎉 所有测试通过！管理员后台修复完成！")
            else:
                print(f"\n⚠️ 有 {total_tests - passed_tests} 个测试失败，需要进一步检查")
                
        finally:
            await self.cleanup()

async def main():
    """主函数"""
    test_suite = AdminTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 