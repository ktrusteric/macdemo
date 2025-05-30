#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.services.user_service import UserService
from app.models.user import UserCreate

async def create_demo_users():
    print("🧑‍💼 创建演示用户...")
    
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    # 清空现有用户数据
    await db.users.delete_many({})
    await db.user_tags.delete_many({})
    print("已清除现有用户数据")
    
    user_service = UserService(db)
    
    demo_users = [
        {
            'email': 'zhang@shanghai.com', 
            'username': '张工程师', 
            'password': 'demo123', 
            'register_city': '上海', 
            'energy_types': ['天然气'], 
            'user_id': 'user001',
            'description': '天然气市场分析师 - 关注天然气价格与政策'
        },
        {
            'email': 'li@beijing.com', 
            'username': '李经理', 
            'password': 'demo123', 
            'register_city': '北京', 
            'energy_types': ['原油'], 
            'user_id': 'user002',
            'description': '石油贸易专家 - 原油进口与价格分析'
        },
        {
            'email': 'wang@shenzhen.com', 
            'username': '王主任', 
            'password': 'demo123', 
            'register_city': '深圳', 
            'energy_types': ['液化天然气(LNG)'], 
            'user_id': 'user003',
            'description': 'LNG项目经理 - 液化天然气接收站运营'
        },
        {
            'email': 'chen@guangzhou.com', 
            'username': '陈总监', 
            'password': 'demo123', 
            'register_city': '广州', 
            'energy_types': ['管道天然气(PNG)'], 
            'user_id': 'user004',
            'description': '管道天然气运营专家 - 天然气管网建设'
        },
        {
            'email': 'liu@chengdu.com', 
            'username': '刘研究员', 
            'password': 'demo123', 
            'register_city': '成都', 
            'energy_types': ['电力'], 
            'user_id': 'user005',
            'description': '电力系统研究员 - 可再生能源发电'
        }
    ]
    
    created_count = 0
    for user_data in demo_users:
        try:
            user_create = UserCreate(
                email=user_data['email'],
                username=user_data['username'],
                password=user_data['password'],
                register_city=user_data['register_city']
            )
            
            user = await user_service.create_user(user_create, energy_types=user_data['energy_types'])
            
            # 设置demo_user_id
            await db.users.update_one(
                {'id': user.id},
                {'$set': {
                    'demo_user_id': user_data['user_id'],
                    'description': user_data['description']
                }}
            )
            
            await db.user_tags.update_one(
                {'user_id': user.id},
                {'$set': {'demo_user_id': user_data['user_id']}}
            )
            
            created_count += 1
            print(f"✅ 创建用户: {user.username} ({user_data['register_city']}) - {user_data['energy_types']}")
            
        except Exception as e:
            print(f"❌ 创建用户失败 {user_data['email']}: {str(e)}")
    
    await client.close()
    print(f"\n🎉 成功创建 {created_count} 个演示用户！")

if __name__ == "__main__":
    asyncio.run(create_demo_users()) 