#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient

def check_admin_stats():
    """检查管理员统计数据"""
    client = MongoClient('mongodb://localhost:27017')
    db = client.energy_info
    content_collection = db.content
    users_collection = db.users
    
    print("=== 管理员统计数据检查 ===")
    
    # 检查文章总数
    total_articles = content_collection.count_documents({})
    print(f"📄 总文章数: {total_articles}")
    
    # 检查type字段分布
    print("\n📊 文章类型分布:")
    pipeline = [{"$group": {"_id": "$type", "count": {"$sum": 1}}}]
    type_stats = {}
    for doc in content_collection.aggregate(pipeline):
        type_name = doc["_id"]
        count = doc["count"]
        type_stats[type_name] = count
        print(f"  {type_name}: {count}")
    
    # 检查basic_info_tags分布
    print("\n🏷️ 基础信息标签分布:")
    pipeline = [
        {"$unwind": "$basic_info_tags"},
        {"$group": {"_id": "$basic_info_tags", "count": {"$sum": 1}}}
    ]
    for doc in content_collection.aggregate(pipeline):
        tag_name = doc["_id"]
        count = doc["count"]
        print(f"  {tag_name}: {count}")
    
    # 检查用户统计
    print("\n👥 用户统计:")
    total_users = users_collection.count_documents({})
    admin_users = users_collection.count_documents({"role": "admin"})
    regular_users = total_users - admin_users
    
    print(f"  总用户数: {total_users}")
    print(f"  管理员数: {admin_users}")
    print(f"  普通用户数: {regular_users}")
    
    # 构建统计结果
    stats = {
        "articles": {
            "total": total_articles,
            "by_type": type_stats
        },
        "users": {
            "total": total_users,
            "admins": admin_users,
            "regular": regular_users
        }
    }
    
    print(f"\n✅ 统计数据构建完成:")
    print(f"  文章总数: {stats['articles']['total']}")
    print(f"  用户总数: {stats['users']['total']}")
    
    return stats

if __name__ == "__main__":
    check_admin_stats() 