#!/usr/bin/env python3
"""
能源品种标签规范化脚本
根据README.md中定义的标准energyTypes重新分析和整理原始数据中的能源品种标签
"""

import json
import re
import os
from typing import List, Dict, Any
from china_regions import find_regions_in_text

# 标准能源类型（来自README.md）
STANDARD_ENERGY_TYPES = [
    '原油',
    '管道天然气(PNG)', 
    '天然气',
    '液化天然气(LNG)',
    '液化石油气(LPG)',
    '汽油',
    '柴油', 
    '沥青',
    '石油焦',
    '生物柴油',
    '电力',
    '煤炭',
    '重烃'
]

# 关键词映射表 - 根据文章内容关键词判断能源类型
ENERGY_TYPE_KEYWORDS = {
    '原油': [
        '原油', '石油', '原油进口', '原油价格', '原油加工', '原油储备',
        '石油勘探', '石油开采', '油田', '石油公司', '石油储量',
        'WTI', 'Brent', '布伦特', '石油期货'
    ],
    '管道天然气(PNG)': [
        '管道天然气', 'PNG', '管道气', '天然气管道', '输气管道',
        '天然气管网', '管输', '管道运输', '干线管道', '支线管道',
        '国家管网', '管道建设', '气源管道'
    ],
    '天然气': [
        '天然气', '天然气价格', '天然气销售', '天然气消费', 
        '天然气市场', '天然气供应', '天然气需求', '燃气',
        '天然气发电', '天然气化工', '页岩气', '常规天然气',
        '天然气基础设施', '天然气储备'
    ],
    '液化天然气(LNG)': [
        'LNG', '液化天然气', 'LNG接收站', 'LNG储罐', 'LNG船',
        'LNG进口', 'LNG出口', 'LNG终端', 'LNG加注', 'LNG槽车',
        '液化天然气接收站', '液化天然气储存', '液态天然气',
        'LNG交易', 'LNG现货', 'LNG合同'
    ],
    '液化石油气(LPG)': [
        'LPG', '液化石油气', '丙烷', '丁烷', '液化气',
        'LPG进口', 'LPG出口', 'LPG价格', 'LPG储罐',
        '液化石油气储存', '液化石油气销售', '重烃', 'C3', 'C4'
    ],
    '汽油': [
        '汽油', '汽油价格', '汽油销售', '汽油生产', '汽油消费',
        '92号汽油', '95号汽油', '98号汽油', '无铅汽油', '成品油汽油'
    ],
    '柴油': [
        '柴油', '柴油价格', '柴油销售', '柴油生产', '柴油消费',
        '0号柴油', '-10号柴油', '生物柴油除外'
    ],
    '沥青': [
        '沥青', '道路沥青', '建筑沥青', '沥青价格', '沥青生产',
        '沥青消费', '重质沥青', '沥青市场'
    ],
    '石油焦': [
        '石油焦', '石油焦价格', '石油焦生产', '石油焦销售',
        '针状焦', '海绵焦', '弹丸焦'
    ],
    '生物柴油': [
        '生物柴油', '生物燃料', '生物质柴油', '可再生柴油',
        '生物柴油生产', '生物柴油价格', 'BD100', 'B5', 'B10'
    ],
    '电力': [
        '电力', '发电', '电力生产', '电力消费', '电力市场',
        '电网', '火力发电', '水力发电', '核电', '风电', '光伏',
        '电价', '用电量', '发电量', '电力供应', '电力需求',
        '可再生能源', '新能源发电', '储能', '电力交易'
    ],
    '煤炭': [
        '煤炭', '原煤', '煤炭价格', '煤炭生产', '煤炭消费',
        '动力煤', '炼焦煤', '褐煤', '无烟煤', '煤炭市场',
        '煤矿', '煤炭开采', '煤炭储备', '煤炭进口', '煤炭出口'
    ],
    '重烃': [
        '重烃', '重质烃', '重烃产品', '重烃生产', '重烃销售',
        '重烃价格', '重烃市场', '重烃贸易', '重烃加工', '重烃储存',
        '重烃运输', '重烃化工', '戊烷', '己烷', 'C5+', 'C6+'
    ]
}

def analyze_energy_types_from_content(title: str, content: str) -> List[str]:
    """
    根据文章标题和内容分析能源类型
    """
    text = (title + " " + content).lower()
    detected_types = []
    
    # 按优先级检测能源类型（更具体的类型优先）
    priority_order = [
        '液化天然气(LNG)',
        '液化石油气(LPG)',
        '重烃',
        '管道天然气(PNG)',
        '生物柴油',
        '石油焦',
        '沥青',
        '汽油',
        '柴油',
        '原油',
        '天然气',  # 放在后面，避免被过度匹配
        '电力',
        '煤炭'
    ]
    
    for energy_type in priority_order:
        keywords = ENERGY_TYPE_KEYWORDS.get(energy_type, [])
        
        # 检查是否包含该能源类型的关键词
        matched_keywords = []
        for keyword in keywords:
            if keyword.lower() in text:
                matched_keywords.append(keyword)
        
        # 如果匹配到足够的关键词，就认为包含该能源类型
        if matched_keywords:
            print(f"   检测到 {energy_type}: {matched_keywords[:3]}")  # 只显示前3个匹配的关键词
            detected_types.append(energy_type)
            
            # 特殊处理：如果检测到LNG或PNG，就不再添加通用的"天然气"
            if energy_type in ['液化天然气(LNG)', '管道天然气(PNG)']:
                if '天然气' in detected_types:
                    detected_types.remove('天然气')
    
    # 限制每篇文章最多3个能源类型
    return detected_types[:3]

