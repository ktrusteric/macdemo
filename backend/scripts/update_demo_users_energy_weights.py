#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新演示用户能源权重
将现有演示用户的能源标签权重更新为分层权重体系
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.utils.energy_weight_system import EnergyWeightSystem, get_energy_weight, get_energy_category
from datetime import datetime

async def update_demo_users_energy_weights():
    """更新演示用户的能源标签权重"""
    print("🔋 更新演示用户能源权重体系")
    print("=" * 50)
    
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        user_tags_collection = db["user_tags"]
        users_collection = db["users"]
        
        # 1. 获取所有演示用户
        print("👥 获取演示用户列表...")
        demo_users_cursor = users_collection.find(
            {"demo_user_id": {"$exists": True}},
            {"id": 1, "demo_user_id": 1, "username": 1, "_id": 0}
        )
        
        demo_users = await demo_users_cursor.to_list(length=None)
        print(f"找到 {len(demo_users)} 个演示用户")
        
        total_updated = 0
        
        for demo_user in demo_users:
            user_id = demo_user["id"]
            demo_user_id = demo_user["demo_user_id"]
            username = demo_user["username"]
            
            print(f"\n🔧 处理用户: {username} ({demo_user_id})")
            
            # 2. 获取用户当前标签
            user_tags_doc = await user_tags_collection.find_one({"user_id": user_id})
            if not user_tags_doc:
                print(f"   ⚠️ 用户 {username} 没有标签，跳过")
                continue
            
            tags = user_tags_doc.get("tags", [])
            print(f"   📊 当前标签数: {len(tags)}")
            
            # 3. 提取能源类型标签
            energy_tags = [tag for tag in tags if tag.get("category") == "energy_type"]
            other_tags = [tag for tag in tags if tag.get("category") != "energy_type"]
            
            print(f"   ⚡ 能源标签数: {len(energy_tags)}")
            print(f"   🏷️ 其他标签数: {len(other_tags)}")
            
            if not energy_tags:
                print(f"   ⚠️ 用户 {username} 没有能源标签，跳过")
                continue
            
            # 4. 更新能源标签权重
            updated_energy_tags = []
            categories_added = set()
            
            for tag in energy_tags:
                tag_name = tag.get("name")
                if not tag_name:
                    continue
                
                # 获取新的权重
                new_weight = get_energy_weight(tag_name)
                category = get_energy_category(tag_name)
                old_weight = tag.get("weight", 1.0)
                
                # 更新标签权重
                updated_tag = tag.copy()
                updated_tag["weight"] = float(new_weight)
                updated_energy_tags.append(updated_tag)
                
                # 检查权重是否变化
                weight_changed = abs(old_weight - float(new_weight)) > 0.01
                weight_status = "🔄" if weight_changed else "✅"
                print(f"     {weight_status} {tag_name}: {old_weight} -> {new_weight}")
                
                # 如果是具体产品，自动添加对应的大类标签
                is_category = tag_name in EnergyWeightSystem.ENERGY_HIERARCHY
                if not is_category and category and category not in categories_added:
                    # 检查是否已经有这个大类标签
                    has_category_tag = any(
                        t.get("name") == category for t in energy_tags
                    )
                    
                    if not has_category_tag:
                        # 添加大类标签
                        category_tag = {
                            "category": "energy_type",
                            "name": category,
                            "weight": 3.0,  # 大类权重
                            "source": "region_auto",
                            "created_at": datetime.utcnow()
                        }
                        updated_energy_tags.append(category_tag)
                        categories_added.add(category)
                        print(f"     ➕ 自动添加大类: {category} (权重: 3.0)")
            
            # 5. 合并所有标签
            all_updated_tags = other_tags + updated_energy_tags
            
            # 6. 更新数据库
            update_result = await user_tags_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "tags": all_updated_tags,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if update_result.modified_count > 0:
                total_updated += 1
                print(f"   ✅ 用户 {username} 权重更新成功")
                print(f"     📊 最终能源标签数: {len(updated_energy_tags)}")
                print(f"     📊 总标签数: {len(all_updated_tags)}")
            else:
                print(f"   ⚠️ 用户 {username} 权重更新失败")
        
        print(f"\n🎉 演示用户能源权重更新完成!")
        print(f"📈 统计结果:")
        print(f"   👥 总演示用户数: {len(demo_users)}")
        print(f"   ✅ 成功更新用户数: {total_updated}")
        print(f"   🔥 权重体系: 大类3.0，具体产品5.0")
        
        # 7. 验证更新结果
        print(f"\n🔍 验证更新结果:")
        for demo_user in demo_users:
            user_id = demo_user["id"]
            username = demo_user["username"]
            
            user_tags_doc = await user_tags_collection.find_one({"user_id": user_id})
            if user_tags_doc:
                energy_tags = [
                    tag for tag in user_tags_doc.get("tags", [])
                    if tag.get("category") == "energy_type"
                ]
                
                category_tags = [tag for tag in energy_tags if tag.get("weight") == 3.0]
                product_tags = [tag for tag in energy_tags if tag.get("weight") == 5.0]
                
                print(f"   👤 {username}:")
                print(f"      📁 大类标签: {len(category_tags)} 个")
                print(f"      🔧 具体产品: {len(product_tags)} 个")
                
                # 显示前3个标签
                for i, tag in enumerate(energy_tags[:3]):
                    weight_type = "大类" if tag.get("weight") == 3.0 else "具体产品" if tag.get("weight") == 5.0 else "其他"
                    print(f"         {i+1}. {tag.get('name')} (权重: {tag.get('weight')}, {weight_type})")
        
        client.close()
        
    except Exception as e:
        print(f"❌ 更新过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(update_demo_users_energy_weights()) 