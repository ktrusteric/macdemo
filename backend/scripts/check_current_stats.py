#!/usr/bin/env python3
"""
检查当前数据库的内容统计
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def check_content_stats():
    """检查当前数据库的内容统计"""
    client = None
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        collection = db.content
        
        print('📊 当前数据库内容统计:')
        
        # 总数统计
        total = await collection.count_documents({})
        print(f'   总文章数: {total} 篇')
        
        # 按版本统计
        v1_count = await collection.count_documents({"version": "v1"})
        v2_count = await collection.count_documents({"version": "v2"})
        print(f'   v1版本: {v1_count} 篇')
        print(f'   v2版本: {v2_count} 篇')
        
        # 按基础信息标签统计
        print('\n📈 按基础信息标签统计:')
        tags = ['行业资讯', '政策法规', '交易公告', '调价公告']
        for tag in tags:
            count = await collection.count_documents({'basic_info_tags': tag})
            print(f'   {tag}: {count} 篇')
        
        # 查看交易公告的具体内容
        print('\n📋 交易公告详情:')
        announcements = await collection.find({'basic_info_tags': '交易公告'}).to_list(length=None)
        for i, ann in enumerate(announcements):
            print(f'   {i+1}. {ann["title"][:60]}... (版本: {ann.get("version", "未知")})')
        
        # 查看调价公告的具体内容
        print('\n💰 调价公告详情:')
        price_announcements = await collection.find({'basic_info_tags': '调价公告'}).to_list(length=None)
        for i, ann in enumerate(price_announcements):
            print(f'   {i+1}. {ann["title"][:60]}... (版本: {ann.get("version", "未知")})')
        
        print(f'\n✅ 统计完成')
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    asyncio.run(check_content_stats()) 