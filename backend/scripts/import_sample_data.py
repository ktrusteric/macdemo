import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.content import Content, ContentType, ContentTag
from app.models.user import User, UserRole, UserCreate, TagCategory, TagSource
from app.services.user_service import UserService
from passlib.context import CryptContext
from typing import List

# 内容类型映射
CONTENT_TYPE_MAP = {
    "政策法规": ContentType.POLICY,
    "行业资讯": ContentType.NEWS,
    "调价公告": ContentType.PRICE,
    "交易公告": ContentType.ANNOUNCEMENT
}

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def import_articles():
    """导入示例文章数据"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    content_collection = db.content
    
    # 清除现有数据
    await content_collection.delete_many({})
    print("Cleared existing content data")
    
    # 读取JSON文件
    json_file_path = os.path.join(os.path.dirname(__file__), "信息发布文章与标签.json")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        articles_data = json.load(f)
    
    # 导入文章
    imported_count = 0
    for article_data in articles_data:
        try:
            # 转换文章类型
            content_type = CONTENT_TYPE_MAP.get(article_data.get("类型", ""), ContentType.NEWS)
            
            # 处理标签
            content_tags = []
            if "标签" in article_data and article_data["标签"]:
                for tag_name in article_data["标签"]:
                    if isinstance(tag_name, str):
                        content_tags.append(ContentTag(category="general", name=tag_name))
            
            # 创建内容对象
            content = Content(
                title=article_data.get("标题", ""),
                content=article_data.get("内容", ""),
                type=content_type,
                source=article_data.get("来源", "官方发布"),
                tags=content_tags,
                publish_time=datetime.now()
            )
            
            await content_collection.insert_one(content.dict())
            imported_count += 1
            print(f"Imported: {content.title[:50]}...")
            
        except Exception as e:
            print(f"Error importing article: {str(e)}")
            continue
    
    print(f"\nTotal articles imported: {imported_count}")
    client.close()

async def create_sample_users():
    """创建示例用户数据（包含完整账户信息和正确的能源类型标签）"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    users_collection = db.users
    user_tags_collection = db.user_tags
    
    # 清空现有数据
    await users_collection.delete_many({})
    await user_tags_collection.delete_many({})
    print("Cleared existing user data")
    
    # 创建UserService实例
    user_service = UserService(db)
    
    # 预设的5个演示用户 - 使用正确的能源类型 (与前端energyTypes对应)
    demo_users = [
        {
            "email": "zhang@newenergy.com",
            "username": "张先生",
            "password": "demo123",
            "register_city": "上海",
            "energy_types": ["电力", "生物柴油", "天然气"],  # 新能源投资者
            "user_id": "user001",
            "description": "新能源投资者 - 关注太阳能、风能项目"
        },
        {
            "email": "li@traditional.com", 
            "username": "李女士",
            "password": "demo123",
            "register_city": "北京",
            "energy_types": ["原油", "天然气", "液化天然气(LNG)", "煤炭"],  # 传统能源
            "user_id": "user002",
            "description": "传统能源企业主 - 石油、天然气行业专家"
        },
        {
            "email": "wang@carbon.com",
            "username": "王先生", 
            "password": "demo123",
            "register_city": "深圳",
            "energy_types": ["电力", "生物柴油", "天然气"],  # 节能减排
            "user_id": "user003",
            "description": "节能减排顾问 - 专注碳中和、环保政策"
        },
        {
            "email": "chen@power.com",
            "username": "陈女士",
            "password": "demo123", 
            "register_city": "广州",
            "energy_types": ["电力", "煤炭", "天然气"],  # 电力系统
            "user_id": "user004",
            "description": "电力系统工程师 - 电网、储能技术专家"
        },
        {
            "email": "liu@policy.com",
            "username": "刘先生",
            "password": "demo123",
            "register_city": "成都",
            "energy_types": ["原油", "天然气", "电力", "煤炭"],  # 政策研究
            "user_id": "user005", 
            "description": "能源政策研究员 - 政策法规、市场分析"
        }
    ]
    
    created_count = 0
    for user_data in demo_users:
        try:
            # 创建用户对象
            user_create = UserCreate(
                email=user_data["email"],
                username=user_data["username"],
                password=user_data["password"],
                register_city=user_data["register_city"]
            )
            
            # 创建用户（包含三层地区标签）
            user = await user_service.create_user(
                user_create, 
                energy_types=user_data["energy_types"]
            )
            
            # 手动设置用户ID为预设值，确保与前端一致
            await users_collection.update_one(
                {"id": user.id},
                {"$set": {"demo_user_id": user_data["user_id"], "description": user_data["description"]}}
            )
            
            # 更新用户标签集合中的用户ID引用
            await user_tags_collection.update_one(
                {"user_id": user.id},
                {"$set": {"demo_user_id": user_data["user_id"]}}
            )
            
            created_count += 1
            print(f"Created demo user: {user.username} ({user.email}) - {user_data['register_city']}")
            print(f"  Demo ID: {user_data['user_id']}")
            print(f"  Description: {user_data['description']}")
            
            # 显示生成的标签信息
            user_tags = await user_service.get_user_tags(user.id)
            if user_tags:
                print(f"  Generated tags:")
                for tag in user_tags.tags:
                    print(f"    - {tag.category}: {tag.name} (权重: {tag.weight}, 来源: {tag.source})")
            print("")
            
        except Exception as e:
            print(f"Error creating user {user_data['email']}: {str(e)}")
    
    print(f"Total demo users created: {created_count}")
    
    client.close()

async def main():
    """主函数"""
    print("Starting data import...")
    
    # 导入文章数据
    print("\n1. Importing articles...")
    await import_articles()
    
    # 创建示例用户
    print("\n2. Creating sample users...")
    await create_sample_users()
    
    print("\nData import completed!")

if __name__ == "__main__":
    asyncio.run(main()) 