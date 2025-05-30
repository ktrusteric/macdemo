#!/usr/bin/env python3
"""
更新Demo用户能源标签脚本
每个用户只保留一个能源类型，基于覆盖率优化
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def update_demo_users():
    """更新demo用户的能源标签，每个用户只保留一个能源类型"""
    
    print("🔄 更新Demo用户能源标签...")
    print("=" * 50)
    
    # 连接数据库
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.energy_info
    users_collection = db.users
    user_tags_collection = db.user_tags
    
    # 根据覆盖率优化的能源类型分配
    # 天然气42.2%, 原油42.2%, LNG24.4%, PNG22.2%, 电力8.9%
    user_energy_mapping = [
        {
            "username": "张先生",
            "city": "上海", 
            "energy_type": "天然气",  # 覆盖率最高42.2%
            "description": "天然气市场分析师"
        },
        {
            "username": "李女士",
            "city": "北京",
            "energy_type": "原油",  # 覆盖率最高42.2%
            "description": "石油贸易专家"
        },
        {
            "username": "王先生", 
            "city": "深圳",
            "energy_type": "液化天然气(LNG)",  # 第三高24.4%
            "description": "LNG项目经理"
        },
        {
            "username": "陈女士",
            "city": "广州",
            "energy_type": "管道天然气(PNG)",  # 第四高22.2%
            "description": "管道天然气运营专家"
        },
        {
            "username": "刘先生",
            "city": "成都",
            "energy_type": "电力",  # 第五高8.9%
            "description": "电力系统研究员"
        }
    ]
    
    for mapping in user_energy_mapping:
        # 查找用户
        user = await users_collection.find_one({"username": mapping["username"]})
        if not user:
            print(f"❌ 未找到用户: {mapping['username']}")
            continue
            
        user_id = str(user["_id"])
        print(f"\n👤 更新用户: {mapping['username']} ({mapping['city']})")
        
        # 查找用户标签记录
        user_tags = await user_tags_collection.find_one({"user_id": user["id"]})
        if not user_tags:
            print(f"❌ 未找到用户标签记录: {mapping['username']}")
            continue
        
        # 移除所有旧的能源类型标签
        updated_tags = []
        energy_tags_removed = 0
        
        for tag in user_tags["tags"]:
            if tag["category"] == "energy_type":
                energy_tags_removed += 1
            else:
                updated_tags.append(tag)
        
        print(f"   🗑️ 移除 {energy_tags_removed} 个旧能源标签")
        
        # 添加新的单一能源类型标签
        new_energy_tag = {
            "category": "energy_type",
            "name": mapping["energy_type"],
            "weight": 2.5,  # 提升能源标签权重
            "source": "preset",
            "created_at": datetime.utcnow()
        }
        updated_tags.append(new_energy_tag)
        
        print(f"   ✅ 添加新能源标签: {mapping['energy_type']} (权重: 2.5)")
        
        # 更新数据库
        await user_tags_collection.update_one(
            {"user_id": user["id"]},
            {"$set": {"tags": updated_tags}}
        )
        
        # 更新用户description
        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"description": mapping["description"]}}
        )
        
        print(f"   📝 更新描述: {mapping['description']}")
    
    print(f"\n✅ Demo用户能源标签更新完成!")
    print(f"📊 每个用户现在只有1个能源类型标签")
    print(f"🎯 覆盖能源类型分布: 天然气, 原油, LNG, PNG, 电力")
    print(f"⚖️ 能源标签权重提升至: 2.5 (原为1.0)")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(update_demo_users()) 