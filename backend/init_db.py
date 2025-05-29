#!/usr/bin/env python3
"""
数据库初始化脚本
创建测试用户和基础数据
"""

import asyncio
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import UserRole, TagCategory, UserTag
import uuid

async def init_database():
    """初始化数据库"""
    print("正在连接到数据库...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    try:
        # 测试连接
        await client.admin.command('ping')
        print("数据库连接成功!")
        
        # 创建测试用户
        await create_test_users(db)
        
        # 创建示例标签数据
        await create_sample_tags(db)
        
        print("数据库初始化完成!")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise e
    finally:
        client.close()

async def create_test_users(db):
    """创建测试用户"""
    users_collection = db.users
    user_tags_collection = db.user_tags
    
    test_users = [
        {
            "id": str(uuid.uuid4()),
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": get_password_hash("testpass"),
            "role": UserRole.FREE,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "has_initial_tags": True
        },
        {
            "id": str(uuid.uuid4()),
            "email": "admin@example.com", 
            "username": "admin",
            "hashed_password": get_password_hash("adminpass"),
            "role": UserRole.ADMIN,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "has_initial_tags": True
        }
    ]
    
    for user in test_users:
        # 检查用户是否已存在
        existing = await users_collection.find_one({"email": user["email"]})
        if not existing:
            await users_collection.insert_one(user)
            print(f"创建用户: {user['email']}")
            
            # 为用户创建默认标签
            await create_user_default_tags(user_tags_collection, user["id"])
        else:
            print(f"用户已存在: {user['email']}")

async def create_user_default_tags(user_tags_collection, user_id):
    """为用户创建默认标签"""
    default_tags = [
        UserTag(
            category=TagCategory.REGION,
            name="华东地区",
            weight=1.0,
            source="preset"
        ),
        UserTag(
            category=TagCategory.ENERGY_TYPE,
            name="天然气",
            weight=1.0,
            source="preset"
        ),
        UserTag(
            category=TagCategory.ENERGY_TYPE,
            name="LNG",
            weight=0.8,
            source="preset"
        ),
        UserTag(
            category=TagCategory.BUSINESS_FIELD,
            name="市场动态",
            weight=1.0,
            source="preset"
        )
    ]
    
    user_tags_doc = {
        "user_id": user_id,
        "tags": [tag.dict() for tag in default_tags],
        "updated_at": datetime.utcnow()
    }
    
    await user_tags_collection.replace_one(
        {"user_id": user_id},
        user_tags_doc,
        upsert=True
    )

async def create_sample_tags(db):
    """创建示例标签库"""
    tag_library_collection = db.tag_library
    
    sample_tags = [
        # 地域标签
        {"category": "region", "name": "华东地区", "description": "包括上海、江苏、浙江、安徽等"},
        {"category": "region", "name": "华南地区", "description": "包括广东、广西、海南等"},
        {"category": "region", "name": "华北地区", "description": "包括北京、天津、河北、山西等"},
        {"category": "region", "name": "西南地区", "description": "包括四川、重庆、云南、贵州等"},
        {"category": "region", "name": "全国", "description": "全国范围"},
        {"category": "region", "name": "国际", "description": "国际市场"},
        
        # 能源品种标签
        {"category": "energy_type", "name": "天然气", "description": "天然气相关"},
        {"category": "energy_type", "name": "LNG", "description": "液化天然气"},
        {"category": "energy_type", "name": "管道气", "description": "管道天然气"},
        {"category": "energy_type", "name": "PNG", "description": "压缩天然气"},
        {"category": "energy_type", "name": "重烃", "description": "重烃类"},
        {"category": "energy_type", "name": "原油", "description": "原油相关"},
        {"category": "energy_type", "name": "成品油", "description": "成品油"},
        {"category": "energy_type", "name": "煤炭", "description": "煤炭相关"},
        {"category": "energy_type", "name": "电力", "description": "电力相关"},
        
        # 业务领域标签
        {"category": "business_field", "name": "市场动态", "description": "市场动态信息"},
        {"category": "business_field", "name": "价格变化", "description": "价格变化信息"},
        {"category": "business_field", "name": "交易信息", "description": "交易相关信息"},
        {"category": "business_field", "name": "科技创新", "description": "科技创新动态"},
        {"category": "business_field", "name": "政策解读", "description": "政策解读分析"},
        {"category": "business_field", "name": "国际合作", "description": "国际合作信息"},
        {"category": "business_field", "name": "投资支持", "description": "投资支持政策"},
    ]
    
    for tag in sample_tags:
        tag_doc = {
            "category": tag["category"],
            "name": tag["name"],
            "description": tag["description"],
            "usage_count": 0,
            "is_active": True
        }
        
        existing = await tag_library_collection.find_one({
            "category": tag["category"],
            "name": tag["name"]
        })
        
        if not existing:
            await tag_library_collection.insert_one(tag_doc)
            print(f"创建标签: {tag['category']} - {tag['name']}")

if __name__ == "__main__":
    asyncio.run(init_database()) 