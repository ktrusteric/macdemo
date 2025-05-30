#!/usr/bin/env python3
"""
测试内容服务API返回的数据
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.content_service import ContentService
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def test_content_api():
    """测试内容服务API"""
    client = None
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        service = ContentService(db)
        
        print("🧪 测试内容服务API...")
        
        # 测试获取所有内容
        all_content = await service.get_content_list(skip=0, limit=100)
        print(f'📊 API返回总内容数: {len(all_content)}')
        
        # 按类型统计
        type_counts = {}
        for content in all_content:
            content_type = content.type
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
        
        print('\n📈 API返回的类型统计:')
        for t, count in type_counts.items():
            print(f'   {t}: {count} 篇')
        
        # 检查交易公告
        announcements = [c for c in all_content if c.type == 'announcement']
        print(f'\n📋 交易公告详情 ({len(announcements)}篇):')
        for i, ann in enumerate(announcements):
            print(f'   {i+1}. {ann.title[:60]}...')
            print(f'      ID: {ann.id}')
            print(f'      Basic tags: {getattr(ann, "basic_info_tags", [])}')
            print()
        
        # 检查调价公告
        price_announcements = [c for c in all_content if c.type == 'price']
        print(f'💰 调价公告详情 ({len(price_announcements)}篇):')
        for i, ann in enumerate(price_announcements):
            print(f'   {i+1}. {ann.title[:60]}...')
            print(f'      ID: {ann.id}')
            print(f'      Basic tags: {getattr(ann, "basic_info_tags", [])}')
            print()
        
        # 测试筛选功能
        print("🔍 测试筛选功能...")
        filtered_announcements = await service.get_content_by_type("announcement", skip=0, limit=10)
        print(f'   按类型筛选交易公告: {len(filtered_announcements)} 篇')
        
        print("\n✅ API测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    asyncio.run(test_content_api()) 