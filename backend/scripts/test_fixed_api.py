#!/usr/bin/env python3
import requests
import json

def test_api():
    base_url = "http://localhost:8001/api/v1"
    
    print("🧪 测试修复后的API功能")
    print("=" * 50)
    
    # 测试获取所有内容
    print("\n📚 测试获取所有内容...")
    response = requests.get(f"{base_url}/content/?page=1&page_size=100")
    if response.status_code == 200:
        data = response.json()
        all_content = data.get('items', [])
        print(f"✅ 获取成功，总数: {len(all_content)}篇")
        
        # 统计分类
        market_count = len([item for item in all_content 
                           if '行业资讯' in item.get('basic_info_tags', [])])
        policy_count = len([item for item in all_content 
                           if '政策法规' in item.get('basic_info_tags', [])])
        trade_count = len([item for item in all_content 
                          if '交易公告' in item.get('basic_info_tags', [])])
        price_count = len([item for item in all_content 
                          if '调价公告' in item.get('basic_info_tags', [])])
        
        print(f"📈 行情咨询: {market_count}篇")
        print(f"📋 政策法规: {policy_count}篇")
        print(f"📢 交易公告: {trade_count}篇")
        print(f"💰 调价公告: {price_count}篇")
        print(f"📊 总公告数: {trade_count + price_count}篇")
        
        # 测试前端筛选逻辑
        print("\n🔍 测试前端筛选逻辑:")
        
        # 行情筛选（前端逻辑）
        market_filtered = [item for item in all_content 
                          if (item.get('basic_info_tags', []) and 
                              '行业资讯' in item.get('basic_info_tags', []))]
        print(f"🎯 行情筛选结果: {len(market_filtered)}篇")
        
        # 政策筛选（前端逻辑）
        policy_filtered = [item for item in all_content 
                          if (item.get('basic_info_tags', []) and 
                              '政策法规' in item.get('basic_info_tags', []))]
        print(f"🎯 政策筛选结果: {len(policy_filtered)}篇")
        
        # 公告筛选（前端逻辑）
        announcement_filtered = [item for item in all_content 
                               if (item.get('basic_info_tags', []) and 
                                   ('交易公告' in item.get('basic_info_tags', []) or
                                    '调价公告' in item.get('basic_info_tags', [])))]
        print(f"🎯 公告筛选结果: {len(announcement_filtered)}篇")
        
    else:
        print(f"❌ 获取失败: {response.status_code}")
    
    # 测试推荐API
    print("\n🎯 测试推荐API...")
    user_tags = ["天然气", "政策", "交易"]
    response = requests.post(f"{base_url}/content/recommend", 
                           json={"user_tags": user_tags, "limit": 20})
    if response.status_code == 200:
        data = response.json()
        recommendations = data.get('recommendations', [])
        print(f"✅ 推荐成功，数量: {len(recommendations)}篇")
        
        # 统计推荐分类
        rec_market = len([item for item in recommendations 
                         if '行业资讯' in item.get('basic_info_tags', [])])
        rec_policy = len([item for item in recommendations 
                         if '政策法规' in item.get('basic_info_tags', [])])
        rec_trade = len([item for item in recommendations 
                        if '交易公告' in item.get('basic_info_tags', [])])
        rec_price = len([item for item in recommendations 
                        if '调价公告' in item.get('basic_info_tags', [])])
        
        print(f"📈 推荐行情: {rec_market}篇")
        print(f"📋 推荐政策: {rec_policy}篇")
        print(f"📢 推荐交易公告: {rec_trade}篇")
        print(f"💰 推荐调价公告: {rec_price}篇")
        
    else:
        print(f"❌ 推荐失败: {response.status_code}")

if __name__ == "__main__":
    test_api() 