def normalize_energy_tags_in_articles():
    """
    规范化原始文章数据中的能源品种标签，同时优化地域标签识别
    """
    
    # 读取原始数据
    input_file = os.path.join(os.path.dirname(__file__), "信息发布文章与标签.json")
    if not os.path.exists(input_file):
        print("❌ 找不到原始数据文件")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    print(f"📊 开始处理 {len(original_data)} 篇文章")
    print(f"🎯 标准能源类型共 {len(STANDARD_ENERGY_TYPES)} 种")
    print("🗺️ 同时进行完整地域标签识别")
    print()
    
    # 处理每篇文章
    normalized_articles = []
    energy_type_stats = {}
    region_stats = {}
    
    for i, article in enumerate(original_data):
        print(f"处理第 {i+1} 篇: {article['标题'][:50]}...")
        
        # 分析能源类型
        detected_energy_types = analyze_energy_types_from_content(
            article['标题'], 
            article['文章内容']
        )
        
        # 🗺️ 使用完整地域数据分析地域标签
        article_text = article['标题'] + " " + article['文章内容']
        found_regions = find_regions_in_text(article_text)
        
        # 选择最佳地域标签（优先高级别地域）
        selected_regions = []
        if found_regions:
            # 按级别和权重排序，选择前2个最重要的地域
            found_regions.sort(key=lambda x: (x["level"], x["weight"]), reverse=True)
            selected_regions = [r["name"] for r in found_regions[:2]]
            
            print(f"   发现地域: {[r['name'] for r in found_regions[:3]]}")
            print(f"   选择地域: {selected_regions}")
        
        # 统计能源类型
        for energy_type in detected_energy_types:
            energy_type_stats[energy_type] = energy_type_stats.get(energy_type, 0) + 1
        
        # 统计地域分布
        for region in selected_regions:
            region_stats[region] = region_stats.get(region, 0) + 1
        
        # 创建规范化的文章数据
        normalized_article = article.copy()
        normalized_article['能源品种标签'] = detected_energy_types
        normalized_article['规范化地域标签'] = selected_regions  # 新增规范化地域标签
        
        normalized_articles.append(normalized_article)
        print()
    
    # 保存规范化数据
    output_file = os.path.join(os.path.dirname(__file__), "信息发布文章与标签_规范化.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(normalized_articles, f, ensure_ascii=False, indent=2)
    
    # 输出统计信息
    print("✅ 能源品种和地域标签规范化完成！")
    print(f"💾 规范化数据已保存到：{output_file}")
    print()
    
    print("📈 能源类型分布统计：")
    sorted_energy_stats = sorted(energy_type_stats.items(), key=lambda x: x[1], reverse=True)
    for energy_type, count in sorted_energy_stats:
        percentage = (count / len(normalized_articles)) * 100
        print(f"   {energy_type}: {count} 篇 ({percentage:.1f}%)")
    
    print()
    print("🗺️ 地域分布统计（TOP 15）：")
    sorted_region_stats = sorted(region_stats.items(), key=lambda x: x[1], reverse=True)
    for i, (region, count) in enumerate(sorted_region_stats[:15]):
        percentage = (count / len(normalized_articles)) * 100
        print(f"   {region}: {count} 篇 ({percentage:.1f}%)")
    
    print()
    print("🔍 规范化效果预览（前5篇文章）：")
    for i, article in enumerate(normalized_articles[:5]):
        print(f"\n{i+1}. {article['标题'][:60]}...")
        print(f"   文档类型: {article['文档类型']}")
        print(f"   能源品种: {article['能源品种标签']}")
        print(f"   地域标签: {article.get('规范化地域标签', [])}")
    
    # 输出覆盖率统计
    articles_with_energy = sum(1 for article in normalized_articles if article.get('能源品种标签'))
    articles_with_region = sum(1 for article in normalized_articles if article.get('规范化地域标签'))
    
    print()
    print("📊 标签覆盖率：")
    print(f"   能源标签覆盖率: {articles_with_energy}/{len(normalized_articles)} ({articles_with_energy/len(normalized_articles)*100:.1f}%)")
    print(f"   地域标签覆盖率: {articles_with_region}/{len(normalized_articles)} ({articles_with_region/len(normalized_articles)*100:.1f}%)")
    
    return output_file

def create_energy_mapping_report():
    """
    创建能源类型映射报告，帮助验证规范化效果
    """
    print("\n📋 能源类型关键词映射表：")
    print("=" * 80)
    
    for energy_type in STANDARD_ENERGY_TYPES:
        keywords = ENERGY_TYPE_KEYWORDS.get(energy_type, [])
        print(f"\n🔹 {energy_type}")
        print(f"   关键词({len(keywords)}个): {', '.join(keywords[:8])}")
        if len(keywords) > 8:
            print(f"   ...")
    
    print("\n" + "=" * 80)
    print("💡 检测逻辑说明：")
    print("   1. 优先检测更具体的类型（如LNG优先于天然气）")
    print("   2. 每篇文章最多保留3个能源类型") 
    print("   3. 根据标题和内容的关键词匹配进行判断")
    print("   4. 如果检测到LNG或PNG，会自动移除通用的'天然气'标签")

if __name__ == "__main__":
    print("🔧 能源品种标签规范化工具")
    print("=" * 50)
    
    # 显示映射规则
    create_energy_mapping_report()
    
    print("\n" + "=" * 50)
    print("开始处理...")
    
    # 执行规范化
    output_file = normalize_energy_tags_in_articles()
    
    print(f"\n🎉 处理完成！规范化文件: {output_file}")
    print("\n📝 下一步建议：")
    print("   1. 检查规范化结果")
    print("   2. 运行 python simplify_test_data.py 使用新数据")
    print("   3. 重新导入数据到系统") 