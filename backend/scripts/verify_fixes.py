#!/usr/bin/env python3
"""
验证前端修复效果的脚本
"""
import requests
import json

def verify_content_stats():
    """验证内容统计数据"""
    print("🔍 验证内容统计数据...")
    
    try:
        # 获取所有内容
        response = requests.get('http://localhost:8001/api/v1/content/?page=1&page_size=100')
        data = response.json()
        items = data.get('items', [])
        total = data.get('total', 0)
        
        print(f"📊 总文章数: {total}篇")
        print(f"📊 当前获取: {len(items)}篇")
        
        # 统计各类文章
        market_count = len([item for item in items if '行业资讯' in item.get('basic_info_tags', [])])
        policy_count = len([item for item in items if '政策法规' in item.get('basic_info_tags', [])])
        trade_count = len([item for item in items if '交易公告' in item.get('basic_info_tags', [])])
        price_count = len([item for item in items if '调价公告' in item.get('basic_info_tags', [])])
        
        print(f"📈 行情资讯: {market_count}篇")
        print(f"📋 政策法规: {policy_count}篇") 
        print(f"📢 交易公告: {trade_count}篇")
        print(f"💰 调价公告: {price_count}篇")
        print(f"📊 总公告数: {trade_count + price_count}篇")
        
        # 验证预期结果
        expected = {
            'total': 51,
            'market': 26,
            'policy': 20,
            'trade': 3,
            'price': 2
        }
        
        actual = {
            'total': total,
            'market': market_count,
            'policy': policy_count,
            'trade': trade_count,
            'price': price_count
        }
        
        print("\n📊 数据验证结果:")
        for key in expected:
            status = "✅" if expected[key] == actual[key] else "❌"
            print(f"  {status} {key}: 期望{expected[key]}, 实际{actual[key]}")
            
        return all(expected[key] == actual[key] for key in expected)
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def verify_recommendation():
    """验证推荐功能"""
    print("\n🎯 验证推荐功能...")
    
    try:
        # 测试推荐API
        response = requests.post(
            'http://localhost:8001/api/v1/content/recommend',
            json={
                'user_tags': ['basic_info:政策法规', 'region:全国'],
                'limit': 3
            }
        )
        
        data = response.json()
        items = data.get('items', [])
        
        print(f"📄 推荐内容数量: {len(items)}篇")
        
        if items:
            print("✅ 推荐功能正常工作")
            for i, item in enumerate(items[:2], 1):
                print(f"  📄 推荐{i}: {item.get('title', '无标题')[:30]}...")
            return True
        else:
            print("❌ 推荐功能返回空结果")
            return False
            
    except Exception as e:
        print(f"❌ 推荐功能验证失败: {e}")
        return False

def main():
    print("🔧 开始验证前端修复效果...\n")
    
    stats_ok = verify_content_stats()
    recommend_ok = verify_recommendation()
    
    print(f"\n📋 验证总结:")
    print(f"  内容统计: {'✅ 正常' if stats_ok else '❌ 异常'}")
    print(f"  推荐功能: {'✅ 正常' if recommend_ok else '❌ 异常'}")
    
    if stats_ok and recommend_ok:
        print("\n🎉 所有修复验证通过！前端应该显示正确数据。")
    else:
        print("\n⚠️ 部分功能仍有问题，需要进一步排查。")

if __name__ == "__main__":
    main() 