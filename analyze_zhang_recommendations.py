import json

# 分析张工程师的推荐结果
with open('zhang_recommendations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

if 'items' not in data:
    print("❌ 推荐数据获取失败")
    print(f"返回数据: {data}")
    exit(1)

articles = data['items']
print(f"🔍 张工程师推荐分析")
print(f"推荐文章总数: {len(articles)}")
print()

# 按内容类型分类
content_types = {}
for article in articles:
    content_type = article.get('type', '未知')
    if content_type not in content_types:
        content_types[content_type] = []
    content_types[content_type].append(article)

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
print("🎯 详细推荐文章列表:")
for i, article in enumerate(articles, 1):
    title = article['title'][:50] + "..."
    score = article.get('relevance_score', 0)
    content_type = article.get('type', '未知')
    type_name = type_names.get(content_type, content_type)
    
    energy_tags = article.get('energy_type_tags', [])
    region_tags = article.get('region_tags', [])
    basic_tags = article.get('basic_info_tags', [])
    
    print(f"  {i:2d}. [{type_name}] {title}")
    print(f"      得分: {score:.3f}")
    print(f"      能源: {energy_tags}")
    print(f"      地区: {region_tags}")
    print(f"      基础: {basic_tags}")
    print()

# 检查是否符合预期
print("="*60)
print("🔍 预期 vs 实际对比:")
print("预期: 政策法规4篇，调价公告1篇，交易公告2篇，行业资讯3篇")

actual_policy = len(content_types.get('policy', []))
actual_price = len(content_types.get('price', []))
actual_announcement = len(content_types.get('announcement', []))
actual_news = len(content_types.get('news', []))

print(f"实际: 政策法规{actual_policy}篇，调价公告{actual_price}篇，交易公告{actual_announcement}篇，行业资讯{actual_news}篇")

if actual_policy == 4 and actual_price == 1 and actual_announcement == 2 and actual_news == 3:
    print("✅ 推荐结果符合预期")
else:
    print("❌ 推荐结果与预期不符，可能需要重新初始化数据库")
    print()
    print("可能的问题:")
    if actual_policy != 4:
        print(f"  - 政策法规数量不对: 预期4篇，实际{actual_policy}篇")
    if actual_price != 1:
        print(f"  - 调价公告数量不对: 预期1篇，实际{actual_price}篇")
    if actual_announcement != 2:
        print(f"  - 交易公告数量不对: 预期2篇，实际{actual_announcement}篇")
    if actual_news != 3:
        print(f"  - 行业资讯数量不对: 预期3篇，实际{actual_news}篇") 