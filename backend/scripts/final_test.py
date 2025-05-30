#!/usr/bin/env python3
import json
import subprocess
import sys

def test_api():
    print("🎉 最终验证测试")
    print("=" * 50)
    
    # 测试API响应
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://localhost:8001/api/v1/content/?page=1&page_size=100'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                items = data.get('items', [])
                total = data.get('total', 0)
                
                print(f"✅ API响应成功")
                print(f"📊 返回数据: {len(items)}篇文章，总计: {total}篇")
                
                # 测试筛选逻辑
                market_count = len([item for item in items 
                                   if '行业资讯' in item.get('basic_info_tags', [])])
                policy_count = len([item for item in items 
                                   if '政策法规' in item.get('basic_info_tags', [])])
                trade_count = len([item for item in items 
                                  if '交易公告' in item.get('basic_info_tags', [])])
                price_count = len([item for item in items 
                                  if '调价公告' in item.get('basic_info_tags', [])])
                
                print(f"\n🔍 筛选验证:")
                print(f"📈 行情资讯: {market_count}篇")
                print(f"📋 政策法规: {policy_count}篇") 
                print(f"📢 交易公告: {trade_count}篇")
                print(f"💰 调价公告: {price_count}篇")
                print(f"📊 总公告数: {trade_count + price_count}篇")
                
                # 验证期望结果
                expected_results = {
                    "total": 51,
                    "market": 26,
                    "policy": 20,
                    "trade": 3,
                    "price": 2
                }
                
                print(f"\n✅ 结果验证:")
                results = {
                    "total": total,
                    "market": market_count,
                    "policy": policy_count,
                    "trade": trade_count,
                    "price": price_count
                }
                
                all_correct = True
                for key, expected in expected_results.items():
                    actual = results[key]
                    status = "✅" if actual == expected else "❌"
                    print(f"   {key}: {actual} (期望: {expected}) {status}")
                    if actual != expected:
                        all_correct = False
                
                if all_correct:
                    print(f"\n🎉 所有测试通过！前端筛选功能已修复")
                    print(f"   - 行情筛选: 可筛选出{market_count}篇行业资讯")
                    print(f"   - 政策筛选: 可筛选出{policy_count}篇政策法规")
                    print(f"   - 公告筛选: 可筛选出{trade_count + price_count}篇公告")
                else:
                    print(f"\n❌ 部分测试失败，请检查数据")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"原始响应: {result.stdout[:200]}...")
                
        else:
            print(f"❌ API请求失败: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_api() 