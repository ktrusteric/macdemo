#!/usr/bin/env python3
"""
测试修复后的推荐功能和标签处理
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.services.content_service import ContentService
from app.services.recommendation_service import RecommendationService
from app.utils.tag_processor import TagProcessor
from app.utils.region_mapper import RegionMapper
import json

async def test_fixed_functionality():
    """测试修复后的功能"""
    
    print("🔧 测试修复后的推荐功能和标签处理")
    print("="*60)
    
    # 初始化数据库连接
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    # 初始化服务
    content_service = ContentService(db)
    recommendation_service = RecommendationService(db)
    
    try:
        # 测试1：TagProcessor功能测试
        print("\n🏷️ 测试1：TagProcessor功能")
        test_tags = ['["天然气", "上海"]', "['原油']", "液化天然气(LNG)", "天然气,原油"]
        for tag_string in test_tags:
            parsed = TagProcessor.safe_parse_tags(tag_string)
            print(f"   输入: {tag_string} -> 输出: {parsed}")
        
        # 测试2：能源标签验证
        print("\n⚡ 测试2：能源标签验证")
        test_energy_tags = ["天然气", "原油", "无效能源", "电力"]
        validation = TagProcessor.validate_energy_type_tags(test_energy_tags)
        print(f"   有效标签: {validation['valid_tags']}")
        print(f"   无效标签: {validation['invalid_tags']}")
        
        # 测试3：地区映射功能
        print("\n🗺️ 测试3：地区映射功能")
        test_cities = ["上海", "北京", "深圳", "杭州", "无效城市"]
        for city in test_cities:
            province = RegionMapper.get_province_by_city(city)
            region = RegionMapper.get_region_by_city(city)
            print(f"   {city} -> 省份: {province}, 地区: {region}")
        
        # 测试4：内容服务字段映射
        print("\n📄 测试4：内容服务字段映射")
        content_count = await content_service.get_content_count()
        print(f"   数据库中文章总数: {content_count}")
        
        if content_count > 0:
            contents = await content_service.get_content_list(limit=3)
            print(f"   成功获取 {len(contents)} 篇文章样本")
            
            for i, content in enumerate(contents):
                print(f"   文章 {i+1}:")
                print(f"     标题: {content.title}")
                print(f"     类型: {content.type}")
                print(f"     能源标签: {content.energy_type_tags}")
                print(f"     地区标签: {content.region_tags[:3]}...")  # 只显示前3个
        
        # 测试5：推荐功能测试
        print("\n🎯 测试5：推荐功能测试")
        
        # 测试用户推荐 - 使用Demo用户user001 (张工程师)
        test_user_id = "user001"
        print(f"   使用演示用户 {test_user_id} 进行推荐测试...")
        
        try:
            recommendations = await recommendation_service.get_user_recommendations(
                user_id=test_user_id,
                limit=5
            )
            
            if recommendations:
                print(f"   ✅ 成功获取 {len(recommendations)} 条推荐")
                for i, content in enumerate(recommendations):
                    score = getattr(content, 'relevance_score', 0)
                    print(f"   推荐 {i+1}: {content.title[:50]}... (得分: {score:.3f})")
                    print(f"             能源标签: {content.energy_type_tags}")
                    print(f"             地区标签: {content.region_tags[:2]}")
            else:
                print("   ❌ 未获取到推荐内容")
        except Exception as e:
            print(f"   ⚠️ 推荐功能测试失败: {str(e)}")
            print("   尝试获取分层推荐...")
            try:
                tiered_recs = await recommendation_service.get_tiered_recommendations(test_user_id)
                primary_count = len(tiered_recs.get("primary_recommendations", []))
                secondary_count = len(tiered_recs.get("secondary_recommendations", []))
                print(f"   ✅ 分层推荐成功: 主要推荐 {primary_count} 条, 次要推荐 {secondary_count} 条")
            except Exception as e2:
                print(f"   ❌ 分层推荐也失败: {str(e2)}")
        
        # 测试6：标签提取功能
        print("\n🔍 测试6：标签提取功能")
        test_title = "上海天然气价格调整公告：华东地区统一执行新价格标准"
        extracted_tags = TagProcessor.extract_tags_from_content(test_title)
        print(f"   标题: {test_title}")
        print("   提取的标签:")
        for category, tags in extracted_tags.items():
            if tags:
                print(f"     {category}: {tags}")
        
        # 测试7：验证数据兼容性
        print("\n🔄 测试7：数据兼容性验证")
        
        # 查询包含新字段的文章
        pipeline = [
            {"$match": {"title": {"$exists": True}}},
            {"$limit": 5},
            {"$project": {
                "title": 1,
                "has_english_fields": {
                    "$and": [
                        {"$ne": ["$title", None]},
                        {"$ne": ["$content", None]},
                        {"$ne": ["$type", None]}
                    ]
                },
                "has_chinese_fields": {
                    "$and": [
                        {"$ne": ["$标题", None]},
                        {"$ne": ["$文章内容", None]},
                        {"$ne": ["$文档类型", None]}
                    ]
                }
            }}
        ]
        
        field_stats = {"english_fields": 0, "chinese_fields": 0, "mixed_fields": 0}
        async for doc in db.content.aggregate(pipeline):
            if doc.get("has_english_fields") and doc.get("has_chinese_fields"):
                field_stats["mixed_fields"] += 1
            elif doc.get("has_english_fields"):
                field_stats["english_fields"] += 1
            elif doc.get("has_chinese_fields"):
                field_stats["chinese_fields"] += 1
        
        print(f"   字段兼容性统计: {field_stats}")
        
        print("\n✅ 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_fixed_functionality()) 