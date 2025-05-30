import json
import random
import os
from typing import List, Dict, Any

def parse_tag_string(tag_str: str) -> List[str]:
    """解析标签字符串，处理各种格式"""
    if not tag_str:
        return []
    
    # 移除外层的单引号和方括号
    tag_str = tag_str.strip()
    if tag_str.startswith("['") and tag_str.endswith("']"):
        # 处理 "['tag1', 'tag2']" 格式
        try:
            import ast
            return ast.literal_eval(tag_str)
        except:
            # 如果解析失败，手动处理
            content = tag_str[2:-2]  # 移除 ['']
            if content:
                tags = [tag.strip().strip("'\"") for tag in content.split("',")]
                return [tag for tag in tags if tag]
    
    return []

def simplify_article_tags(article: Dict[str, Any]) -> Dict[str, Any]:
    """简化单篇文章的标签，重点保留地域和能源类型，控制总数在3-5个"""
    
    # 解析各类标签
    region_tags = []
    industry_tags = []
    beneficiary_tags = []
    policy_tags = []
    importance_tags = []
    business_tags = []
    
    # 处理原始标签格式
    original_tags = parse_tag_string(article.get("地域标签", ""))
    
    # 🔋 处理能源类型标签 - 优先使用规范化后的数据
    if "能源品种标签" in article and article["能源品种标签"]:
        # 使用规范化后的能源类型
        energy_type_tags = article["能源品种标签"][:2]  # 最多保留2个能源类型
        print(f"   使用规范化能源类型: {energy_type_tags}")
    else:
        # 回退到原始标签解析
        energy_type_tags = []
        for tag in original_tags:
            if any(keyword in tag for keyword in ["天然气", "原油", "汽油", "柴油", "电力", "煤炭", "LNG", "LPG"]):
                energy_type_tags.append(tag)
        energy_type_tags = energy_type_tags[:2]  # 最多2个
    
    # 🏛️ 地域标签解析和优先级处理
    for tag in original_tags:
        tag_lower = tag.lower()
        
        # 城市级地域标签（优先级最高）
        if any(city in tag for city in ["北京", "上海", "广州", "深圳", "杭州", "苏州", "成都", "武汉", "重庆", "西安", "天津"]):
            region_tags.append(tag)
        # 省份级地域标签
        elif any(province in tag for province in ["江苏", "浙江", "广东", "山东", "河北", "四川", "湖北", "湖南", "安徽", "河南"]):
            region_tags.append(tag)
        # 其他地域相关
        elif any(keyword in tag for keyword in ["市", "省", "区域", "地区", "华东", "华南", "华北", "华中", "西部", "东部"]):
            if tag not in ["全国", "国内", "国际"]:  # 排除过于泛化的标签
                region_tags.append(tag)
    
    # 🏭 业务领域标签
    for tag in original_tags:
        if any(keyword in tag for keyword in ["发电", "炼化", "储运", "销售", "贸易", "运输", "配送", "零售"]):
            business_tags.append(tag)
    
    # 📊 重要性和政策标签（优先级较低）
    for tag in original_tags:
        if any(keyword in tag for keyword in ["重大", "重要", "关键", "核心"]):
            importance_tags.append(tag)
        elif any(keyword in tag for keyword in ["政策", "法规", "通知", "办法", "规定"]):
            policy_tags.append(tag)
    
    # ⚖️ 标签数量平衡策略（目标：3-5个总标签）
    selected_tags = {
        "region_tags": [],
        "energy_type_tags": energy_type_tags,
        "business_field_tags": [],
        "basic_info_tags": [],
        "importance_tags": []
    }
    
    # 1. 地域标签：最多2个，优先城市
    city_regions = [tag for tag in region_tags if any(city in tag for city in ["北京", "上海", "广州", "深圳", "杭州", "苏州"])]
    province_regions = [tag for tag in region_tags if tag not in city_regions]
    
    selected_tags["region_tags"].extend(city_regions[:1])  # 最多1个城市
    if len(selected_tags["region_tags"]) < 2:
        selected_tags["region_tags"].extend(province_regions[:2-len(selected_tags["region_tags"])])
    
    # 2. 业务领域：最多1个
    selected_tags["business_field_tags"] = business_tags[:1]
    
    # 3. 基础信息：文档类型
    doc_type = article.get("文档类型", "")
    if doc_type:
        selected_tags["basic_info_tags"] = [doc_type]
    
    # 4. 控制总标签数不超过5个
    current_total = (
        len(selected_tags["region_tags"]) +
        len(selected_tags["energy_type_tags"]) +
        len(selected_tags["business_field_tags"]) +
        len(selected_tags["basic_info_tags"])
    )
    
    # 如果总数少于3个，添加重要性标签
    if current_total < 3 and importance_tags:
        available_slots = min(3 - current_total, len(importance_tags))
        selected_tags["importance_tags"] = importance_tags[:available_slots]
    
    # 创建简化的文章数据
    simplified_article = article.copy()
    simplified_article.update(selected_tags)
    
    return simplified_article

