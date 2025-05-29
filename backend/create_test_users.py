#!/usr/bin/env python3
"""
初始化测试用户脚本
创建两个测试用户，分别注册在上海和长沙，自动生成地理标签
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import connect_to_mongo, get_database
from app.services.user_service import UserService
from app.models.user import UserCreate

async def create_test_users():
    """创建测试用户并初始化标签"""
    print("🚀 开始创建测试用户...")
    
    try:
        # 连接数据库
        await connect_to_mongo()
        db = await get_database()
        user_service = UserService(db)
        
        # 测试用户数据
        test_users = [
            {
                "data": UserCreate(
                    email="shanghai_user@test.com",
                    username="shanghai_user",
                    password="test123456",
                    register_city="上海"
                ),
                "energy_types": ["天然气", "电力", "汽油"],
                "description": "上海测试用户"
            },
            {
                "data": UserCreate(
                    email="changsha_user@test.com", 
                    username="changsha_user",
                    password="test123456",
                    register_city="长沙"
                ),
                "energy_types": ["天然气", "电力", "煤炭"],
                "description": "长沙测试用户"
            }
        ]
        
        created_users = []
        
        for user_info in test_users:
            try:
                print(f"\n📝 创建 {user_info['description']}...")
                
                # 检查用户是否已存在
                existing_user = await user_service.users_collection.find_one({
                    "email": user_info["data"].email
                })
                
                if existing_user:
                    print(f"⚠️  用户 {user_info['data'].email} 已存在，跳过创建")
                    
                    # 获取现有用户的标签
                    user_tags = await user_service.get_user_tags(existing_user["id"])
                    if user_tags:
                        print(f"📋 现有标签数量: {len(user_tags.tags)}")
                        for tag in user_tags.tags:
                            print(f"   - {tag.category}: {tag.name} (权重: {tag.weight})")
                    continue
                
                # 创建新用户
                user = await user_service.create_user(
                    user_info["data"], 
                    user_info["energy_types"]
                )
                
                print(f"✅ 用户创建成功:")
                print(f"   - 用户ID: {user.id}")
                print(f"   - 邮箱: {user.email}")
                print(f"   - 用户名: {user.username}")
                print(f"   - 注册城市: {user.register_city}")
                
                # 获取用户标签
                user_tags = await user_service.get_user_tags(user.id)
                if user_tags:
                    print(f"🏷️  自动生成标签 ({len(user_tags.tags)} 个):")
                    for tag in user_tags.tags:
                        print(f"   - {tag.category}: {tag.name} (权重: {tag.weight}, 来源: {tag.source})")
                
                # 获取用户区域信息
                region_info = await user_service.get_user_region_info(user.id)
                print(f"🗺️  区域信息:")
                print(f"   - 城市: {region_info.get('city')}")
                print(f"   - 省份: {region_info.get('province')}")
                print(f"   - 区域: {region_info.get('region')}")
                
                created_users.append(user)
                
            except ValueError as e:
                print(f"❌ 创建用户失败: {e}")
            except Exception as e:
                print(f"💥 意外错误: {e}")
        
        print(f"\n🎉 测试用户创建完成！共成功创建 {len(created_users)} 个用户")
        
        # 显示登录信息
        print(f"\n🔑 登录信息:")
        print(f"上海用户 - 邮箱: shanghai_user@test.com, 密码: test123456")
        print(f"长沙用户 - 邮箱: changsha_user@test.com, 密码: test123456")
        
        return created_users
        
    except Exception as e:
        print(f"💥 系统错误: {e}")
        return []

async def verify_test_users():
    """验证测试用户数据"""
    print("\n🔍 验证测试用户数据...")
    
    try:
        db = await get_database()
        user_service = UserService(db)
        
        test_emails = ["shanghai_user@test.com", "changsha_user@test.com"]
        
        for email in test_emails:
            print(f"\n📊 验证用户: {email}")
            
            # 查找用户
            user_doc = await user_service.users_collection.find_one({"email": email})
            if not user_doc:
                print(f"❌ 用户不存在: {email}")
                continue
            
            print(f"✅ 用户信息:")
            print(f"   - ID: {user_doc['id']}")
            print(f"   - 用户名: {user_doc['username']}")
            print(f"   - 注册城市: {user_doc.get('register_city', '未设置')}")
            print(f"   - 创建时间: {user_doc.get('created_at', '未知')}")
            print(f"   - 标签初始化: {user_doc.get('has_initial_tags', False)}")
            
            # 验证标签
            user_tags = await user_service.get_user_tags(user_doc['id'])
            if user_tags:
                print(f"🏷️  标签验证 ({len(user_tags.tags)} 个):")
                
                # 按分类统计
                category_stats = {}
                for tag in user_tags.tags:
                    if tag.category not in category_stats:
                        category_stats[tag.category] = []
                    category_stats[tag.category].append(tag)
                
                for category, tags in category_stats.items():
                    print(f"   📂 {category} ({len(tags)} 个):")
                    for tag in tags:
                        print(f"      - {tag.name} (权重: {tag.weight}, 来源: {tag.source})")
            else:
                print(f"❌ 用户标签未找到")
                
    except Exception as e:
        print(f"💥 验证失败: {e}")

async def main():
    """主函数"""
    print("🏷️ 测试用户初始化脚本")
    print("=" * 50)
    
    # 创建测试用户
    users = await create_test_users()
    
    # 验证用户数据
    await verify_test_users()
    
    print("\n" + "=" * 50)
    print("✨ 脚本执行完成！")
    print("\n💡 下一步:")
    print("1. 启动前端服务: cd frontend && npm run dev")
    print("2. 访问登录页面: http://localhost:5175/login")
    print("3. 使用上述测试账号登录查看标签")

if __name__ == "__main__":
    asyncio.run(main()) 