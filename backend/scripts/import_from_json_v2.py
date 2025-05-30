#!/usr/bin/env python3
"""
从JSON文件导入v2版本内容数据到数据库
"""

import asyncio
import sys
import os
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

def extract_tags(data, key, fallback_key=None):
    """提取标签的辅助函数，处理字符串格式的标签"""
    import ast
    tags = data.get(key, [])
    if not tags and fallback_key:
        tags = data.get(fallback_key, [])
    
    # 处理字符串格式的标签（如 "['行业资讯']"）
    if isinstance(tags, str):
        try:
            # 尝试使用ast.literal_eval安全解析
            tags = ast.literal_eval(tags)
        except (ValueError, SyntaxError):
            # 如果解析失败，返回空列表
            tags = []
    
    return tags if isinstance(tags, list) else []

async def import_from_json():
    """从JSON文件导入v2版本内容数据"""
    client = None
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        collection = db.content
        
        # 读取JSON文件
        json_file_path = os.path.join(os.path.dirname(__file__), "shpgx_content_v2_corrected.json")
        
        if not os.path.exists(json_file_path):
            print(f"❌ JSON文件不存在: {json_file_path}")
            return
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        print(f"🚀 开始从JSON文件导入v2版本内容数据... (共{len(raw_data)}篇)")
        
        imported_count = 0
        for article_data in raw_data:
            # 标准化标签
            basic_info_tags = extract_tags(article_data, "基础信息标签")
            energy_type_tags = extract_tags(article_data, "能源品种标签")
            region_tags = extract_tags(article_data, "地域标签") + article_data.get("规范化地域标签", [])
            business_field_tags = extract_tags(article_data, "业务领域/主题标签")
            beneficiary_tags = extract_tags(article_data, "受益主体标签")
            policy_measure_tags = extract_tags(article_data, "关键措施/政策标签")
            importance_tags = extract_tags(article_data, "重要性/影响力标签")
            
            # 确定内容类型
            content_type = "news"  # 默认为行业资讯
            if "政策法规" in basic_info_tags:
                content_type = "policy"
            elif "交易公告" in basic_info_tags:
                content_type = "announcement"
            elif "调价公告" in basic_info_tags:
                content_type = "price"
            
            # 转换为数据库格式
            db_article = {
                "title": article_data["标题"],
                "content": article_data["文章内容"],
                "type": content_type,
                "source": article_data["来源机构"],
                "publish_time": article_data.get("发布时间", article_data.get("发布日期")),
                "link": article_data["链接"],
                "basic_info_tags": basic_info_tags,
                "energy_type_tags": energy_type_tags,
                "region_tags": list(set(region_tags)),  # 去重
                "business_field_tags": business_field_tags,
                "beneficiary_tags": beneficiary_tags,
                "policy_measure_tags": policy_measure_tags,
                "importance_tags": importance_tags,
                "version": "v2",  # 标记为v2版本
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # 检查是否已存在相同标题的文章
            existing = await collection.find_one({"title": db_article["title"]})
            if not existing:
                await collection.insert_one(db_article)
                imported_count += 1
                print(f"✅ 导入文章: {db_article['title'][:50]}...")
            else:
                print(f"⚠️  文章已存在，跳过: {db_article['title'][:50]}...")
        
        # 统计验证
        total_v1 = await collection.count_documents({"version": {"$ne": "v2"}})
        total_v2 = await collection.count_documents({"version": "v2"})
        total_all = await collection.count_documents({})
        
        print(f"\n📊 导入完成统计:")
        print(f"   本次导入: {imported_count} 篇")
        print(f"   v1版本文章: {total_v1} 篇")
        print(f"   v2版本文章: {total_v2} 篇")
        print(f"   总文章数: {total_all} 篇")
        
        # 按类型统计v2版本
        news_count = await collection.count_documents({"version": "v2", "basic_info_tags": "行业资讯"})
        policy_count = await collection.count_documents({"version": "v2", "basic_info_tags": "政策法规"})
        
        print(f"\n📈 v2版本分类统计:")
        print(f"   行业资讯: {news_count} 篇")
        print(f"   政策法规: {policy_count} 篇")
        
        # 验证链接格式
        print(f"\n🔗 验证链接格式:")
        cursor = collection.find({"version": "v2"}, {"title": 1, "link": 1}).limit(3)
        async for doc in cursor:
            title = doc.get('title', '未知')[:40]
            link = doc.get('link', '未知')
            print(f"   {title}... -> {link}")
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    asyncio.run(import_from_json()) 