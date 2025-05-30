#!/usr/bin/env python3
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_filtering_logic():
    print("🧪 测试前端筛选逻辑")
    print("=" * 50)
    
    # 模拟从API获取的数据
    sample_data = [
        {"basic_info_tags": ["行业资讯"], "title": "行业资讯1"},
        {"basic_info_tags": ["行业资讯"], "title": "行业资讯2"},
        {"basic_info_tags": ["政策法规"], "title": "政策法规1"},
        {"basic_info_tags": ["政策法规"], "title": "政策法规2"},
        {"basic_info_tags": ["交易公告"], "title": "交易公告1"},
        {"basic_info_tags": ["调价公告"], "title": "调价公告1"},
        {"basic_info_tags": ["调价公告"], "title": "调价公告2"},
    ]
    
    print(f"📊 测试数据总数: {len(sample_data)}篇")
    
    # 测试行情筛选（前端逻辑）
    market_filtered = [item for item in sample_data 
                      if (item.get('basic_info_tags', []) and 
                          '行业资讯' in item.get('basic_info_tags', []))]
    print(f"📈 行情筛选结果: {len(market_filtered)}篇")
    for item in market_filtered:
        print(f"   - {item['title']}")
    
    # 测试政策筛选（前端逻辑）
    policy_filtered = [item for item in sample_data 
                      if (item.get('basic_info_tags', []) and 
                          '政策法规' in item.get('basic_info_tags', []))]
    print(f"📋 政策筛选结果: {len(policy_filtered)}篇")
    for item in policy_filtered:
        print(f"   - {item['title']}")
    
    # 测试公告筛选（前端逻辑）
    announcement_filtered = [item for item in sample_data 
                           if (item.get('basic_info_tags', []) and 
                               ('交易公告' in item.get('basic_info_tags', []) or
                                '调价公告' in item.get('basic_info_tags', [])))]
    print(f"📢 公告筛选结果: {len(announcement_filtered)}篇")
    for item in announcement_filtered:
        print(f"   - {item['title']}")
    
    # 验证统计
    total_filtered = len(market_filtered) + len(policy_filtered) + len(announcement_filtered)
    print(f"\n✅ 筛选验证:")
    print(f"   总筛选结果: {total_filtered}篇")
    print(f"   原始数据: {len(sample_data)}篇")
    print(f"   匹配: {'✅' if total_filtered == len(sample_data) else '❌'}")

if __name__ == "__main__":
    test_filtering_logic() 