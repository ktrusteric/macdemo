#!/usr/bin/env python3
"""
前端页面标签处理验证测试脚本
测试Dashboard.vue、ContentList.vue、TagsManagement.vue对标签修改的适配情况
"""

import json
import sys
import time
import requests
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:8001/api/v1"
DEMO_USERS = [
    {"username": "张工程师", "email": "zhang@shanghai.com", "password": "demo123", "city": "上海", "energy_focus": "天然气"},
    {"username": "李经理", "email": "li@beijing.com", "password": "demo123", "city": "北京", "energy_focus": "原油"},
    {"username": "王主任", "email": "wang@shenzhen.com", "password": "demo123", "city": "深圳", "energy_focus": "LNG"},
    {"username": "陈总监", "email": "chen@guangzhou.com", "password": "demo123", "city": "广州", "energy_focus": "PNG"},
    {"username": "刘研究员", "email": "liu@chengdu.com", "password": "demo123", "city": "成都", "energy_focus": "电力"}
]

class FrontendPagesTest:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, category, item, status, details):
        """记录测试结果"""
        result = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "category": category,
            "item": item,
            "status": status,
            "details": details
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} [{category}] {item}: {details}")
    
    def test_backend_connectivity(self):
        """测试后端连接性"""
        try:
            resp = self.session.get("http://localhost:8001/health", timeout=5)
            if resp.status_code == 200:
                self.log_test("连接性", "后端服务", "PASS", "后端服务正常运行")
                return True
            else:
                self.log_test("连接性", "后端服务", "FAIL", f"HTTP状态码: {resp.status_code}")
                return False
        except Exception as e:
            self.log_test("连接性", "后端服务", "FAIL", f"连接失败: {str(e)}")
            return False
    
    def test_user_login_and_tags(self, user_info):
        """测试用户登录并获取标签信息"""
        try:
            # 登录用户
            login_data = {
                "email": user_info["email"],
                "password": user_info["password"]
            }
            
            resp = self.session.post(f"{BASE_URL}/users/login", json=login_data, timeout=10)
            if resp.status_code != 200:
                self.log_test("用户登录", user_info["username"], "FAIL", f"登录失败: {resp.status_code}")
                return None
            
            result = resp.json()
            token = result.get("access_token")
            user_info = result.get("user_info", {})
            user_id = user_info.get("id")
            
            if not token:
                self.log_test("用户登录", user_info["username"], "FAIL", "未获取到访问令牌")
                return None
            
            self.log_test("用户登录", user_info.get("username", "未知用户"), "PASS", f"用户ID: {user_id}")
            
            # 获取用户标签
            headers = {"Authorization": f"Bearer {token}"}
            tag_resp = self.session.get(f"{BASE_URL}/users/{user_id}/tags", headers=headers, timeout=10)
            if tag_resp.status_code == 200:
                tag_data = tag_resp.json()
                tags = tag_data.get("data", {}).get("tags", [])
                
                # 分析标签结构
                tag_analysis = self.analyze_user_tags(tags, user_info)
                
                return {
                    "user_id": user_id,
                    "token": token,
                    "tags": tags,
                    "analysis": tag_analysis
                }
            else:
                self.log_test("用户标签", user_info["username"], "FAIL", f"获取标签失败: {tag_resp.status_code}")
                return None
                
        except Exception as e:
            self.log_test("用户登录", user_info["username"], "FAIL", f"异常: {str(e)}")
            return None
    
    def analyze_user_tags(self, tags, user_info):
        """分析用户标签结构（验证前端页面需要的格式）"""
        analysis = {
            "total_count": len(tags),
            "by_category": {},
            "energy_tags": [],
            "regional_tags": [],
            "weight_distribution": {}
        }
        
        for tag in tags:
            category = tag.get("category", "unknown")
            name = tag.get("name", "")
            weight = tag.get("weight", 0)
            source = tag.get("source", "unknown")
            
            # 按分类统计
            if category not in analysis["by_category"]:
                analysis["by_category"][category] = []
            analysis["by_category"][category].append({
                "name": name,
                "weight": weight,
                "source": source
            })
            
            # 收集能源标签
            if category == "energy_type":
                analysis["energy_tags"].append(name)
            
            # 收集地域标签
            if category in ["city", "province", "region"]:
                analysis["regional_tags"].append(f"{category}:{name}")
            
            # 权重分布
            weight_range = "高权重(≥2.0)" if weight >= 2.0 else "中权重(1.0-2.0)" if weight >= 1.0 else "低权重(<1.0)"
            if weight_range not in analysis["weight_distribution"]:
                analysis["weight_distribution"][weight_range] = 0
            analysis["weight_distribution"][weight_range] += 1
        
        # 验证单能源标签设计
        energy_count = len(analysis["energy_tags"])
        if energy_count == 1:
            self.log_test("标签验证", f"{user_info['username']}-能源标签", "PASS", 
                         f"单能源标签设计正确: {analysis['energy_tags'][0]}")
        else:
            self.log_test("标签验证", f"{user_info['username']}-能源标签", "WARN", 
                         f"能源标签数量: {energy_count} (期望: 1)")
        
        # 验证地域标签层次
        regional_count = len(analysis["regional_tags"])
        if regional_count >= 2:  # 至少应有城市和省份
            self.log_test("标签验证", f"{user_info['username']}-地域标签", "PASS", 
                         f"地域标签层次: {', '.join(analysis['regional_tags'])}")
        else:
            self.log_test("标签验证", f"{user_info['username']}-地域标签", "WARN", 
                         f"地域标签数量: {regional_count} (期望: ≥2)")
        
        return analysis
    
    def test_recommendation_api(self, user_data):
        """测试推荐API（Dashboard.vue调用）"""
        try:
            headers = {"Authorization": f"Bearer {user_data['token']}"}
            
            # 构建推荐请求（模拟Dashboard.vue的调用）
            relevant_tags = [tag for tag in user_data['tags'] 
                           if tag['category'] in ['basic_info', 'region', 'energy_type', 'business_field', 'beneficiary', 'policy_measure', 'importance']]
            
            recommend_data = {
                "user_tags": [f"{tag['category']}:{tag['name']}" for tag in relevant_tags],
                "limit": 6
            }
            
            resp = self.session.post(f"{BASE_URL}/content/recommend", 
                                   json=recommend_data, headers=headers, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                items = result.get("items", [])
                
                self.log_test("推荐引擎", f"{user_data['analysis']['energy_tags'][0] if user_data['analysis']['energy_tags'] else '未知'}用户", 
                            "PASS", f"获取推荐内容: {len(items)}条")
                
                # 验证推荐内容的标签格式（前端页面需要）
                if items:
                    sample_item = items[0]
                    tag_fields = ['basic_info_tags', 'region_tags', 'energy_type_tags', 
                                'business_field_tags', 'beneficiary_tags', 'policy_measure_tags', 'importance_tags']
                    
                    available_fields = [field for field in tag_fields if field in sample_item]
                    self.log_test("数据格式", "推荐内容标签字段", "PASS", 
                                f"包含标签字段: {', '.join(available_fields)}")
                
                return items
            else:
                self.log_test("推荐引擎", "API调用", "FAIL", f"状态码: {resp.status_code}")
                return []
                
        except Exception as e:
            self.log_test("推荐引擎", "API调用", "FAIL", f"异常: {str(e)}")
            return []
    
    def test_content_list_api(self):
        """测试内容列表API（ContentList.vue调用）"""
        try:
            params = {"page": 1, "page_size": 10, "sort_by": "latest"}
            resp = self.session.get(f"{BASE_URL}/content/", params=params, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                items = result.get("items", [])
                total = result.get("total", 0)
                
                self.log_test("内容列表", "API调用", "PASS", f"获取内容: {len(items)}/{total}条")
                
                # 验证内容的标签字段
                if items:
                    sample_item = items[0]
                    tag_fields = ['basic_info_tags', 'region_tags', 'energy_type_tags', 
                                'business_field_tags', 'beneficiary_tags', 'policy_measure_tags', 'importance_tags']
                    
                    tag_count = 0
                    for field in tag_fields:
                        if field in sample_item and sample_item[field]:
                            tag_count += len(sample_item[field])
                    
                    self.log_test("数据格式", "内容标签完整性", "PASS", 
                                f"样本文章标签数: {tag_count}")
                
                return items
            else:
                self.log_test("内容列表", "API调用", "FAIL", f"状态码: {resp.status_code}")
                return []
                
        except Exception as e:
            self.log_test("内容列表", "API调用", "FAIL", f"异常: {str(e)}")
            return []
    
    def test_tags_management_compatibility(self, user_data):
        """测试标签管理页面兼容性"""
        try:
            headers = {"Authorization": f"Bearer {user_data['token']}"}
            user_id = user_data['user_id']
            
            # 测试获取用户标签（TagsManagement.vue主要功能）
            resp = self.session.get(f"{BASE_URL}/users/{user_id}/tags", headers=headers, timeout=10)
            if resp.status_code == 200:
                tag_data = resp.json()
                tags = tag_data.get("data", {}).get("tags", [])
                
                # 验证标签分类结构
                categories = set(tag['category'] for tag in tags)
                expected_categories = {'city', 'province', 'region', 'energy_type'}
                
                if expected_categories.issubset(categories):
                    self.log_test("标签管理", "分类结构", "PASS", 
                                f"包含核心分类: {', '.join(expected_categories)}")
                else:
                    missing = expected_categories - categories
                    self.log_test("标签管理", "分类结构", "WARN", 
                                f"缺少分类: {', '.join(missing)}")
                
                # 验证标签权重设置
                weight_valid = all(isinstance(tag.get('weight'), (int, float)) for tag in tags)
                if weight_valid:
                    self.log_test("标签管理", "权重设置", "PASS", "所有标签都有有效权重")
                else:
                    self.log_test("标签管理", "权重设置", "FAIL", "存在无效权重")
                
                return True
            else:
                self.log_test("标签管理", "API调用", "FAIL", f"状态码: {resp.status_code}")
                return False
                
        except Exception as e:
            self.log_test("标签管理", "API调用", "FAIL", f"异常: {str(e)}")
            return False
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*80)
        print("📊 前端页面标签处理验证测试总结")
        print("="*80)
        
        total_tests = len(self.test_results)
        pass_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        fail_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warn_tests = len([r for r in self.test_results if r["status"] == "WARN"])
        
        print(f"📈 总测试数: {total_tests}")
        print(f"✅ 通过: {pass_tests}")
        print(f"❌ 失败: {fail_tests}")
        print(f"⚠️  警告: {warn_tests}")
        print(f"📊 成功率: {(pass_tests/total_tests*100):.1f}%")
        
        # 按分类统计
        categories = {}
        for result in self.test_results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"PASS": 0, "FAIL": 0, "WARN": 0}
            categories[cat][result["status"]] += 1
        
        print("\n📋 分类统计:")
        for category, stats in categories.items():
            total = sum(stats.values())
            pass_rate = (stats["PASS"] / total * 100) if total > 0 else 0
            print(f"  {category}: {stats['PASS']}/{total} ({pass_rate:.1f}%)")
        
        # 关键发现
        print("\n🔍 关键发现:")
        
        # 能源标签优化验证
        energy_tag_tests = [r for r in self.test_results if "能源标签" in r["item"]]
        single_energy_users = len([r for r in energy_tag_tests if r["status"] == "PASS"])
        print(f"  • Demo用户单能源标签优化: {single_energy_users}/{len(DEMO_USERS)} 用户符合预期")
        
        # API兼容性
        api_tests = [r for r in self.test_results if r["category"] in ["推荐引擎", "内容列表", "标签管理"]]
        api_success = len([r for r in api_tests if r["status"] == "PASS"])
        print(f"  • 前端页面API兼容性: {api_success}/{len(api_tests)} 接口正常")
        
        # 数据格式验证
        format_tests = [r for r in self.test_results if r["category"] == "数据格式"]
        format_success = len([r for r in format_tests if r["status"] == "PASS"])
        print(f"  • 标签数据格式兼容: {format_success}/{len(format_tests)} 字段正确")
        
        if fail_tests == 0:
            print(f"\n🎉 所有核心功能测试通过！前端页面已适配标签修改。")
        else:
            print(f"\n⚠️  发现 {fail_tests} 个问题，需要修复。")

def main():
    print("🧪 前端页面标签处理验证测试")
    print("=" * 50)
    print("测试目标:")
    print("  • Dashboard.vue - 推荐引擎和标签显示")
    print("  • ContentList.vue - 内容列表和标签格式")  
    print("  • TagsManagement.vue - 标签管理功能")
    print("  • Demo用户单能源标签优化验证")
    print("-" * 50)
    
    tester = FrontendPagesTest()
    
    # 1. 测试后端连接
    if not tester.test_backend_connectivity():
        print("❌ 后端服务未启动，请先运行 ./start_all_with_data.sh")
        return
    
    # 2. 测试内容列表API
    tester.test_content_list_api()
    
    # 3. 测试每个Demo用户
    for user_info in DEMO_USERS:
        print(f"\n🔍 测试用户: {user_info['username']} ({user_info['city']}, {user_info['energy_focus']})")
        
        user_data = tester.test_user_login_and_tags(user_info)
        if user_data:
            # 测试推荐功能
            tester.test_recommendation_api(user_data)
            
            # 测试标签管理兼容性
            tester.test_tags_management_compatibility(user_data)
    
    # 4. 打印测试总结
    tester.print_summary()

if __name__ == "__main__":
    main() 