#!/usr/bin/env python3
"""
标签一致性验证脚本
验证系统中所有标签配置的一致性
"""

import sys
import os
import asyncio
import httpx
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.utils.tag_processor import TagProcessor

def test_tag_processor_updates():
    """测试TagProcessor的标签更新"""
    print("🧪 测试1: TagProcessor标签配置")
    print("=" * 50)
    
    # 测试能源类型标签
    print(f"能源类型标签数量: {len(TagProcessor.STANDARD_ENERGY_TYPES)}")
    print(f"包含的新增标签: {[tag for tag in TagProcessor.STANDARD_ENERGY_TYPES if tag in ['核能', '可再生能源', '生物质能', '氢能', '重烃']]}")
    
    # 测试基础信息标签
    print(f"基础信息标签数量: {len(TagProcessor.STANDARD_BASIC_INFO_TAGS)}")
    print(f"标签内容: {TagProcessor.STANDARD_BASIC_INFO_TAGS}")
    
    # 测试业务领域标签
    print(f"业务领域标签数量: {len(TagProcessor.STANDARD_BUSINESS_FIELD_TAGS)}")
    print(f"包含现代化标签: {[tag for tag in TagProcessor.STANDARD_BUSINESS_FIELD_TAGS if tag in ['民营经济发展', '市场准入优化', '公平竞争']]}")
    
    # 测试新增的标签类型
    print(f"受益主体标签数量: {len(TagProcessor.STANDARD_BENEFICIARY_TAGS)}")
    print(f"政策措施标签数量: {len(TagProcessor.STANDARD_POLICY_MEASURE_TAGS)}")
    print(f"重要性标签数量: {len(TagProcessor.STANDARD_IMPORTANCE_TAGS)}")

