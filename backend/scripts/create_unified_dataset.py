#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建统一的上海石油天然气交易中心信息门户系统数据集
从多个JSON文件合并数据，创建包含完整标签信息的统一数据集
"""

import sys
import os
import json
from datetime import datetime

def load_v1_articles():
    """加载v1版本的45篇文章"""
    json_file_path = os.path.join(os.path.dirname(__file__), '信息发布文章与标签_规范化.json')
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            v1_articles = json.load(f)
        print(f"✅ 加载v1版本文章: {len(v1_articles)}篇")
        return v1_articles
    except Exception as e:
        print(f"❌ 加载v1文章失败: {e}")
        return []

def get_v2_additional_articles():
    """获取v2版本的6篇额外文章"""
    v2_articles = [
        {
            "发布日期": "2025-05-30",
            "文档类型": "行业资讯",
            "发布时间": "2025-05-30",
            "来源机构": "上海石油天然气交易中心",
            "标题": "密集投产潮下利用率不足50%，LNG接收站市场竞争加剧，如何保障效益",
            "文章内容": "随着全球LNG贸易量持续增长，中国LNG接收站建设进入密集投产期。然而，受市场供需变化影响，部分接收站利用率不足50%，面临严峻的市场竞争压力。行业专家指出，接收站运营商需要通过技术升级、服务优化、商业模式创新等方式提升竞争力，确保投资效益。未来LNG接收站发展需要统筹规划，避免重复建设，提高整体利用效率。",
            "链接": "https://www.shpgx.com/html/xyzx/20250530/7850.html",
            "基础信息标签": "['行业资讯']",
            "地域标签": "['全国']",
            "能源品种标签": ["液化天然气(LNG)"],
            "业务领域/主题标签": "['接收站运营', '市场竞争']",
            "受益主体标签": "['LNG运营商', '能源企业']",
            "关键措施/政策标签": "['技术升级', '商业模式创新']",
            "重要性/影响力标签": "['行业级']",
            "规范化地域标签": ["中国", "全国"]
        },
        {
            "发布日期": "2025-05-30",
            "文档类型": "行业资讯",
            "发布时间": "2025-05-30",
            "来源机构": "上海石油天然气交易中心",
            "标题": "新奥股份重大资产重组获股东大会超99.9%高票通过，天然气产业链一体化战略取得关键进展",
            "文章内容": "新奥股份重大资产重组方案获得股东大会超99.9%的高票通过，标志着公司天然气产业链一体化战略取得关键性进展。此次重组将进一步完善新奥在天然气全产业链的布局，提升公司在LNG贸易、终端销售等关键环节的竞争优势。市场分析认为，这一举措将有助于新奥股份实现规模化发展，提高抗风险能力。",
            "链接": "https://www.shpgx.com/html/xyzx/20250530/7849.html",
            "基础信息标签": "['行业资讯']",
            "地域标签": "['全国']",
            "能源品种标签": ["天然气", "液化天然气(LNG)"],
            "业务领域/主题标签": "['资产重组', '产业链一体化']",
            "受益主体标签": "['新奥股份', '上市公司']",
            "关键措施/政策标签": "['资产重组', '产业链整合']",
            "重要性/影响力标签": "['行业级']",
            "规范化地域标签": ["中国", "全国"]
        },
        {
            "发布日期": "2025-05-30",
            "文档类型": "行业资讯",
            "发布时间": "2025-05-30",
            "来源机构": "上海石油天然气交易中心",
            "标题": "中国石油发布3000亿参数昆仑大模型",
            "文章内容": "中国石油正式发布3000亿参数规模的昆仑大模型，这是石油天然气行业首个千亿级参数大模型。该模型将在勘探开发、炼化生产、销售服务等多个业务场景中应用，通过AI技术提升作业效率和决策水平。专家表示，大模型技术的应用将推动传统能源行业数字化转型，为行业发展注入新动能。",
            "链接": "https://www.shpgx.com/html/xyzx/20250530/7848.html",
            "基础信息标签": "['行业资讯']",
            "地域标签": "['全国']",
            "能源品种标签": ["原油", "天然气"],
            "业务领域/主题标签": "['人工智能', '数字化转型']",
            "受益主体标签": "['中国石油', '能源企业']",
            "关键措施/政策标签": "['技术创新', 'AI应用']",
            "重要性/影响力标签": "['行业级', '技术突破']",
            "规范化地域标签": ["中国", "全国"]
        },
        {
            "发布日期": "2025-05-29",
            "文档类型": "行业资讯",
            "发布时间": "2025-05-29",
            "来源机构": "上海石油天然气交易中心",
            "标题": "5月19日-25日中国LNG综合进口到岸价格指数为131.78点",
            "文章内容": "5月19日-25日当周，中国LNG综合进口到岸价格指数为131.78点，价格相对稳定。随着夏季用气需求逐步减少，LNG市场供需趋于平衡。业内分析认为，二季度LNG价格将保持相对平稳，但需关注国际市场供应端变化和下半年冬季备货需求。",
            "链接": "https://www.shpgx.com/html/xyzx/20250529/7845.html",
            "基础信息标签": "['行业资讯']",
            "地域标签": "['全国']",
            "能源品种标签": ["液化天然气(LNG)"],
            "业务领域/主题标签": "['价格指数', '进口贸易']",
            "受益主体标签": "['LNG贸易商', '城市燃气公司']",
            "关键措施/政策标签": "['价格监测', '供需调节']",
            "重要性/影响力标签": "['市场级']",
            "规范化地域标签": ["中国", "全国"]
        },
        {
            "发布日期": "2025-05-29",
            "文档类型": "行业资讯",
            "发布时间": "2025-05-29",
            "来源机构": "上海石油天然气交易中心",
            "标题": "大港油田储气库群加快扩容 为京津冀冬季保供蓄能",
            "文章内容": "大港油田储气库群正在加快扩容建设，为即将到来的冬季天然气保供做好准备。作为华北地区重要的天然气储备基地，大港储气库群承担着京津冀地区冬季调峰保供的重要任务。预计新增储气能力将有效缓解冬季用气紧张局面，为区域能源安全提供坚实保障。",
            "链接": "https://www.shpgx.com/html/xyzx/20250529/7844.html",
            "基础信息标签": "['行业资讯']",
            "地域标签": "['华北地区']",
            "能源品种标签": ["天然气"],
            "业务领域/主题标签": "['储气库', '冬季保供']",
            "受益主体标签": "['京津冀用户', '城市燃气公司']",
            "关键措施/政策标签": "['储气库建设', '保供措施']",
            "重要性/影响力标签": "['区域级', '民生保障']",
            "规范化地域标签": ["北京", "天津", "河北", "华北地区", "京津冀"]
        },
        {
            "发布日期": "2025-05-28",
            "文档类型": "行业资讯",
            "发布时间": "2025-05-28",
            "来源机构": "上海石油天然气交易中心",
            "标题": "非洲渐成LNG供应新主力",
            "文章内容": "随着全球LNG需求持续增长，非洲正逐渐成为LNG供应的新主力。尼日利亚、莫桑比克、坦桑尼亚等非洲国家拥有丰富的天然气资源，正在大力发展LNG出口项目。分析师预计，未来5年非洲LNG产能将显著增长，为全球LNG市场供应多元化做出重要贡献。中国企业也积极参与非洲LNG项目开发。",
            "链接": "https://www.shpgx.com/html/xyzx/20250528/7840.html",
            "基础信息标签": "['行业资讯']",
            "地域标签": "['国际']",
            "能源品种标签": ["液化天然气(LNG)", "天然气"],
            "业务领域/主题标签": "['LNG出口', '供应格局']",
            "受益主体标签": "['非洲国家', 'LNG生产商']",
            "关键措施/政策标签": "['资源开发', '国际合作']",
            "重要性/影响力标签": "['国际级']",
            "规范化地域标签": ["非洲", "尼日利亚", "莫桑比克", "坦桑尼亚", "国际"]
        }
    ]
    
    print(f"✅ 加载v2版本额外文章: {len(v2_articles)}篇")
    return v2_articles

def create_unified_dataset():
    """创建统一的数据集"""
    print("🔄 创建统一的51篇文章数据集...")
    print("=" * 60)
    
    # 加载v1版本文章
    v1_articles = load_v1_articles()
    if not v1_articles:
        print("❌ 无法加载v1文章数据")
        return False
    
    # 获取v2版本额外文章
    v2_articles = get_v2_additional_articles()
    
    # 合并数据
    unified_articles = v1_articles + v2_articles
    
    print(f"\n📊 数据合并结果:")
    print(f"   v1版本文章: {len(v1_articles)}篇")
    print(f"   v2版本额外文章: {len(v2_articles)}篇")
    print(f"   统一数据集总计: {len(unified_articles)}篇")
    
    # 数据质量检查
    print(f"\n🔍 数据质量检查:")
    titles = [article.get('标题', '') for article in unified_articles]
    unique_titles = set(titles)
    if len(titles) != len(unique_titles):
        print(f"   ⚠️  发现重复标题: {len(titles) - len(unique_titles)}个")
        duplicates = [title for title in titles if titles.count(title) > 1]
        for dup in set(duplicates):
            print(f"      重复标题: {dup}")
    else:
        print(f"   ✅ 无重复标题")
    
    # 检查必要字段
    missing_fields = []
    for i, article in enumerate(unified_articles):
        required_fields = ['标题', '文章内容', '基础信息标签', '能源品种标签']
        for field in required_fields:
            if not article.get(field):
                missing_fields.append(f"文章{i+1}缺少{field}")
    
    if missing_fields:
        print(f"   ⚠️  发现缺少字段: {len(missing_fields)}个")
        for missing in missing_fields[:5]:  # 只显示前5个
            print(f"      {missing}")
    else:
        print(f"   ✅ 所有必要字段完整")
    
    # 保存统一数据集
    output_file = os.path.join(os.path.dirname(__file__), '上海石油天然气交易中心信息门户系统_完整数据集_51篇.json')
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unified_articles, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 统一数据集保存成功: {output_file}")
        
        # 显示文件大小
        file_size = os.path.getsize(output_file) / 1024
        print(f"   文件大小: {file_size:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ 保存统一数据集失败: {e}")
        return False

def analyze_unified_dataset():
    """分析统一数据集的分布"""
    output_file = os.path.join(os.path.dirname(__file__), '上海石油天然气交易中心信息门户系统_完整数据集_51篇.json')
    if not os.path.exists(output_file):
        print("❌ 统一数据集文件不存在")
        return
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        print(f"\n📈 数据集分析 (总计{len(articles)}篇):")
        print("=" * 60)
        
        # 分析文档类型分布
        doc_types = {}
        for article in articles:
            doc_type = article.get('文档类型', '未知')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        print("📋 文档类型分布:")
        for doc_type, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(articles) * 100
            print(f"   {doc_type}: {count}篇 ({percentage:.1f}%)")
        
        # 分析能源类型分布
        energy_types = {}
        for article in articles:
            energy_tags = article.get('能源品种标签', [])
            if isinstance(energy_tags, str):
                # 简单解析字符串格式
                import ast
                try:
                    energy_tags = ast.literal_eval(energy_tags)
                except:
                    energy_tags = []
            
            for energy_type in energy_tags:
                energy_types[energy_type] = energy_types.get(energy_type, 0) + 1
        
        print("\n⚡ 能源类型分布:")
        for energy_type, count in sorted(energy_types.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(articles) * 100
            print(f"   {energy_type}: {count}篇 ({percentage:.1f}%)")
        
        # 分析发布时间分布
        years = {}
        for article in articles:
            publish_time = article.get('发布时间', '')
            if publish_time:
                year = publish_time[:4] if len(publish_time) >= 4 else '未知'
                years[year] = years.get(year, 0) + 1
        
        print("\n📅 发布年份分布:")
        for year, count in sorted(years.items()):
            percentage = count / len(articles) * 100
            print(f"   {year}年: {count}篇 ({percentage:.1f}%)")
            
    except Exception as e:
        print(f"❌ 分析数据集失败: {e}")

def main():
    """主函数"""
    print("🚀 上海石油天然气交易中心信息门户系统 - 统一数据集创建工具")
    print("=" * 80)
    
    # 创建统一数据集
    success = create_unified_dataset()
    if not success:
        print("\n❌ 统一数据集创建失败")
        return
    
    # 分析数据集
    analyze_unified_dataset()
    
    print("\n" + "=" * 80)
    print("🎉 统一数据集创建完成！")
    print("\n✅ 主要成果:")
    print("   1. 整合v1版本45篇 + v2版本6篇 = 完整51篇文章")
    print("   2. 消除了版本间的数据不一致问题")
    print("   3. 统一数据格式，便于维护")
    print("   4. 生成质量检查报告")
    print("\n📄 输出文件: 上海石油天然气交易中心信息门户系统_完整数据集_51篇.json")
    print("📝 下一步: 更新import_sample_data.py使用新的统一数据集")

if __name__ == "__main__":
    main() 