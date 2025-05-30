#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings

async def check_data():
    settings = Settings()
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    collection = db.content
    
    print(f'🔍 连接数据库: {settings.MONGODB_URL}')
    print(f'🗄️ 数据库名: {settings.DATABASE_NAME}')
    
    total_count = await collection.count_documents({})
    print(f'总文档数: {total_count}')
    
    if total_count == 0:
        print('❌ 数据库为空')
        return
    
    # 按type字段统计
    type_stats = {}
    basic_info_stats = {}
    
    print('\n📚 遍历所有文档...')
    count = 0
    async for doc in collection.find({}):
        count += 1
        content_type = doc.get('type')
        basic_info_tags = doc.get('basic_info_tags', [])
        title = doc.get('title', '')
        
        print(f'文档 {count}: {title[:50]}...')
        print(f'  type: {content_type}')
        print(f'  basic_info_tags: {basic_info_tags}')
        
        # 按type统计
        if content_type:
            if content_type not in type_stats:
                type_stats[content_type] = []
            type_stats[content_type].append(title)
        
        # 按basic_info_tags统计
        for tag in basic_info_tags:
            if tag not in basic_info_stats:
                basic_info_stats[tag] = []
            basic_info_stats[tag].append(title)
        
        if count >= 5:  # 只看前5条
            break
    
    print(f'\n=== 按type字段统计 ===')
    for t, titles in type_stats.items():
        print(f'{t}: {len(titles)}篇')
    
    print(f'\n=== 按basic_info_tags统计 ===')
    for tag, titles in basic_info_stats.items():
        print(f'{tag}: {len(titles)}篇')

if __name__ == '__main__':
    asyncio.run(check_data()) 