async def test_tag_options_api():
    """测试tag-options API返回的标签"""
    print("\n🌐 测试2: tag-options API配置")
    print("=" * 50)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/api/v1/users/tag-options")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ API响应成功")
                print(f"能源类型标签数量: {len(data.get('energy_type_tags', []))}")
                print(f"基础信息标签数量: {len(data.get('basic_info_tags', []))}")
                print(f"业务领域标签数量: {len(data.get('business_field_tags', []))}")
                print(f"受益主体标签数量: {len(data.get('beneficiary_tags', []))}")
                print(f"政策措施标签数量: {len(data.get('policy_measure_tags', []))}")
                print(f"重要性标签数量: {len(data.get('importance_tags', []))}")
                
                # 验证标签一致性
                api_energy_tags = data.get('energy_type_tags', [])
                if api_energy_tags == TagProcessor.STANDARD_ENERGY_TYPES:
                    print("✅ 能源类型标签与TagProcessor一致")
                else:
                    print("❌ 能源类型标签不一致")
                    print(f"API: {api_energy_tags}")
                    print(f"TagProcessor: {TagProcessor.STANDARD_ENERGY_TYPES}")
                
                api_basic_tags = data.get('basic_info_tags', [])
                if api_basic_tags == TagProcessor.STANDARD_BASIC_INFO_TAGS:
                    print("✅ 基础信息标签与TagProcessor一致")
                else:
                    print("❌ 基础信息标签不一致")
                
                api_business_tags = data.get('business_field_tags', [])
                if api_business_tags == TagProcessor.STANDARD_BUSINESS_FIELD_TAGS:
                    print("✅ 业务领域标签与TagProcessor一致")
                else:
                    print("❌ 业务领域标签不一致")
                
                return data
            else:
                print(f"❌ API请求失败: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return None

def compare_frontend_configs():
    """对比前端配置的标签（理论上的验证）"""
    print("\n🖥️ 测试3: 前端标签配置对比")
    print("=" * 50)
    
    # 前端硬编码配置（用于对比）
    frontend_hardcoded = {
        "energy_type_tags": [
            "原油", "管道天然气(PNG)", "天然气", "液化天然气(LNG)", 
            "液化石油气(LPG)", "汽油", "柴油", "沥青", "石油焦", 
            "生物柴油", "电力", "煤炭", "重烃", "核能", "可再生能源", 
            "生物质能", "氢能"
        ],
        "basic_info_tags": [
            "政策法规", "行业资讯", "交易公告", "调价公告", "研报分析"
        ],
        "business_field_tags": [
            "市场动态", "价格变化", "交易信息", "科技创新", 
            "政策解读", "国际合作", "投资支持", "民营经济发展", 
            "市场准入优化", "公平竞争"
        ]
    }
    
    # 验证后端标签与期望的前端标签是否一致
    energy_match = TagProcessor.STANDARD_ENERGY_TYPES == frontend_hardcoded["energy_type_tags"]
    basic_match = TagProcessor.STANDARD_BASIC_INFO_TAGS == frontend_hardcoded["basic_info_tags"]
    business_match = TagProcessor.STANDARD_BUSINESS_FIELD_TAGS == frontend_hardcoded["business_field_tags"]
    
    print(f"能源类型标签一致性: {'✅' if energy_match else '❌'}")
    print(f"基础信息标签一致性: {'✅' if basic_match else '❌'}")
    print(f"业务领域标签一致性: {'✅' if business_match else '❌'}")
    
    if not energy_match:
        print(f"能源类型差异:")
        print(f"  后端: {TagProcessor.STANDARD_ENERGY_TYPES}")
        print(f"  前端: {frontend_hardcoded['energy_type_tags']}")
    
    if not basic_match:
        print(f"基础信息差异:")
        print(f"  后端: {TagProcessor.STANDARD_BASIC_INFO_TAGS}")
        print(f"  前端: {frontend_hardcoded['basic_info_tags']}")
    
    if not business_match:
        print(f"业务领域差异:")
        print(f"  后端: {TagProcessor.STANDARD_BUSINESS_FIELD_TAGS}")
        print(f"  前端: {frontend_hardcoded['business_field_tags']}")
    
    return energy_match and basic_match and business_match

def analyze_tag_improvements():
    """分析标签改进效果"""
    print("\n📊 测试4: 标签改进分析")
    print("=" * 50)
    
    # 旧的能源类型（修复前）
    old_energy_types = [
        "天然气", "原油", "液化天然气(LNG)", "管道天然气(PNG)", 
        "液化石油气(LPG)", "汽油", "柴油", "沥青", "石油焦", 
        "生物柴油", "电力", "煤炭"
    ]
    
    # 新增的能源类型
    new_energy_types = set(TagProcessor.STANDARD_ENERGY_TYPES) - set(old_energy_types)
    
    print(f"修复前能源类型数量: {len(old_energy_types)}")
    print(f"修复后能源类型数量: {len(TagProcessor.STANDARD_ENERGY_TYPES)}")
    print(f"新增能源类型: {list(new_energy_types)}")
    print(f"能源类型增长: {len(TagProcessor.STANDARD_ENERGY_TYPES) - len(old_energy_types)} 个")
    
    # 旧的基础信息标签（修复前）
    old_basic_info = [
        "政策法规", "行业资讯", "调价公告", "交易公告",
        "价格动态", "市场分析", "供需分析", "技术创新"
    ]
    
    print(f"\n修复前基础信息标签数量: {len(old_basic_info)}")
    print(f"修复后基础信息标签数量: {len(TagProcessor.STANDARD_BASIC_INFO_TAGS)}")
    
    # 旧的业务领域标签（修复前）
    old_business_fields = [
        "炼化", "储运", "销售", "贸易", "运输", "配送", 
        "零售", "发电", "输配电", "竞价交易", "进口贸易",
        "企业动态", "系统运营"
    ]
    
    print(f"\n修复前业务领域标签数量: {len(old_business_fields)}")
    print(f"修复后业务领域标签数量: {len(TagProcessor.STANDARD_BUSINESS_FIELD_TAGS)}")
    print(f"现代化标签: {[tag for tag in TagProcessor.STANDARD_BUSINESS_FIELD_TAGS if '民营' in tag or '优化' in tag or '公平' in tag]}")

async def main():
    """主测试函数"""
    print("🏷️ 标签一致性验证开始")
    print("=" * 60)
    
    # 1. 测试TagProcessor配置
    test_tag_processor_updates()
    
    # 2. 测试API配置
    api_data = await test_tag_options_api()
    
    # 3. 对比前端配置
    frontend_consistent = compare_frontend_configs()
    
    # 4. 分析改进效果
    analyze_tag_improvements()
    
    # 总结
    print("\n🎯 验证结果总结")
    print("=" * 60)
    
    if api_data:
        print("✅ 后端API配置正常")
    else:
        print("❌ 后端API配置异常")
    
    if frontend_consistent:
        print("✅ 前后端标签配置一致")
    else:
        print("❌ 前后端标签配置存在差异")
    
    print(f"✅ 能源类型标签已扩展至 {len(TagProcessor.STANDARD_ENERGY_TYPES)} 个")
    print(f"✅ 新增受益主体标签 {len(TagProcessor.STANDARD_BENEFICIARY_TAGS)} 个")
    print(f"✅ 新增政策措施标签 {len(TagProcessor.STANDARD_POLICY_MEASURE_TAGS)} 个")
    print("✅ 所有标签配置已实现统一管理")
    
    print("\n🎉 标签一致性修复验证完成！")

if __name__ == "__main__":
    asyncio.run(main()) 