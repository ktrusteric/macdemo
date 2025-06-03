import requests
import json

# API配置
BASE_URL = "http://localhost:8001"

# 用户ID映射
users = {
    "user001": "3efab1e8-91b2-448b-8490-1f0ad4cf656b",  # 张工程师 - 天然气
    "user002": "f2f08f71-7be0-4e01-83e8-c72da34c1e18",  # 李经理 - 原油
    "user003": "e7fca9e3-4dc6-4a55-b390-d82aa2f2e3f4",  # 王主任 - LNG
    "user004": "82d33325-384b-4fce-853c-201078104e67",  # 陈总监 - PNG
    "user005": "d57d0354-b44f-47a2-bee0-185e7ac42dc9",  # 刘研究员 - 电力
}

# 简化的用户标签配置 - 只保留核心标签
simplified_user_tags = {
    "user001": {  # 张工程师 - 天然气市场分析师（上海）
        "description": "天然气市场分析师 - 关注天然气价格与政策",
        "tags": [
            {"category": "city", "name": "上海", "weight": 2.5, "source": "preset"},
            {"category": "province", "name": "上海市", "weight": 2.0, "source": "region_auto"},
            {"category": "region", "name": "华东地区", "weight": 1.5, "source": "region_auto"},
            {"category": "energy_type", "name": "天然气", "weight": 2.0, "source": "preset"},
        ]
    },
    "user002": {  # 李经理 - 原油贸易专家（北京）
        "description": "石油贸易专家 - 原油进口与价格分析",
        "tags": [
            {"category": "city", "name": "北京", "weight": 2.5, "source": "preset"},
            {"category": "province", "name": "北京市", "weight": 2.0, "source": "region_auto"},
            {"category": "region", "name": "华北地区", "weight": 1.5, "source": "region_auto"},
            {"category": "energy_type", "name": "原油", "weight": 2.0, "source": "preset"},
        ]
    },
    "user003": {  # 王主任 - LNG项目经理（深圳）
        "description": "LNG项目经理 - 液化天然气接收站运营",
        "tags": [
            {"category": "city", "name": "深圳", "weight": 2.5, "source": "preset"},
            {"category": "province", "name": "广东省", "weight": 2.0, "source": "region_auto"},
            {"category": "region", "name": "华南地区", "weight": 1.5, "source": "region_auto"},
            {"category": "energy_type", "name": "液化天然气(LNG)", "weight": 2.0, "source": "preset"},
        ]
    },
    "user004": {  # 陈总监 - 管道天然气运营专家（广州）
        "description": "管道天然气运营专家 - 天然气管网建设",
        "tags": [
            {"category": "city", "name": "广州", "weight": 2.5, "source": "preset"},
            {"category": "province", "name": "广东省", "weight": 2.0, "source": "region_auto"},
            {"category": "region", "name": "华南地区", "weight": 1.5, "source": "region_auto"},
            {"category": "energy_type", "name": "管道天然气(PNG)", "weight": 2.0, "source": "preset"},
        ]
    },
    "user005": {  # 刘研究员 - 电力系统研究员（成都）
        "description": "电力系统研究员 - 可再生能源发电",
        "tags": [
            {"category": "city", "name": "成都", "weight": 2.5, "source": "preset"},
            {"category": "province", "name": "四川省", "weight": 2.0, "source": "region_auto"},
            {"category": "region", "name": "西南地区", "weight": 1.5, "source": "region_auto"},
            {"category": "energy_type", "name": "电力", "weight": 2.0, "source": "preset"},
        ]
    }
}

def reset_user_tags(user_id, new_tags):
    """重置用户标签为简化版本"""
    url = f"{BASE_URL}/api/v1/users/{user_id}/tags"
    
    # 直接设置新标签（覆盖现有标签）
    update_data = {"tags": new_tags}
    response = requests.put(url, json=update_data)
    
    if response.status_code == 200:
        print(f"✓ 用户 {user_id} 标签重置成功")
        return True
    else:
        print(f"✗ 用户 {user_id} 标签重置失败: {response.text}")
        return False

def main():
    print("=== 重置用户标签为简化版本 ===")
    print("只保留核心标签：城市、省份、地区、能源类型")
    print()
    
    for demo_user_id, config in simplified_user_tags.items():
        user_id = users[demo_user_id]
        new_tags = config["tags"]
        description = config["description"]
        
        print(f"重置 {demo_user_id} ({description}):")
        print(f"  核心标签: {[tag['name'] for tag in new_tags]}")
        
        success = reset_user_tags(user_id, new_tags)
        if success:
            print(f"  ✓ 成功重置为 {len(new_tags)} 个核心标签")
        else:
            print(f"  ✗ 标签重置失败")
        print()

    print("=== 标签重置完成 ===")
    print("每个用户现在只有4个核心标签：")
    print("• 城市标签 (权重: 2.5)")
    print("• 省份标签 (权重: 2.0)")  
    print("• 地区标签 (权重: 1.5)")
    print("• 能源类型标签 (权重: 2.0)")
    print()
    print("这样可以确保推荐算法更加聚焦，避免标签过多导致的相似性问题。")

if __name__ == "__main__":
    main() 