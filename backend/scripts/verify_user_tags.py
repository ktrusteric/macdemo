#!/usr/bin/env python3
"""
验证用户标签配置脚本
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def verify_user_tags():
    """验证用户标签配置"""
    
    print("🔍 验证Demo用户标签配置")
    print("=" * 50)
    
    # 连接数据库
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.energy_info
    users_collection = db.users
    user_tags_collection = db.user_tags
    
    # 获取所有用户
    users = await users_collection.find().to_list(None)
    
    for user in users:
        print(f"\n👤 {user['username']} ({user['register_city']})")
        print(f"   用户ID: {user['id']}")
        print(f"   描述: {user.get('description', '无')}")
        
        # 查找用户标签
        user_tags = await user_tags_collection.find_one({"user_id": user["id"]})
        if user_tags:
            print(f"   标签记录ID: {user_tags['_id']}")
            
            # 按类别分组显示标签
            energy_tags = []
            region_tags = []
            other_tags = []
            
            for tag in user_tags["tags"]:
                if tag["category"] == "energy_type":
                    energy_tags.append(f"{tag['name']} (权重:{tag['weight']})")
                elif tag["category"] in ["city", "province", "region"]:
                    region_tags.append(f"{tag['name']} (权重:{tag['weight']})")
                else:
                    other_tags.append(f"{tag['category']}: {tag['name']} (权重:{tag['weight']})")
            
            print(f"   🔋 能源标签: {energy_tags}")
            print(f"   🗺️ 地域标签: {region_tags}")
            print(f"   📋 其他标签: {len(other_tags)}个")
        else:
            print(f"   ❌ 未找到标签记录")
    
    print(f"\n📊 总结:")
    print(f"   总用户数: {len(users)}")
    
    # 统计能源标签分布
    energy_distribution = {}
    for user in users:
        user_tags = await user_tags_collection.find_one({"user_id": user["id"]})
        if user_tags:
            for tag in user_tags["tags"]:
                if tag["category"] == "energy_type":
                    energy_type = tag["name"]
                    if energy_type not in energy_distribution:
                        energy_distribution[energy_type] = 0
                    energy_distribution[energy_type] += 1
    
    print(f"   能源标签分布:")
    for energy_type, count in energy_distribution.items():
        print(f"     {energy_type}: {count}个用户")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(verify_user_tags()) 