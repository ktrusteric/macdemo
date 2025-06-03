#!/usr/bin/env python3
import requests
import json

def test_zhang_frontend_call():
    """模拟前端调用推荐API"""
    print("🔍 模拟前端张工程师访问'猜你喜欢'功能")
    print("="*60)
    
    # 1. 获取张工程师的用户信息
    print("1️⃣ 获取张工程师用户信息...")
    demo_users_response = requests.get('http://localhost:8001/api/v1/users/demo-users')
    demo_users = demo_users_response.json()
    
    zhang_user = None
    for user in demo_users['users']:
        if user['username'] == '张工程师':
            zhang_user = user
            break
    
    if not zhang_user:
        print("❌ 未找到张工程师用户")
        return
    
    print(f"✅ 找到用户: {zhang_user['username']} (ID: {zhang_user['id']})")
    print(f"   描述: {zhang_user['description']}")
    print(f"   城市: {zhang_user['register_city']}")
    
    # 2. 获取用户标签
    print("\n2️⃣ 获取用户标签...")
    user_id = zhang_user['id']
    tags_response = requests.get(f'http://localhost:8001/api/v1/users/{user_id}/tags')
    tags_data = tags_response.json()
    
    if not tags_data['success']:
        print("❌ 获取用户标签失败")
        return
    
    user_tags = tags_data['data']['tags']
    print(f"✅ 用户标签数量: {len(user_tags)}")
    for tag in user_tags:
        print(f"   {tag['category']}: {tag['name']} (权重: {tag['weight']})")
    
    # 3. 模拟前端筛选标签（排除city、province）
    print("\n3️⃣ 前端标签筛选...")
    relevant_tags = [tag for tag in user_tags if tag['category'] in 
                    ['basic_info', 'region', 'energy_type', 'business_field', 'beneficiary', 'policy_measure', 'importance']]
    
    print(f"✅ 筛选后标签数量: {len(relevant_tags)}")
    for tag in relevant_tags:
        print(f"   {tag['category']}: {tag['name']}")
    
    # 4. 调用推荐API（模拟修改后的前端）
    print("\n4️⃣ 调用推荐API...")
    
    print(f"📤 调用个性化推荐API: /users/{user_id}/recommendations")
    
    recommend_response = requests.get(
        f'http://localhost:8001/api/v1/users/{user_id}/recommendations',
        params={
            'page': 1,
            'page_size': 10
        }
    )
    
    if recommend_response.status_code != 200:
        print(f"❌ API调用失败: {recommend_response.status_code}")
        print(f"错误信息: {recommend_response.text}")
        return
    
    recommend_data = recommend_response.json()
    
    # 5. 分析推荐结果
    print("\n5️⃣ 分析推荐结果...")
    items = recommend_data.get('items', [])
    print(f"✅ 推荐文章数量: {len(items)}")
    
    # 按内容类型分类
    content_types = {}
    for item in items:
        content_type = item.get('type', '未知')
        if content_type not in content_types:
            content_types[content_type] = []
        content_types[content_type].append(item)
    
    print("\n📊 内容类型分布:")
    type_names = {
        'policy': '政策法规',
        'news': '行业资讯', 
        'announcement': '交易公告',
        'price': '调价公告'
    }
    
    for content_type, type_articles in content_types.items():
        type_name = type_names.get(content_type, content_type)
        print(f"  {type_name}: {len(type_articles)}篇")
    
    print("\n🎯 前3篇推荐文章详情:")
    for i, item in enumerate(items[:3], 1):
        title = item['title'][:50] + "..."
        content_type = item.get('type', '未知')
        type_name = type_names.get(content_type, content_type)
        
        energy_tags = item.get('energy_type_tags', [])
        region_tags = item.get('region_tags', [])
        basic_tags = item.get('basic_info_tags', [])
        
        print(f"  {i}. [{type_name}] {title}")
        print(f"     能源: {energy_tags}")
        print(f"     地区: {region_tags}")
        print(f"     基础: {basic_tags}")
    
    # 6. 对比预期结果
    print("\n6️⃣ 对比预期结果...")
    print("预期: 政策法规4篇，调价公告1篇，交易公告2篇，行业资讯3篇")
    
    actual_policy = len(content_types.get('policy', []))
    actual_price = len(content_types.get('price', []))
    actual_announcement = len(content_types.get('announcement', []))
    actual_news = len(content_types.get('news', []))
    
    print(f"实际: 政策法规{actual_policy}篇，调价公告{actual_price}篇，交易公告{actual_announcement}篇，行业资讯{actual_news}篇")
    
    if actual_policy == 4 and actual_price == 1 and actual_announcement == 2 and actual_news == 3:
        print("✅ 推荐结果符合预期")
    else:
        print("❌ 推荐结果与预期不符")
        print("\n🔍 可能的问题:")
        print("1. 前端调用的API与后端测试的API不一致")
        print("2. 前端标签筛选逻辑与后端不同")
        print("3. 数据库数据可能发生了变化")
        print("4. 推荐算法逻辑有问题")
    
    # 7. 保存结果用于进一步分析
    with open('frontend_call_result.json', 'w', encoding='utf-8') as f:
        json.dump(recommend_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 推荐结果已保存到 frontend_call_result.json")

if __name__ == "__main__":
    test_zhang_frontend_call() 