#!/usr/bin/env python3
"""
分析各类标签的基础元素构成
"""
import json
import ast
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_parse_tags(tag_string):
    """安全解析标签字符串"""
    if not tag_string:
        return []
    
    try:
        # 使用ast.literal_eval安全解析
        tags = ast.literal_eval(tag_string)
        if isinstance(tags, list):
            return [str(tag).strip() for tag in tags if tag and str(tag).strip()]
        elif isinstance(tags, str):
            return [tags.strip()]
        else:
            return []
    except (ValueError, SyntaxError) as e:
        logger.warning(f"解析标签失败: {tag_string}, 错误: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"未知错误解析标签: {tag_string}, 错误: {str(e)}")
        return []

def analyze_tag_elements():
    """分析标签基础元素"""
    
    print("🔍 分析标签基础元素构成")
    print("="*60)
    
    # 读取数据文件
    try:
        with open('scripts/信息发布文章与标签_规范化.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ 成功读取 {len(data)} 篇文章数据")
    except FileNotFoundError:
        print("❌ 数据文件不存在: scripts/信息发布文章与标签_规范化.json")
        return
    except Exception as e:
        print(f"❌ 读取数据文件失败: {str(e)}")
        return
    
    # 收集所有标签
    basic_tags = set()
    business_tags = set()
    policy_tags = set()
    importance_tags = set()
    energy_tags = set()
    
    # 统计解析失败的文章
    failed_parse_count = 0
    
    for i, article in enumerate(data):
        try:
            # 基础信息标签 - 使用安全解析
            if '基础信息标签' in article and article['基础信息标签']:
                tags = safe_parse_tags(article['基础信息标签'])
                basic_tags.update(tags)
            
            # 业务领域标签
            if '业务领域标签' in article and article['业务领域标签']:
                tags = safe_parse_tags(article['业务领域标签'])
                business_tags.update(tags)
            
            # 政策措施标签
            if '关键措施标签' in article and article['关键措施标签']:
                tags = safe_parse_tags(article['关键措施标签'])
                policy_tags.update(tags)
            
            # 重要性标签
            if '重要性标签' in article and article['重要性标签']:
                tags = safe_parse_tags(article['重要性标签'])
                importance_tags.update(tags)
            
            # 能源品种标签
            if '能源品种标签' in article and article['能源品种标签']:
                if isinstance(article['能源品种标签'], list):
                    energy_tags.update(article['能源品种标签'])
                elif isinstance(article['能源品种标签'], str):
                    tags = safe_parse_tags(article['能源品种标签'])
                    energy_tags.update(tags)
                    
        except Exception as e:
            failed_parse_count += 1
            logger.error(f"解析第 {i+1} 篇文章失败: {str(e)}")
    
    if failed_parse_count > 0:
        print(f"⚠️ {failed_parse_count} 篇文章解析失败")
    
    print('\n🏷️ 基础信息标签 (basic_info_tags):')
    print(f'   总数: {len(basic_tags)} 个')
    for tag in sorted(basic_tags):
        print(f'   - {tag}')
    
    print('\n⚡ 能源类型标签 (energy_type_tags):')
    print(f'   总数: {len(energy_tags)} 个')
    for tag in sorted(energy_tags):
        print(f'   - {tag}')
    
    print('\n🏢 业务领域标签 (business_field_tags):')
    print(f'   总数: {len(business_tags)} 个')
    for tag in sorted(business_tags):
        print(f'   - {tag}')
    
    print('\n📋 政策措施标签 (policy_measure_tags):')
    print(f'   总数: {len(policy_tags)} 个')
    for tag in sorted(policy_tags):
        print(f'   - {tag}')
    
    print('\n⭐ 重要性标签 (importance_tags):')
    print(f'   总数: {len(importance_tags)} 个')
    for tag in sorted(importance_tags):
        print(f'   - {tag}')
    
    print(f"\n📊 标签统计汇总:")
    print(f"   基础信息标签: {len(basic_tags)} 个")
    print(f"   能源类型标签: {len(energy_tags)} 个")
    print(f"   业务领域标签: {len(business_tags)} 个")
    print(f"   政策措施标签: {len(policy_tags)} 个")
    print(f"   重要性标签: {len(importance_tags)} 个")
    print(f"   总计: {len(basic_tags) + len(energy_tags) + len(business_tags) + len(policy_tags) + len(importance_tags)} 个标签类型")
    print(f"\n✅ 标签分析完成，使用安全的ast.literal_eval()解析")

if __name__ == "__main__":
    analyze_tag_elements() 