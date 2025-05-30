#!/usr/bin/env python3
"""
验证内容类型分类是否正确
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def validate_content_types():
    """验证内容类型分类"""
    client = None
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        collection = db.content
        
        print('🔍 验证内容类型分类...')
        
        # 获取所有文章
        all_articles = await collection.find({}).to_list(length=None)
        
        type_stats = {
            "news": 0,      # 行业资讯
            "policy": 0,    # 政策法规  
            "announcement": 0,  # 交易公告
            "price": 0      # 调价公告
        }
        
        basic_info_stats = {
            "行业资讯": 0,
            "政策法规": 0,
            "交易公告": 0,
            "调价公告": 0
        }
        
        inconsistencies = []
        
        for article in all_articles:
            article_type = article.get("type", "unknown")
            basic_info_tags = article.get("basic_info_tags", [])
            title = article.get("title", "")
            
            # 统计type字段
            if article_type in type_stats:
                type_stats[article_type] += 1
            
            # 统计basic_info_tags
            for tag in basic_info_tags:
                if tag in basic_info_stats:
                    basic_info_stats[tag] += 1
            
            # 检查一致性
            expected_type = None
            if "政策法规" in basic_info_tags:
                expected_type = "policy"
            elif "交易公告" in basic_info_tags:
                expected_type = "announcement"
            elif "调价公告" in basic_info_tags:
                expected_type = "price"
            elif "行业资讯" in basic_info_tags:
                expected_type = "news"
            
            if expected_type and article_type != expected_type:
                inconsistencies.append({
                    "title": title[:60] + "...",
                    "actual_type": article_type,
                    "expected_type": expected_type,
                    "basic_info_tags": basic_info_tags
                })
        
        print("\n📊 Type字段统计:")
        for t, count in type_stats.items():
            print(f"   {t}: {count} 篇")
        
        print("\n🏷️ Basic_info_tags统计:")
        for tag, count in basic_info_stats.items():
            print(f"   {tag}: {count} 篇")
        
        if inconsistencies:
            print(f"\n⚠️ 发现 {len(inconsistencies)} 个分类不一致的文章:")
            for inc in inconsistencies[:10]:  # 只显示前10个
                print(f"   • {inc['title']}")
                print(f"     实际type: {inc['actual_type']}, 期望type: {inc['expected_type']}")
                print(f"     基础标签: {inc['basic_info_tags']}")
        else:
            print("\n✅ 所有文章的类型分类都是一致的")
        
        # 特别检查交易公告
        print(f"\n📋 交易公告详细检查:")
        announcements = await collection.find({"basic_info_tags": "交易公告"}).to_list(length=None)
        for i, ann in enumerate(announcements):
            print(f"   {i+1}. {ann['title'][:60]}...")
            print(f"      Type: {ann.get('type', '未设置')}")
            print(f"      Basic tags: {ann.get('basic_info_tags', [])}")
            print(f"      Version: {ann.get('version', '未知')}")
            print()
        
        print(f'✅ 验证完成，总共 {len(all_articles)} 篇文章')
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    asyncio.run(validate_content_types()) 