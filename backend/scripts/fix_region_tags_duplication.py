#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复地域标签重复问题
统一使用"全国"标签，移除"中国"标签
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def fix_region_tags_in_database():
    """修复数据库中的地域标签重复问题"""
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        content_collection = db["content"]
        user_tags_collection = db["user_tags"]
        
        print("🔧 开始修复地域标签重复问题...")
        
        # 1. 修复文章内容中的地域标签
        print("\n📄 修复文章内容中的地域标签...")
        articles_updated = 0
        
        # 查找所有包含"中国"标签的文章
        articles_cursor = content_collection.find({"region_tags": "中国"})
        async for article in articles_cursor:
            region_tags = article.get("region_tags", [])
            
            # 统一地域标签
            updated_tags = []
            has_national = False
            
            for tag in region_tags:
                if tag == "中国":
                    # 将"中国"替换为"全国"
                    if not has_national:
                        updated_tags.append("全国")
                        has_national = True
                elif tag == "全国":
                    # 保留"全国"标签
                    if not has_national:
                        updated_tags.append("全国")
                        has_national = True
                else:
                    # 保留其他地域标签
                    updated_tags.append(tag)
            
            # 更新文章
            if updated_tags != region_tags:
                await content_collection.update_one(
                    {"_id": article["_id"]},
                    {"$set": {"region_tags": updated_tags}}
                )
                articles_updated += 1
                print(f"  ✅ 文章: {article.get('title', '')[:30]}... -> 标签: {updated_tags}")
        
        print(f"\n📊 文章地域标签修复完成: {articles_updated} 篇文章已更新")
        
        # 2. 修复用户标签中的地域标签
        print("\n👥 修复用户标签中的地域标签...")
        users_updated = 0
        
        # 查找所有包含"中国"标签的用户
        user_tags_cursor = user_tags_collection.find({"tags.name": "中国"})
        async for user_tags in user_tags_cursor:
            tags = user_tags.get("tags", [])
            updated_tags = []
            has_national = False
            
            for tag in tags:
                if tag.get("name") == "中国" and tag.get("category") == "region":
                    # 将"中国"标签替换为"全国"
                    if not has_national:
                        tag["name"] = "全国"
                        updated_tags.append(tag)
                        has_national = True
                elif tag.get("name") == "全国" and tag.get("category") == "region":
                    # 保留"全国"标签
                    if not has_national:
                        updated_tags.append(tag)
                        has_national = True
                else:
                    # 保留其他标签
                    updated_tags.append(tag)
            
            # 更新用户标签
            if len(updated_tags) != len(tags):
                await user_tags_collection.update_one(
                    {"_id": user_tags["_id"]},
                    {"$set": {"tags": updated_tags}}
                )
                users_updated += 1
                print(f"  ✅ 用户: {user_tags.get('user_id')} -> 地域标签已去重")
        
        print(f"\n📊 用户地域标签修复完成: {users_updated} 个用户已更新")
        
        # 3. 验证修复结果
        print("\n🔍 验证修复结果...")
        
        # 检查是否还有"中国"标签
        china_articles_count = await content_collection.count_documents({"region_tags": "中国"})
        china_users_count = await user_tags_collection.count_documents({"tags.name": "中国"})
        
        national_articles_count = await content_collection.count_documents({"region_tags": "全国"})
        national_users_count = await user_tags_collection.count_documents({"tags.name": "全国"})
        
        print(f"  📄 包含'中国'标签的文章: {china_articles_count} 篇")
        print(f"  👥 包含'中国'标签的用户: {china_users_count} 个")
        print(f"  📄 包含'全国'标签的文章: {national_articles_count} 篇")
        print(f"  👥 包含'全国'标签的用户: {national_users_count} 个")
        
        if china_articles_count == 0 and china_users_count == 0:
            print("\n✅ 地域标签重复问题修复成功！所有'中国'标签已统一为'全国'")
        else:
            print("\n⚠️  仍有部分'中国'标签未处理，请检查数据")
        
        client.close()
        
    except Exception as e:
        print(f"❌ 修复过程出错: {str(e)}")
        raise

def fix_json_data_files():
    """修复JSON数据文件中的地域标签重复问题"""
    print("\n📂 修复JSON数据文件中的地域标签...")
    
    data_files = [
        "scripts/能源信息服务系统_清理重复字段_51篇.json"
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            print(f"\n处理文件: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            updated_count = 0
            
            for article in data:
                if "规范化地域标签" in article:
                    region_tags = article["规范化地域标签"]
                    
                    # 统一地域标签
                    updated_tags = []
                    has_national = False
                    
                    for tag in region_tags:
                        if tag == "中国":
                            # 将"中国"替换为"全国"
                            if not has_national:
                                updated_tags.append("全国")
                                has_national = True
                        elif tag == "全国":
                            # 保留"全国"标签
                            if not has_national:
                                updated_tags.append("全国")
                                has_national = True
                        else:
                            # 保留其他地域标签
                            updated_tags.append(tag)
                    
                    # 更新标签
                    if updated_tags != region_tags:
                        article["规范化地域标签"] = updated_tags
                        updated_count += 1
            
            # 保存修复后的文件
            if updated_count > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"  ✅ 已更新 {updated_count} 篇文章的地域标签")
            else:
                print(f"  ℹ️  文件中没有发现重复的地域标签")
        else:
            print(f"  ⚠️  文件不存在: {file_path}")

async def main():
    """主执行函数"""
    print("🔧 地域标签重复问题修复工具")
    print("=" * 50)
    
    # 1. 修复JSON数据文件
    fix_json_data_files()
    
    # 2. 修复数据库
    await fix_region_tags_in_database()
    
    print("\n🎉 地域标签重复问题修复完成！")
    print("统一使用'全国'标签，已移除所有'中国'重复标签")

if __name__ == "__main__":
    asyncio.run(main()) 