#!/usr/bin/env python3
"""
管理员文章搜索功能测试脚本
测试所有搜索和筛选功能是否正常工作
"""

import requests
import json
import urllib.parse

def get_admin_token():
    """获取管理员token"""
    login_data = {
        "username": "admin",
        "password": "admin123456"
    }
    
    response = requests.post(
        'http://localhost:8001/api/v1/admin/login',
        json=login_data
    )
    
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"❌ 管理员登录失败: {response.text}")
        return None

def test_search_feature(token, test_name, params):
    """测试搜索功能"""
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(
        'http://localhost:8001/api/v1/admin/articles',
        params=params,
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        total = data.get('total', 0)
        items_count = len(data.get('items', []))
        print(f"✅ {test_name}: 找到 {total} 篇文章，返回 {items_count} 篇")
        return data
    else:
        print(f"❌ {test_name}: 请求失败 - {response.text}")
        return None

def main():
    print("🔍 管理员文章搜索功能测试")
    print("=" * 60)
    
    # 获取管理员token
    token = get_admin_token()
    if not token:
        return
    
    print("✅ 管理员登录成功")
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "基础查询（无筛选）",
            "params": {"page": 1, "page_size": 5}
        },
        {
            "name": "文章类型筛选 - 政策法规",
            "params": {"page": 1, "page_size": 5, "content_type": "policy"}
        },
        {
            "name": "文章类型筛选 - 行业资讯",
            "params": {"page": 1, "page_size": 5, "content_type": "news"}
        },
        {
            "name": "文章类型筛选 - 交易公告",
            "params": {"page": 1, "page_size": 5, "content_type": "announcement"}
        },
        {
            "name": "文章类型筛选 - 调价公告",
            "params": {"page": 1, "page_size": 5, "content_type": "price"}
        },
        {
            "name": "能源类型筛选 - 天然气",
            "params": {"page": 1, "page_size": 5, "energy_type": "天然气"}
        },
        {
            "name": "能源类型筛选 - 原油",
            "params": {"page": 1, "page_size": 5, "energy_type": "原油"}
        },
        {
            "name": "能源类型筛选 - LNG",
            "params": {"page": 1, "page_size": 5, "energy_type": "液化天然气(LNG)"}
        },
        {
            "name": "标签搜索 - 上海",
            "params": {"page": 1, "page_size": 5, "tag_search": "上海"}
        },
        {
            "name": "标签搜索 - 华东地区",
            "params": {"page": 1, "page_size": 5, "tag_search": "华东地区"}
        },
        {
            "name": "关键词搜索 - 价格",
            "params": {"page": 1, "page_size": 5, "search_keyword": "价格"}
        },
        {
            "name": "组合搜索 - 政策法规+天然气",
            "params": {"page": 1, "page_size": 5, "content_type": "policy", "energy_type": "天然气"}
        },
        {
            "name": "组合搜索 - 行业资讯+原油+上海",
            "params": {"page": 1, "page_size": 5, "content_type": "news", "energy_type": "原油", "tag_search": "上海"}
        },
        {
            "name": "复杂组合搜索",
            "params": {
                "page": 1, 
                "page_size": 5, 
                "content_type": "policy", 
                "energy_type": "天然气", 
                "tag_search": "上海",
                "search_keyword": "价格"
            }
        }
    ]
    
    # 执行测试
    results = {}
    for test_case in test_cases:
        result = test_search_feature(token, test_case["name"], test_case["params"])
        if result:
            results[test_case["name"]] = result.get('total', 0)
    
    print()
    print("📊 测试结果汇总")
    print("=" * 60)
    
    for test_name, count in results.items():
        print(f"{test_name}: {count} 篇文章")
    
    print()
    print("🎯 功能验证")
    print("=" * 60)
    
    # 验证功能是否正常
    checks = [
        ("文章类型筛选", results.get("文章类型筛选 - 政策法规", 0) > 0),
        ("能源类型筛选", results.get("能源类型筛选 - 天然气", 0) > 0),
        ("标签搜索", results.get("标签搜索 - 上海", 0) > 0),
        ("关键词搜索", results.get("关键词搜索 - 价格", 0) > 0),
        ("组合搜索", results.get("组合搜索 - 政策法规+天然气", 0) > 0),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 所有搜索功能测试通过！")
        print("✅ 文章类型筛选正常")
        print("✅ 能源类型筛选正常") 
        print("✅ 标签搜索功能正常")
        print("✅ 关键词搜索正常")
        print("✅ 组合搜索正常")
    else:
        print("⚠️ 部分功能测试失败，请检查后端实现")

if __name__ == "__main__":
    main() 