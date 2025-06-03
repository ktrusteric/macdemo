#!/usr/bin/env python3
import requests
import json

def debug_content_recommend_api():
    """调试/content/recommend API的多样化推荐逻辑"""
    print("🔍 调试 /content/recommend API")
    print("="*60)
    
    # 测试参数
    test_request = {
        'user_tags': ['region:华东地区', 'energy_type:天然气'],
        'limit': 6
    }
    
    print(f"📤 测试请求: {test_request}")
    print()
    
    # 调用API
    response = requests.post(
        'http://localhost:8001/api/v1/content/recommend',
        json=test_request
    )
    
    if response.status_code != 200:
        print(f"❌ API调用失败: {response.status_code}")
        print(f"错误信息: {response.text}")
        return
    
    data = response.json()
    items = data.get('items', [])
    
    print(f"✅ API调用成功，返回 {len(items)} 条内容")
    print()
    
    # 分析返回结果
    content_types = {}
    for item in items:
        content_type = item.get('type', '未知')
        if content_type not in content_types:
            content_types[content_type] = []
        content_types[content_type].append(item)
    
    print("📊 内容类型分布:")
    type_names = {
        'policy': '政策法规',
        'news': '行业资讯', 
        'announcement': '交易公告',
        'price': '调价公告'
    }
    
    for content_type, type_articles in content_types.items():
        type_name = type_names.get(content_type, content_type)
        print(f"  {type_name}: {len(type_articles)}篇")
    
    print()
    print("🎯 详细分析:")
    
    # 检查是否应该走多样化推荐逻辑
    has_basic_info = any('basic_info:' in tag for tag in test_request['user_tags'])
    print(f"用户是否有basic_info标签: {has_basic_info}")
    print(f"应该走多样化推荐逻辑: {not has_basic_info}")
    
    if not has_basic_info:
        print("\n🎯 多样化推荐逻辑分析:")
        print("应该获取的内容类型: ['行业资讯', '政策法规', '交易公告', '调价公告']")
        print(f"每种类型应获取: {6 // 4} = 1篇")
        
        # 测试每种类型的单独查询
        print("\n🔍 测试单独查询每种类型:")
        for content_type in ['行业资讯', '政策法规', '交易公告', '调价公告']:
            test_single_type = requests.post(
                'http://localhost:8001/api/v1/content/recommend',
                json={
                    'user_tags': ['basic_info:' + content_type, 'region:华东地区', 'energy_type:天然气'],
                    'limit': 2
                }
            )
            
            if test_single_type.status_code == 200:
                single_data = test_single_type.json()
                single_items = single_data.get('items', [])
                print(f"  {content_type}: {len(single_items)}篇可用")
                
                # 显示匹配的文章标题
                for item in single_items[:1]:
                    title = item['title'][:40] + "..."
                    energy_tags = item.get('energy_type_tags', [])
                    region_tags = item.get('region_tags', [])
                    print(f"    - {title}")
                    print(f"      能源: {energy_tags}, 地区: {region_tags}")
            else:
                print(f"  {content_type}: 查询失败")
    
    print()
    print("🔍 实际返回的文章详情:")
    for i, item in enumerate(items[:6], 1):
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
        print()
    
    # 保存结果
    with open('debug_content_recommend_result.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("💾 调试结果已保存到 debug_content_recommend_result.json")

if __name__ == "__main__":
    debug_content_recommend_api() 