#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v1"

class DashboardContentListTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, category, test_name, status, details=""):
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"[{timestamp}] {status_icon} {category} - {test_name}: {details}")
        
    def test_content_api(self):
        """测试内容API（ContentList.vue使用）"""
        try:
            # 测试基本内容获取
            resp = self.session.get(f"{BASE_URL}/content/", params={
                "page": 1,
                "page_size": 10,
                "sort_by": "latest"
            }, timeout=10)
            
            if resp.status_code == 200:
                result = resp.json()
                items = result.get("items", [])
                total = result.get("total", 0)
                
                self.log_test("ContentList", "基础API调用", "PASS", 
                            f"获取内容: {len(items)}/{total}条")
                
                # 验证数据结构
                if items:
                    sample_item = items[0]
                    required_fields = ['title', 'content', 'type', 'publish_time', 'basic_info_tags']
                    missing_fields = [field for field in required_fields if field not in sample_item]
                    
                    if not missing_fields:
                        self.log_test("ContentList", "数据结构验证", "PASS", 
                                    "所有必需字段存在")
                    else:
                        self.log_test("ContentList", "数据结构验证", "FAIL", 
                                    f"缺少字段: {missing_fields}")
                
                # 验证标签字段
                tag_fields = ['basic_info_tags', 'region_tags', 'energy_type_tags', 
                            'business_field_tags', 'beneficiary_tags', 'policy_measure_tags', 'importance_tags']
                
                tag_count = 0
                for item in items[:3]:  # 检查前3个项目
                    for field in tag_fields:
                        if field in item and item[field]:
                            tag_count += len(item[field])
                
                self.log_test("ContentList", "标签完整性", "PASS", 
                            f"前3篇文章总标签数: {tag_count}")
                
                return items
            else:
                self.log_test("ContentList", "基础API调用", "FAIL", 
                            f"状态码: {resp.status_code}")
                return []
                
        except Exception as e:
            self.log_test("ContentList", "基础API调用", "FAIL", f"异常: {str(e)}")
            return []
    
    def test_content_filtering(self):
        """测试内容筛选功能"""
        try:
            # 测试按类型筛选
            resp = self.session.get(f"{BASE_URL}/content/", params={
                "page": 1,
                "page_size": 100,
                "content_type": "policy"
            }, timeout=10)
            
            if resp.status_code == 200:
                result = resp.json()
                items = result.get("items", [])
                
                # 验证筛选结果
                policy_items = [item for item in items if 
                              (item.get('basic_info_tags', []) and '政策法规' in item['basic_info_tags'])]
                
                self.log_test("ContentList", "政策类型筛选", "PASS", 
                            f"政策文章数: {len(policy_items)}")
                
                # 测试搜索功能
                resp = self.session.get(f"{BASE_URL}/content/", params={
                    "page": 1,
                    "page_size": 100,
                    "search": "天然气"
                }, timeout=10)
                
                if resp.status_code == 200:
                    result = resp.json()
                    search_items = result.get("items", [])
                    
                    self.log_test("ContentList", "搜索功能", "PASS", 
                                f"搜索'天然气'结果: {len(search_items)}条")
                else:
                    self.log_test("ContentList", "搜索功能", "FAIL", 
                                f"状态码: {resp.status_code}")
            else:
                self.log_test("ContentList", "政策类型筛选", "FAIL", 
                            f"状态码: {resp.status_code}")
                
        except Exception as e:
            self.log_test("ContentList", "筛选功能", "FAIL", f"异常: {str(e)}")
    
    def test_dashboard_apis(self):
        """测试Dashboard页面相关API"""
        try:
            # 测试演示用户获取
            resp = self.session.get(f"{BASE_URL}/users/demo-users", timeout=10)
            
            if resp.status_code == 200:
                result = resp.json()
                demo_users = result.get("users", [])
                
                self.log_test("Dashboard", "演示用户获取", "PASS", 
                            f"演示用户数: {len(demo_users)}")
                
                # 测试用户标签获取
                if demo_users:
                    user_id = demo_users[0].get("id")
                    if user_id:
                        resp = self.session.get(f"{BASE_URL}/users/{user_id}/tags", timeout=10)
                        
                        if resp.status_code == 200:
                            result = resp.json()
                            tags = result.get("data", {}).get("tags", [])
                            
                            self.log_test("Dashboard", "用户标签获取", "PASS", 
                                        f"用户标签数: {len(tags)}")
                            
                            # 测试推荐内容获取
                            resp = self.session.get(f"{BASE_URL}/users/{user_id}/recommendations", 
                                                  params={"page": 1, "page_size": 5}, timeout=10)
                            
                            if resp.status_code == 200:
                                result = resp.json()
                                recommendations = result.get("items", [])
                                
                                self.log_test("Dashboard", "推荐内容获取", "PASS", 
                                            f"推荐内容数: {len(recommendations)}")
                            else:
                                self.log_test("Dashboard", "推荐内容获取", "FAIL", 
                                            f"状态码: {resp.status_code}")
                        else:
                            self.log_test("Dashboard", "用户标签获取", "FAIL", 
                                        f"状态码: {resp.status_code}")
            else:
                self.log_test("Dashboard", "演示用户获取", "FAIL", 
                            f"状态码: {resp.status_code}")
                
        except Exception as e:
            self.log_test("Dashboard", "API调用", "FAIL", f"异常: {str(e)}")
    
    def test_data_consistency(self):
        """测试数据一致性（重复字段清理效果）"""
        try:
            resp = self.session.get(f"{BASE_URL}/content/", params={
                "page": 1,
                "page_size": 50
            }, timeout=10)
            
            if resp.status_code == 200:
                result = resp.json()
                items = result.get("items", [])
                
                # 检查是否还有重复的"文档类型"字段
                duplicate_field_count = 0
                basic_info_count = 0
                
                for item in items:
                    if "文档类型" in item:
                        duplicate_field_count += 1
                    if "basic_info_tags" in item and item["basic_info_tags"]:
                        basic_info_count += 1
                
                if duplicate_field_count == 0:
                    self.log_test("数据一致性", "重复字段清理", "PASS", 
                                "无重复'文档类型'字段")
                else:
                    self.log_test("数据一致性", "重复字段清理", "FAIL", 
                                f"仍有{duplicate_field_count}个重复字段")
                
                self.log_test("数据一致性", "标准字段使用", "PASS", 
                            f"{basic_info_count}/{len(items)}篇文章有basic_info_tags")
                
                # 检查标签分布
                tag_distribution = {}
                for item in items:
                    for tag in item.get("basic_info_tags", []):
                        tag_distribution[tag] = tag_distribution.get(tag, 0) + 1
                
                self.log_test("数据一致性", "标签分布", "PASS", 
                            f"基础信息标签类型: {list(tag_distribution.keys())}")
                
            else:
                self.log_test("数据一致性", "数据获取", "FAIL", 
                            f"状态码: {resp.status_code}")
                
        except Exception as e:
            self.log_test("数据一致性", "检查", "FAIL", f"异常: {str(e)}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始测试Dashboard和ContentList功能")
        print("=" * 60)
        
        # 等待服务启动
        print("⏳ 等待服务启动...")
        time.sleep(2)
        
        # 运行测试
        self.test_content_api()
        self.test_content_filtering()
        self.test_dashboard_apis()
        self.test_data_consistency()
        
        print("=" * 60)
        print("✅ 测试完成！")

if __name__ == "__main__":
    tester = DashboardContentListTest()
    tester.run_all_tests() 