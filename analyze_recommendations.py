import json

# 分析推荐结果
with open('user001_recommendations.json', 'r', encoding='utf-8') as f:
    recommendations = json.load(f)

print("=== 用户001推荐分析 ===")
print(f"推荐文章总数: {len(recommendations['items'])}")
print()

# 按内容类型分类
content_types = {}
for article in recommendations['items']:
    content_type = article.get('type', '未知')
    if content_type not in content_types:
        content_types[content_type] = []
    content_types[content_type].append(article)

print("=== 推荐文章按类型分布 ===")
for content_type, articles_list in content_types.items():
    print(f"{content_type}: {len(articles_list)}篇")

print()
print("=== 各类型推荐文章详情 ===")
for content_type, articles_list in content_types.items():
    print(f"\n{content_type}类文章 ({len(articles_list)}篇):")
    for i, article in enumerate(articles_list[:3], 1):
        print(f"  {i}. {article['title'][:60]}...")
        print(f"     相关度得分: {article.get('relevance_score', 0):.3f}")
        print(f"     能源标签: {article.get('energy_type_tags', [])}")
        print(f"     地区标签: {article.get('region_tags', [])}")
        print(f"     基础信息标签: {article.get('basic_info_tags', [])}")

# 分析所有文章数据
print("\n" + "="*60)
print("=== 全部文章数据分析 ===")

with open('articles_data.json', 'r', encoding='utf-8') as f:
    all_articles = json.load(f)

articles = all_articles['items']
print(f"总文章数: {len(articles)}")

# 按type字段分类（原始数据）
original_types = {}
for article in articles:
    content_type = article.get('type', '未知')
    if content_type not in original_types:
        original_types[content_type] = []
    original_types[content_type].append(article)

print("\n=== 原始数据按type字段分布 ===")
for content_type, articles_list in original_types.items():
    print(f"{content_type}: {len(articles_list)}篇")

print("\n=== 各类型文章示例 ===")
for content_type, articles_list in original_types.items():
    print(f"\n{content_type}类文章:")
    for i, article in enumerate(articles_list[:2], 1):
        print(f"  {i}. {article['title'][:50]}...")
        print(f"     能源标签: {article.get('energy_type_tags', [])}")
        print(f"     地区标签: {article.get('region_tags', [])}")
        print(f"     基础信息标签: {article.get('basic_info_tags', [])}")

# 分析用户标签
print("\n" + "="*60)
print("=== 用户001标签分析 ===")
with open('user001_tags.json', 'r', encoding='utf-8') as f:
    user_tags = json.load(f)

print("用户001标签:")
for tag in user_tags['data']['tags']:
    print(f"  {tag['category']}: {tag['name']} (权重: {tag['weight']})")

print("\n=== 标签匹配度分析 ===")
print("用户001关注: 上海 + 天然气")
print("推荐的前5篇文章匹配情况:")
for i, article in enumerate(recommendations['items'][:5], 1):
    title = article['title'][:40] + "..."
    energy_match = "天然气" in article.get('energy_type_tags', [])
    region_match = any(tag in ["上海", "上海市"] for tag in article.get('region_tags', []))
    score = article.get('relevance_score', 0)
    print(f"  {i}. {title}")
    print(f"     能源匹配: {'✓' if energy_match else '✗'}, 地区匹配: {'✓' if region_match else '✗'}, 得分: {score:.3f}") 