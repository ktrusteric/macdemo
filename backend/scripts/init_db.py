import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import UserRole
import uuid
from datetime import datetime

async def init_database():
    """初始化数据库，创建测试用户"""
    try:
        # 连接数据库
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        
        # 检查用户是否已存在
        existing_user = await db.users.find_one({"email": "cooper.liu@k-trust.cn"})
        if existing_user:
            print("用户 cooper.liu@k-trust.cn 已存在")
            return
        
        # 创建测试用户
        test_user = {
            "id": str(uuid.uuid4()),
            "email": "cooper.liu@k-trust.cn",
            "username": "Cooper Liu",
            "hashed_password": get_password_hash("123456"),  # 默认密码
            "role": UserRole.PAID,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "has_initial_tags": True
        }
        
        # 插入用户
        await db.users.insert_one(test_user)
        print(f"成功创建测试用户: {test_user['email']}")
        print(f"默认密码: 123456")
        
        # 为用户创建一些示例标签
        user_tags = {
            "user_id": test_user["id"],
            "tags": [
                {
                    "category": "region",
                    "name": "华东地区",
                    "weight": 1.0,
                    "source": "preset",
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "category": "energy_type",
                    "name": "天然气",
                    "weight": 1.0,
                    "source": "preset",
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "category": "energy_type",
                    "name": "LNG",
                    "weight": 0.8,
                    "source": "preset",
                    "created_at": datetime.utcnow().isoformat()
                }
            ],
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await db.user_tags.insert_one(user_tags)
        print("成功创建用户标签")
        
        # 关闭连接
        client.close()
        print("数据库初始化完成")
        
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(init_database())