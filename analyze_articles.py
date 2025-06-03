import json

with open('articles_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

articles = data['items']
print(f'总文章数: {len(articles)}')
print()

# 按内容类型分类统计
content_types = {}
for article in articles:
    content_type = article.get('content_type', '未知')
    if content_type not in content_types:
        content_types[content_type] = []
    content_types[content_type].append(article)

print('=== 按内容类型分类统计 ===')
for content_type, articles_list in content_types.items():
    print(f'{content_type}: {len(articles_list)}篇')
    
print()
print('=== 各类型文章标签分析 ===')
for content_type, articles_list in content_types.items():
    print(f'\n{content_type} ({len(articles_list)}篇):')
    
    # 统计能源类型标签
    energy_tags = {}
    region_tags = {}
    
    for article in articles_list:
        # 能源类型标签
        for tag in article.get('energy_type_tags', []):
            energy_tags[tag] = energy_tags.get(tag, 0) + 1
        
        # 地区标签
        for tag in article.get('region_tags', []):
            region_tags[tag] = region_tags.get(tag, 0) + 1
    
    print('  能源类型标签:')
    for tag, count in sorted(energy_tags.items(), key=lambda x: x[1], reverse=True):
        print(f'    {tag}: {count}篇')
    
    print('  地区标签:')
    for tag, count in sorted(region_tags.items(), key=lambda x: x[1], reverse=True)[:5]:  # 只显示前5个
        print(f'    {tag}: {count}篇')

print('\n=== 详细文章列表（按类型） ===')
for content_type, articles_list in content_types.items():
    print(f'\n{content_type}类文章:')
    for i, article in enumerate(articles_list[:3], 1):  # 只显示前3篇
        print(f'  {i}. {article["title"][:50]}...')
        print(f'     能源标签: {article.get("energy_type_tags", [])}')
        print(f'     地区标签: {article.get("region_tags", [])}') 