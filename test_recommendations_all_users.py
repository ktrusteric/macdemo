import requests
import json

# API配置
BASE_URL = "http://localhost:8001"

# 用户ID映射
users = {
    "user001": {"id": "3efab1e8-91b2-448b-8490-1f0ad4cf656b", "name": "张工程师", "focus": "天然气+上海"},
    "user002": {"id": "f2f08f71-7be0-4e01-83e8-c72da34c1e18", "name": "李经理", "focus": "原油+北京"},
    "user003": {"id": "e7fca9e3-4dc6-4a55-b390-d82aa2f2e3f4", "name": "王主任", "focus": "LNG+深圳"},
    "user004": {"id": "82d33325-384b-4fce-853c-201078104e67", "name": "陈总监", "focus": "PNG+广州"},
    "user005": {"id": "d57d0354-b44f-47a2-bee0-185e7ac42dc9", "name": "刘研究员", "focus": "电力+成都"},
}

def get_user_recommendations(user_id, limit=10):
    """获取用户推荐"""
    url = f"{BASE_URL}/api/v1/users/{user_id}/recommendations?limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取推荐失败: {response.text}")
        return None

def analyze_recommendations(user_key, user_info, recommendations):
    """分析推荐结果"""
    if not recommendations or 'items' not in recommendations:
        print(f"❌ {user_key} ({user_info['name']}) - 无推荐数据")
        return
    
    articles = recommendations['items']
    print(f"\n🔍 {user_key} ({user_info['name']}) - {user_info['focus']}")
    print(f"推荐文章数: {len(articles)}")
    
    # 按内容类型分类
    content_types = {}
    for article in articles:
        content_type = article.get('type', '未知')
        if content_type not in content_types:
            content_types[content_type] = []
        content_types[content_type].append(article)
    
    print("📊 内容类型分布:")
    for content_type, type_articles in content_types.items():
        type_name = {
            'policy': '政策法规',
            'news': '行业资讯', 
            'announcement': '交易公告',
            'price': '调价公告'
        }.get(content_type, content_type)
        print(f"  {type_name}: {len(type_articles)}篇")
    
    # 分析前5篇文章的匹配度
    print("🎯 前5篇推荐文章:")
    for i, article in enumerate(articles[:5], 1):
        title = article['title'][:40] + "..."
        score = article.get('relevance_score', 0)
        content_type = article.get('type', '未知')
        type_name = {
            'policy': '政策',
            'news': '资讯', 
            'announcement': '公告',
            'price': '调价'
        }.get(content_type, content_type)
        
        energy_tags = article.get('energy_type_tags', [])
        region_tags = article.get('region_tags', [])
        
        print(f"  {i}. [{type_name}] {title}")
        print(f"     得分: {score:.3f} | 能源: {energy_tags[:2]} | 地区: {region_tags[:2]}")
    
    return content_types

def main():
    print("=== 测试所有用户的推荐差异 ===")
    print("验证简化标签配置后的推荐效果")
    print("="*60)
    
    all_results = {}
    
    # 获取所有用户的推荐
    for user_key, user_info in users.items():
        recommendations = get_user_recommendations(user_info['id'])
        content_types = analyze_recommendations(user_key, user_info, recommendations)
        all_results[user_key] = content_types
    
    # 汇总分析
    print("\n" + "="*60)
    print("📈 推荐差异化分析")
    print("="*60)
    
    print("\n🎯 各用户推荐类型分布对比:")
    type_names = {'policy': '政策法规', 'news': '行业资讯', 'announcement': '交易公告', 'price': '调价公告'}
    
    for type_key, type_name in type_names.items():
        print(f"\n{type_name}:")
        for user_key, user_info in users.items():
            if user_key in all_results and all_results[user_key]:
                count = len(all_results[user_key].get(type_key, []))
                print(f"  {user_info['name']}: {count}篇")
    
    print("\n🔍 推荐差异化评估:")
    print("✅ 如果各用户的推荐类型分布有明显差异，说明标签配置有效")
    print("❌ 如果各用户推荐结果过于相似，需要进一步优化数据或算法")
    
    # 检查是否有明显差异
    has_difference = False
    for type_key in type_names.keys():
        counts = []
        for user_key in all_results.keys():
            if all_results[user_key]:
                counts.append(len(all_results[user_key].get(type_key, [])))
        
        if len(set(counts)) > 1:  # 如果有不同的数量
            has_difference = True
            break
    
    if has_difference:
        print("\n✅ 推荐系统工作正常 - 不同用户获得了差异化的推荐结果")
    else:
        print("\n⚠️  推荐结果相似度较高 - 可能需要进一步优化")

if __name__ == "__main__":
    main() 