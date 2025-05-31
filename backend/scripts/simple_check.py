#!/usr/bin/env python3
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.energy_info
collection = db.content

# 查找包含重烃的文章
heavy_hc_query = {'$or': [
    {'energy_type_tags': '重烃'}, 
    {'标题': {'$regex': '重烃', '$options': 'i'}}
]}
heavy_hc_articles = list(collection.find(heavy_hc_query))

print(f'🔍 包含重烃的文章数量: {len(heavy_hc_articles)}')

for i, article in enumerate(heavy_hc_articles):
    title = article.get('标题', '未知标题')
    print(f'{i+1}. {title[:60]}...')
    print(f'   能源类型标签: {article.get("energy_type_tags", [])}')
    print()

# 检查能源类型分布
pipeline = [
    {'$unwind': '$energy_type_tags'},
    {'$group': {'_id': '$energy_type_tags', 'count': {'$sum': 1}}},
    {'$sort': {'count': -1}}
]

energy_distribution = list(collection.aggregate(pipeline))

print('📊 能源类型分布:')
for item in energy_distribution:
    print(f'   {item["_id"]}: {item["count"]} 篇')

# 总文章数
total_count = collection.count_documents({})
print(f'\n📚 总文章数: {total_count} 篇')

print('\n✅ 检查完成') 