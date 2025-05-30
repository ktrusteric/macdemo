#!/usr/bin/env python3
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.core.config import settings

async def clear_announcements():
    client = None
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        
        # 删除现有的交易公告和调价公告
        trade_result = await db.content.delete_many({'basic_info_tags': '交易公告'})
        price_result = await db.content.delete_many({'basic_info_tags': '调价公告'})
        
        print(f'已删除 {trade_result.deleted_count} 篇交易公告')
        print(f'已删除 {price_result.deleted_count} 篇调价公告')
        
    except Exception as e:
        print(f'错误: {e}')
    finally:
        if client:
            await client.close()

if __name__ == "__main__":
    asyncio.run(clear_announcements()) 