def create_simplified_data():
    """创建简化的测试数据"""
    
    # 优先使用规范化后的数据
    normalized_file = os.path.join(os.path.dirname(__file__), "信息发布文章与标签_规范化.json")
    original_file = os.path.join(os.path.dirname(__file__), "信息发布文章与标签.json")
    
    if os.path.exists(normalized_file):
        input_file = normalized_file
        print("🎯 使用规范化后的能源标签数据")
    else:
        input_file = original_file
        print("⚠️  使用原始数据（建议先运行 normalize_energy_tags.py）")
    
    if not os.path.exists(input_file):
        print("❌ 找不到数据文件")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    print(f"📊 原始数据：{len(original_data)} 篇文章")
    
    # 简化数据
    simplified_articles = []
    tag_stats = {"total": 0, "min": 100, "max": 0, "counts": []}
    
    for article in original_data:
        simplified = simplify_article_tags(article)
        simplified_articles.append(simplified)
        
        # 统计标签数量
        total_tags = (
            len(simplified.get("basic_info_tags", [])) +
            len(simplified.get("region_tags", [])) +
            len(simplified.get("energy_type_tags", [])) +
            len(simplified.get("business_field_tags", [])) +
            len(simplified.get("importance_tags", []))
        )
        tag_stats["total"] += total_tags
        tag_stats["min"] = min(tag_stats["min"], total_tags)
        tag_stats["max"] = max(tag_stats["max"], total_tags)
        tag_stats["counts"].append(total_tags)
    
    # 保存简化数据
    output_file = os.path.join(os.path.dirname(__file__), "简化测试数据.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(simplified_articles, f, ensure_ascii=False, indent=2)
    
    # 输出统计信息
    print(f"✅ 简化完成：{len(simplified_articles)} 篇文章")
    print(f"📈 标签统计：")
    print(f"   平均标签数：{tag_stats['total'] / len(simplified_articles):.1f}")
    print(f"   标签数范围：{tag_stats['min']} - {tag_stats['max']}")
    
    # 统计标签数分布
    from collections import Counter
    count_dist = Counter(tag_stats["counts"])
    print(f"   标签数分布：{dict(sorted(count_dist.items()))}")
    print()
    
    # 统计能源类型分布
    energy_type_counts = {}
    for article in simplified_articles:
        for energy_type in article.get("energy_type_tags", []):
            energy_type_counts[energy_type] = energy_type_counts.get(energy_type, 0) + 1
    
    print("🔋 能源类型分布：")
    sorted_energy = sorted(energy_type_counts.items(), key=lambda x: x[1], reverse=True)
    for energy_type, count in sorted_energy:
        percentage = (count / len(simplified_articles)) * 100
        print(f"   {energy_type}: {count} 篇 ({percentage:.1f}%)")
    print()
    
    # 显示前5篇示例
    print("📋 简化后的文章示例：")
    for i, article in enumerate(simplified_articles[:5]):
        print(f"\n{i+1}. {article['标题'][:50]}...")
        print(f"   类型: {article['文档类型']}")
        for key, name in [
            ("basic_info_tags", "基础信息"),
            ("region_tags", "地域"),
            ("energy_type_tags", "能源类型"),
            ("business_field_tags", "业务领域"),
            ("importance_tags", "重要性")
        ]:
            tags = article.get(key, [])
            if tags:
                print(f"   {name}: {tags}")
        
        total = sum(len(article.get(key, [])) for key in ["basic_info_tags", "region_tags", "energy_type_tags", "business_field_tags", "importance_tags"])
        print(f"   总标签数: {total}")
    
    print(f"\n💾 简化数据已保存到：{output_file}")
    print("\n🎯 简化策略：")
    print("   • 地域标签权重最高，优先保留具体城市/省份")
    print("   • 能源类型标签权重高，使用规范化后的标准分类")  
    print("   • 总标签数控制在3-5个，便于测试推荐效果")
    print("   • 精确区分LNG、PNG等天然气细分类型")
    return output_file

if __name__ == "__main__":
    create_simplified_data() 