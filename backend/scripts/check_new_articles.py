#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient

async def check_new_articles():
    """检查最新生成的文章"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.energy_info
    
    # 获取最新4篇文章
    articles = await db.content.find({}).sort([('created_at', -1)]).limit(4).to_list(4)
    
    print("🔍 最新4篇文章:")
    for i, article in enumerate(articles):
        print(f"{i+1}. {article.get('title', '无标题')}")
        print(f"   类型: {article.get('type')} | ID: {article['_id']}")
        print(f"   地区标签: {article.get('region_tags', [])}")
        print(f"   能源标签: {article.get('energy_type_tags', [])}")
        print(f"   发布时间: {article.get('publish_time', 'N/A')}")
        print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_new_articles()) 