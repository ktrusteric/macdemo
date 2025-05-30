#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings

async def full_analysis():
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
    
    # 分类统计
    type_stats = {}
    basic_info_stats = {}
    content_types = set()
    
    async for doc in collection.find({}):
        content_type = doc.get('type')
        basic_info_tags = doc.get('basic_info_tags', [])
        title = doc.get('title', '')
        
        # 收集所有type值
        if content_type:
            content_types.add(content_type)
            if content_type not in type_stats:
                type_stats[content_type] = []
            type_stats[content_type].append(title)
        
        # 按basic_info_tags统计
        for tag in basic_info_tags:
            if tag not in basic_info_stats:
                basic_info_stats[tag] = []
            basic_info_stats[tag].append(title)
    
    print(f'\n📊 按type字段统计（完整）:')
    for t in sorted(type_stats.keys()):
        print(f'  {t}: {len(type_stats[t])}篇')
    
    print(f'\n🏷️ 按basic_info_tags统计（完整）:')
    for tag in sorted(basic_info_stats.keys()):
        print(f'  {tag}: {len(basic_info_stats[tag])}篇')
    
    print(f'\n🎯 内容集市分类对应关系:')
    print(f'  行情动态 (market): {basic_info_stats.get("行业资讯", 0)}篇')
    print(f'  政策法规 (policy): {basic_info_stats.get("政策法规", 0)}篇') 
    print(f'  交易公告 (trade): {basic_info_stats.get("交易公告", 0)}篇')
    print(f'  调价公告 (price): {basic_info_stats.get("调价公告", 0)}篇')
    print(f'  总公告数 (announcement): {basic_info_stats.get("交易公告", 0) + basic_info_stats.get("调价公告", 0)}篇')
    
    print(f'\n🔧 前端筛选需要匹配的标签:')
    print(f'  行情筛选: 需要匹配包含"行情"或"行业资讯"的basic_info_tags')
    print(f'  政策筛选: 需要匹配包含"政策"或"政策法规"的basic_info_tags')
    print(f'  公告筛选: 需要匹配包含"公告"、"交易公告"或"调价公告"的basic_info_tags')

if __name__ == '__main__':
    asyncio.run(full_analysis()) 