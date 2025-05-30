import json
import random
import os
from typing import List, Dict, Any
from china_regions import find_regions_in_text, classify_region_type

def parse_tag_string(tag_str: str) -> List[str]:
    """解析标签字符串，处理各种格式"""
    if not tag_str:
        return []
    
    # 移除外层的单引号和方括号
    tag_str = tag_str.strip()
    if tag_str.startswith("[") and tag_str.endswith("]"):
        # 处理 "['tag1', 'tag2']" 格式
        try:
            import ast
            return ast.literal_eval(tag_str)
        except:
            # 如果解析失败，手动处理
            content = tag_str[1:-1]  # 移除 []
            if content:
                # 处理引号
                if content.startswith("'") and content.endswith("'"):
                    content = content[1:-1]
                tags = [tag.strip().strip("'\"") for tag in content.split("',")]
                return [tag for tag in tags if tag]
    
    return []

def simplify_article_tags(article: Dict[str, Any]) -> Dict[str, Any]:
    """简化单篇文章的标签，重点保留地域和能源类型，控制总数在3-5个"""
    
    # 🔋 处理能源类型标签 - 优先使用规范化后的数据
    if "能源品种标签" in article and article["能源品种标签"]:
        # 使用规范化后的能源类型
        energy_type_tags = article["能源品种标签"][:2]  # 最多保留2个能源类型
        print(f"   使用规范化能源类型: {energy_type_tags}")
    else:
        # 回退到原始标签解析
        original_tags = parse_tag_string(article.get("地域标签", ""))
        energy_type_tags = []
        for tag in original_tags:
            if any(keyword in tag for keyword in ["天然气", "原油", "汽油", "柴油", "电力", "煤炭", "LNG", "LPG"]):
                energy_type_tags.append(tag)
        energy_type_tags = energy_type_tags[:2]  # 最多2个
    
    # 🏛️ 使用完整地域数据进行地域标签识别
    article_text = article.get("标题", "") + " " + article.get("文章内容", "")
    
    # 🎯 优先使用规范化后的地域标签
    if "规范化地域标签" in article and article["规范化地域标签"]:
        # 使用规范化后的地域标签
        selected_regions = article["规范化地域标签"][:2]  # 最多2个
        print(f"   使用规范化地域标签: {selected_regions}")
    else:
        # 回退到实时地域识别
        found_regions = find_regions_in_text(article_text)
        
        # 解析原始地域标签（作为补充）
        original_region_tags = parse_tag_string(article.get("地域标签", ""))
        
        # 合并发现的地域和原始标签
        all_region_candidates = []
        
        # 添加从文本中发现的地域
        for region_info in found_regions:
            all_region_candidates.append({
                "name": region_info["name"],
                "weight": region_info["weight"],
                "level": region_info["level"],
                "type": region_info["type"],
                "source": "text_analysis"
            })
        
        # 添加原始标签中的地域（给予较低权重）
        for tag in original_region_tags:
            region_info = classify_region_type(tag)
            if region_info["type"] != "unknown":
                # 避免重复
                if not any(candidate["name"] == tag for candidate in all_region_candidates):
                    all_region_candidates.append({
                        "name": tag,
                        "weight": region_info["weight"] * 0.8,  # 原始标签权重降低
                        "level": region_info["level"],
                        "type": region_info["type"],
                        "source": "original_tags"
                    })
        
        # 按权重和级别排序，选择最佳地域标签
        all_region_candidates.sort(key=lambda x: (x["level"], x["weight"]), reverse=True)
        
        # 🎯 地域标签选择策略
        selected_regions = []
        
        # 1. 优先选择直辖市和省会城市（level=4, weight>=2.5）
        high_level_regions = [r for r in all_region_candidates if r["level"] == 4 and r["weight"] >= 2.5]
        if high_level_regions:
            selected_regions.append(high_level_regions[0]["name"])
        
        # 2. 如果没有高级别城市，选择省份级别的地域
        if not selected_regions:
            province_regions = [r for r in all_region_candidates if r["level"] == 3]
            if province_regions:
                selected_regions.append(province_regions[0]["name"])
        
        # 3. 最多再添加一个重要地域（避免过多地域标签）
        remaining_regions = [r for r in all_region_candidates 
                            if r["name"] not in selected_regions and r["weight"] >= 1.5]
        if remaining_regions and len(selected_regions) < 2:
            selected_regions.append(remaining_regions[0]["name"])
        
        print(f"   实时识别地域标签: {selected_regions}")
    
    # 🏭 处理其他类型标签
    original_tags = parse_tag_string(article.get("业务领域/主题标签", ""))
    business_tags = []
    importance_tags = []
    
    for tag in original_tags:
        if any(keyword in tag for keyword in ["发电", "炼化", "储运", "销售", "贸易", "运输", "配送", "零售"]):
            business_tags.append(tag)
        elif any(keyword in tag for keyword in ["重大", "重要", "关键", "核心", "政策", "法规"]):
            importance_tags.append(tag)
    
    # ⚖️ 标签数量平衡策略（目标：3-5个总标签）
    selected_tags = {
        "region_tags": selected_regions[:2],  # 最多2个地域标签
        "energy_type_tags": energy_type_tags,
        "business_field_tags": business_tags[:1],  # 最多1个业务标签
        "basic_info_tags": [article.get("文档类型", "")] if article.get("文档类型") else [],
        "importance_tags": []
    }
    
    # 计算当前标签总数
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
    
    # 📊 输出地域识别详情
    found_regions = []  # 确保变量总是被定义
    if "规范化地域标签" in article and article["规范化地域标签"]:
        # 使用规范化后的地域标签时，found_regions为空（因为没有实时识别）
        pass
    else:
        # 只有在实时识别时才有found_regions数据
        found_regions = find_regions_in_text(article_text)
    
    if found_regions:
        print(f"   发现地域标签: {[r['name'] for r in found_regions[:3]]}")
    
    print(f"   最终选择地域: {selected_regions}")
    
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