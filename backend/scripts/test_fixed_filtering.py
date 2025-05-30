#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings

async def test_filtering():
    settings = Settings()
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    collection = db.content
    
    print('🧪 测试修复后的筛选逻辑')
    print('=' * 50)
    
    # 获取所有文档
    all_docs = []
    async for doc in collection.find({}):
        all_docs.append(doc)
    
    print(f'📊 总文档数: {len(all_docs)}')
    
    # 测试行情筛选
    market_docs = [
        doc for doc in all_docs 
        if (doc.get('basic_info_tags', []) and '行业资讯' in doc.get('basic_info_tags', [])) or 
           doc.get('type') == 'news'
    ]
    print(f'📈 行情动态: {len(market_docs)}篇')
    
    # 测试政策筛选
    policy_docs = [
        doc for doc in all_docs 
        if (doc.get('basic_info_tags', []) and '政策法规' in doc.get('basic_info_tags', [])) or 
           doc.get('type') == 'policy'
    ]
    print(f'📋 政策法规: {len(policy_docs)}篇')
    
    # 测试交易公告筛选
    trade_docs = [
        doc for doc in all_docs 
        if (doc.get('basic_info_tags', []) and '交易公告' in doc.get('basic_info_tags', [])) or 
           doc.get('type') == 'announcement'
    ]
    print(f'📊 交易公告: {len(trade_docs)}篇')
    
    # 测试调价公告筛选
    price_docs = [
        doc for doc in all_docs 
        if (doc.get('basic_info_tags', []) and '调价公告' in doc.get('basic_info_tags', [])) or 
           doc.get('type') == 'price'
    ]
    print(f'💰 调价公告: {len(price_docs)}篇')
    
    # 测试总公告筛选
    announcement_docs = [
        doc for doc in all_docs 
        if (doc.get('basic_info_tags', []) and ('交易公告' in doc.get('basic_info_tags', []) or '调价公告' in doc.get('basic_info_tags', []))) or 
           doc.get('type') in ['announcement', 'price']
    ]
    print(f'📢 总公告数: {len(announcement_docs)}篇')
    
    print('\n🔍 详细分析:')
    print(f'  行情 + 政策 + 公告 = {len(market_docs)} + {len(policy_docs)} + {len(announcement_docs)} = {len(market_docs) + len(policy_docs) + len(announcement_docs)}')
    print(f'  总文档数: {len(all_docs)}')
    
    if len(market_docs) + len(policy_docs) + len(announcement_docs) == len(all_docs):
        print('✅ 分类完整，无遗漏')
    else:
        print('⚠️ 分类不完整，存在遗漏')
        
        # 找出未分类的文档
        classified_ids = set()
        for doc in market_docs + policy_docs + announcement_docs:
            classified_ids.add(str(doc['_id']))
        
        unclassified = [doc for doc in all_docs if str(doc['_id']) not in classified_ids]
        print(f'未分类文档: {len(unclassified)}篇')
        for doc in unclassified:
            print(f'  - {doc.get("title", "无标题")[:50]}... (type: {doc.get("type")}, tags: {doc.get("basic_info_tags", [])})')

if __name__ == '__main__':
    asyncio.run(test_filtering()) 