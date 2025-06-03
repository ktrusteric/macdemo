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

# 优化后的用户标签配置
user_tags_config = {
    "user001": {  # 张工程师 - 天然气市场分析师
        "description": "关注天然气价格政策和市场动态",
        "additional_tags": [
            {"category": "business_field", "name": "价格动态", "weight": 1.8, "source": "manual"},
            {"category": "policy_measure", "name": "价格调整", "weight": 1.5, "source": "manual"},
            {"category": "basic_info", "name": "政策法规", "weight": 1.2, "source": "manual"},
        ]
    },
    "user002": {  # 李经理 - 原油贸易专家
        "description": "关注原油进口贸易和国际市场",
        "additional_tags": [
            {"category": "business_field", "name": "国际合作", "weight": 1.8, "source": "manual"},
            {"category": "business_field", "name": "市场动态", "weight": 1.6, "source": "manual"},
            {"category": "basic_info", "name": "行业资讯", "weight": 1.4, "source": "manual"},
            {"category": "region", "name": "国际", "weight": 1.2, "source": "manual"},
        ]
    },
    "user003": {  # 王主任 - LNG项目经理
        "description": "关注LNG交易公告和项目信息",
        "additional_tags": [
            {"category": "business_field", "name": "交易信息", "weight": 1.8, "source": "manual"},
            {"category": "basic_info", "name": "交易公告", "weight": 1.6, "source": "manual"},
            {"category": "beneficiary", "name": "LNG交易方", "weight": 1.4, "source": "manual"},
            {"category": "policy_measure", "name": "竞价规则", "weight": 1.2, "source": "manual"},
        ]
    },
    "user004": {  # 陈总监 - 管道天然气运营专家
        "description": "关注管道天然气基础设施和运营政策",
        "additional_tags": [
            {"category": "business_field", "name": "运输储存", "weight": 1.8, "source": "manual"},
            {"category": "policy_measure", "name": "基础设施建设", "weight": 1.6, "source": "manual"},
            {"category": "basic_info", "name": "政策法规", "weight": 1.4, "source": "manual"},
            {"category": "beneficiary", "name": "管道运营商", "weight": 1.2, "source": "manual"},
        ]
    },
    "user005": {  # 刘研究员 - 电力系统研究员
        "description": "关注电力政策和可再生能源发展",
        "additional_tags": [
            {"category": "business_field", "name": "科技创新", "weight": 1.8, "source": "manual"},
            {"category": "policy_measure", "name": "技术合作", "weight": 1.6, "source": "manual"},
            {"category": "basic_info", "name": "政策法规", "weight": 1.4, "source": "manual"},
            {"category": "beneficiary", "name": "能源企业", "weight": 1.2, "source": "manual"},
        ]
    }
}

def update_user_tags(user_id, additional_tags):
    """更新用户标签"""
    url = f"{BASE_URL}/api/v1/users/{user_id}/tags"
    
    # 获取当前标签
    response = requests.get(url)
    if response.status_code != 200:
        print(f"获取用户标签失败: {response.text}")
        return False
    
    current_data = response.json()
    current_tags = current_data['data']['tags']
    
    # 添加新标签
    all_tags = current_tags + additional_tags
    
    # 更新标签
    update_data = {"tags": all_tags}
    response = requests.put(url, json=update_data)
    
    if response.status_code == 200:
        print(f"✓ 用户 {user_id} 标签更新成功")
        return True
    else:
        print(f"✗ 用户 {user_id} 标签更新失败: {response.text}")
        return False

def main():
    print("=== 开始优化用户标签配置 ===")
    
    for demo_user_id, config in user_tags_config.items():
        user_id = users[demo_user_id]
        additional_tags = config["additional_tags"]
        description = config["description"]
        
        print(f"\n更新 {demo_user_id} ({description}):")
        print(f"  添加标签: {[tag['name'] for tag in additional_tags]}")
        
        success = update_user_tags(user_id, additional_tags)
        if success:
            print(f"  ✓ 成功添加 {len(additional_tags)} 个差异化标签")
        else:
            print(f"  ✗ 标签更新失败")

if __name__ == "__main__":
    main() 