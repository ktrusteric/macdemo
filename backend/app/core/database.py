from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from app.core.config import settings

class DatabaseManager:
    client: AsyncIOMotorClient = None
    database: Database = None

db_manager = DatabaseManager()

async def connect_to_mongo():
    """连接到MongoDB"""
    try:
        db_manager.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=10,
            minPoolSize=10,
        )
        db_manager.database = db_manager.client[settings.DATABASE_NAME]
        
        # 测试连接
        await db_manager.client.admin.command('ping')
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    """关闭MongoDB连接"""
    if db_manager.client:
        db_manager.client.close()
        print("MongoDB connection closed")

def get_database():
    """获取数据库实例（同步版本）"""
    return db_manager.database

async def get_database_async():
    """获取数据库实例（异步版本）"""
    return db_manager.database 