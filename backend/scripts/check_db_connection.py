#!/usr/bin/env python3
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.shpgx_db
    collections = await db.list_collection_names()
    print('Collections:', collections)
    
    count = await db.content.count_documents({})
    print(f'Content count: {count}')
    
    if count > 0:
        # 查看一条记录
        doc = await db.content.find_one({})
        print('Sample document:')
        print(f"  title: {doc.get('title', 'N/A')}")
        print(f"  type: {doc.get('type', 'N/A')}")
        print(f"  basic_info_tags: {doc.get('basic_info_tags', [])}")

if __name__ == '__main__':
    asyncio.run(check()) 