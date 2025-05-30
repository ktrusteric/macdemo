#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings

async def clear_data():
    try:
        settings = Settings()
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        
        print(f'🗑️ 清理数据库: {settings.DATABASE_NAME}')
        
        # 清除content集合
        result = await db.content.delete_many({})
        print(f'✅ 已清除 {result.deleted_count} 条记录')
        
        client.close()
        print('🎉 数据库清理完成')
    except Exception as e:
        print(f'❌ 清理失败: {e}')
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(clear_data()) 