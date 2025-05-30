import json
from collections import Counter

# 读取数据
with open('信息发布文章与标签.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'📊 总文章数量: {len(data)}')
print()

# 分析文档类型分布
doc_types = [item.get('文档类型', '未知') for item in data]
type_counter = Counter(doc_types)
print('📋 文档类型分布:')
for doc_type, count in type_counter.most_common():
    print(f'  {doc_type}: {count}篇 ({count/len(data)*100:.1f}%)')
print()

# 分析标签数量分布
tag_counts = []
all_tags_detail = []

for i, item in enumerate(data):
    total_tags = 0
    item_tags = {
        '基础信息': [],
        '地域': [],
        '能源品种': [],
        '业务领域': [],
        '受益主体': [],
        '关键措施': [],
        '重要性': []
    }
    
    # 统计各类标签数量
    tag_mapping = {
        '基础信息标签': '基础信息',
        '地域标签': '地域',
        '能源品种标签': '能源品种',
        '业务领域/主题标签': '业务领域',
        '受益主体标签': '受益主体',
        '关键措施/政策标签': '关键措施',
        '重要性/影响力标签': '重要性'
    }
    
    for tag_key, category in tag_mapping.items():
        if tag_key in item and item[tag_key]:
            if isinstance(item[tag_key], str):
                try:
                    import ast
                    tags = ast.literal_eval(item[tag_key])
                    if isinstance(tags, list):
                        total_tags += len(tags)
                        item_tags[category] = tags
                except:
                    total_tags += 1
                    item_tags[category] = [item[tag_key]]
            elif isinstance(item[tag_key], list):
                total_tags += len(item[tag_key])
                item_tags[category] = item[tag_key]
    
    tag_counts.append(total_tags)
    all_tags_detail.append({
        'title': item.get('标题', '无标题')[:50] + '...',
        'type': item.get('文档类型', '未知'),
        'total_tags': total_tags,
        'tags': item_tags
    })

tag_dist = Counter(tag_counts)
print('🏷️ 每篇文章标签数量分布:')
for tag_count, article_count in sorted(tag_dist.items()):
    print(f'  {tag_count}个标签: {article_count}篇文章 ({article_count/len(data)*100:.1f}%)')
print()

print(f'📈 标签数量统计:')
print(f'  平均每篇: {sum(tag_counts)/len(tag_counts):.1f}个标签')
print(f'  最多标签: {max(tag_counts)}个')
print(f'  最少标签: {min(tag_counts)}个')
print()

# 找出标签最多的文章
max_tags_count = max(tag_counts)
print(f'🔍 标签最多的文章 ({max_tags_count}个标签):')
for detail in all_tags_detail:
    if detail['total_tags'] == max_tags_count:
        print(f'  标题: {detail["title"]}')
        print(f'  类型: {detail["type"]}')
        for category, tags in detail['tags'].items():
            if tags:
                print(f'    {category}: {tags}')
        print()

# 分析各类标签的使用频率
category_stats = {
    '基础信息': Counter(),
    '地域': Counter(),
    '能源品种': Counter(),
    '业务领域': Counter(),
    '受益主体': Counter(),
    '关键措施': Counter(),
    '重要性': Counter()
}

for detail in all_tags_detail:
    for category, tags in detail['tags'].items():
        for tag in tags:
            category_stats[category][tag] += 1

print('📊 各类标签使用频率分析:')
for category, counter in category_stats.items():
    print(f'\n{category}标签 (共{len(counter)}种):')
    for tag, count in counter.most_common(10):  # 只显示前10个
        print(f'  {tag}: {count}次')

# 检查是否有重复的标签组合模式
print('\n🔄 检查标签重复模式:')
same_tags_articles = []
for i, detail1 in enumerate(all_tags_detail):
    for j, detail2 in enumerate(all_tags_detail[i+1:], i+1):
        if detail1['tags'] == detail2['tags'] and detail1['total_tags'] > 5:
            same_tags_articles.append((i, j, detail1['total_tags']))

if same_tags_articles:
    print(f'发现 {len(same_tags_articles)} 组完全相同的标签组合:')
    for i, j, tag_count in same_tags_articles[:5]:  # 只显示前5组
        print(f'  文章{i+1} 和 文章{j+1} 有相同的{tag_count}个标签')
        print(f'    标题1: {all_tags_detail[i]["title"]}')
        print(f'    标题2: {all_tags_detail[j]["title"]}')
else:
    print('未发现完全相同的标签组合') 