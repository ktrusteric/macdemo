#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import ast
from typing import List, Dict, Any

def clean_duplicate_fields():
    """
    移除重复的文档类型字段，统一使用基础信息标签
    1. 删除"文档类型"字段
    2. 确保"基础信息标签"格式正确
    3. 验证数据一致性
    """
    
    # 读取完整数据集
    with open('上海石油天然气交易中心信息门户系统_完整数据集_51篇.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    print('🔧 清理重复字段：文档类型 vs 基础信息标签')
    print('=' * 60)
    
    # 统计信息
    duplicate_count = 0
    cleaned_articles = []
    issues = []
    
    for i, article in enumerate(articles):
        # 获取原始字段
        doc_type = article.get('文档类型', '')
        basic_info_str = article.get('基础信息标签', '')
        
        # 解析基础信息标签
        basic_info_tags = []
        if isinstance(basic_info_str, str) and basic_info_str.strip():
            try:
                if basic_info_str.startswith('['):
                    basic_info_tags = ast.literal_eval(basic_info_str)
                else:
                    basic_info_tags = [basic_info_str]
            except:
                basic_info_tags = [basic_info_str]
        elif isinstance(basic_info_str, list):
            basic_info_tags = basic_info_str
        
        # 检查重复性
        is_duplicate = (len(basic_info_tags) == 1 and basic_info_tags[0] == doc_type)
        if is_duplicate:
            duplicate_count += 1
        
        # 数据一致性检查
        if doc_type and not basic_info_tags:
            # 如果有文档类型但没有基础信息标签，使用文档类型填充
            basic_info_tags = [doc_type]
            issues.append(f'文章{i+1}: 补充缺失的基础信息标签: {doc_type}')
        elif not doc_type and basic_info_tags:
            # 正常情况，有基础信息标签
            pass
        elif doc_type and basic_info_tags and not is_duplicate:
            # 不一致的情况，优先保留基础信息标签
            issues.append(f'文章{i+1}: 字段不一致，保留基础信息标签: {basic_info_tags}')
        
        # 清理文章数据
        cleaned_article = {k: v for k, v in article.items() if k != '文档类型'}
        
        # 确保基础信息标签为数组格式
        if basic_info_tags:
            cleaned_article['basic_info_tags'] = basic_info_tags
        
        # 删除旧的中文字段名，使用英文标准字段
        if '基础信息标签' in cleaned_article:
            if 'basic_info_tags' not in cleaned_article:
                cleaned_article['basic_info_tags'] = basic_info_tags
            del cleaned_article['基础信息标签']
        
        cleaned_articles.append(cleaned_article)
        
        if i < 5:  # 显示前5篇的处理情况
            print(f'文章{i+1:2d}: 原文档类型="{doc_type}" | 基础信息标签={basic_info_tags} | {"✅删除重复" if is_duplicate else "⚠️不一致"}')
    
    print(f'\n📊 清理统计:')
    print(f'总文章数: {len(articles)}')
    print(f'重复字段数: {duplicate_count}')
    print(f'重复比例: {duplicate_count/len(articles)*100:.1f}%')
    print(f'发现问题: {len(issues)}')
    
    if issues:
        print(f'\n⚠️ 数据问题清单:')
        for issue in issues[:10]:  # 只显示前10个
            print(f'  {issue}')
        if len(issues) > 10:
            print(f'  ... 还有 {len(issues)-10} 个问题')
    
    # 验证清理后的数据
    basic_info_distribution = {}
    for article in cleaned_articles:
        basic_tags = article.get('basic_info_tags', [])
        for tag in basic_tags:
            basic_info_distribution[tag] = basic_info_distribution.get(tag, 0) + 1
    
    print(f'\n📋 清理后基础信息标签分布:')
    for tag, count in sorted(basic_info_distribution.items()):
        print(f'  {tag}: {count}篇')
    
    # 保存清理后的数据
    output_file = '上海石油天然气交易中心信息门户系统_清理重复字段_51篇.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_articles, f, ensure_ascii=False, indent=2)
    
    print(f'\n✅ 清理完成！')
    print(f'📁 输出文件: {output_file}')
    print(f'🗑️  已删除字段: "文档类型"')
    print(f'📝 已标准化字段: "基础信息标签" → "basic_info_tags"')
    
    return cleaned_articles, basic_info_distribution

def validate_cleaned_data():
    """验证清理后的数据质量"""
    try:
        with open('上海石油天然气交易中心信息门户系统_清理重复字段_51篇.json', 'r', encoding='utf-8') as f:
            cleaned_data = json.load(f)
        
        print(f'\n🔍 数据验证:')
        print(f'文章总数: {len(cleaned_data)}')
        
        # 检查字段存在性
        has_doc_type = sum(1 for article in cleaned_data if '文档类型' in article)
        has_basic_info = sum(1 for article in cleaned_data if 'basic_info_tags' in article)
        
        print(f'包含"文档类型"字段的文章: {has_doc_type} (应为0)')
        print(f'包含"basic_info_tags"字段的文章: {has_basic_info}')
        
        if has_doc_type == 0:
            print('✅ "文档类型"字段已完全移除')
        else:
            print('❌ 仍有"文档类型"字段残留')
        
        return cleaned_data
        
    except FileNotFoundError:
        print('❌ 清理后的文件不存在，请先运行清理流程')
        return None

if __name__ == '__main__':
    # 执行清理
    cleaned_articles, distribution = clean_duplicate_fields()
    
    # 验证结果
    validate_cleaned_data()
    
    print(f'\n🎯 总结:')
    print(f'✅ 成功移除重复的"文档类型"字段')
    print(f'✅ 统一使用"basic_info_tags"标准字段')
    print(f'✅ 数据格式标准化完成')
    print(f'✅ 为后续前后端统一奠定基础') 