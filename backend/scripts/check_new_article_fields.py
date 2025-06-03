#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def check_new_article_fields():
    """检查新生成文章的字段结构"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.energy_info
    
    # 检查新生成的文章
    article_id = ObjectId("683e5b09d62d84bf8c0b0a35")
    article = await db.content.find_one({"_id": article_id})
    
    if article:
        print("🔍 新生成文章的字段结构:")
        print(f"字段: {list(article.keys())}")
        print(f"标题字段值 (title): {article.get('title', '缺失')}")
        print(f"中文标题字段值 (标题): {article.get('标题', '缺失')}")
        print(f"内容字段值 (content): {article.get('content', '缺失')[:50]}...")
        print(f"中文内容字段值 (文章内容): {article.get('文章内容', '缺失')[:50] if article.get('文章内容') else '缺失'}...")
        print(f"类型字段值 (type): {article.get('type', '缺失')}")
        print(f"中文类型字段值 (文档类型): {article.get('文档类型', '缺失')}")
    else:
        print("❌ 未找到指定文章")
    
    # 同时检查旧文章的字段结构
    print("\n🔍 对比：旧文章的字段结构:")
    old_article = await db.content.find_one({"标题": {"$exists": True}})
    
    if old_article:
        print(f"旧文章字段: {list(old_article.keys())[:10]}...")  # 只显示前10个
        print(f"标题字段值 (title): {old_article.get('title', '缺失')}")
        print(f"中文标题字段值 (标题): {old_article.get('标题', '缺失')}")
    else:
        print("❌ 未找到旧文章")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_new_article_fields()) 