#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v1"

class AdminDashboardTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.admin_token = None
        
    def log_test(self, category, test_name, status, details=""):
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"[{timestamp}] {status_icon} {category} - {test_name}: {details}")
        
    def admin_login(self):
        """管理员登录"""
        try:
            resp = self.session.post(f"{BASE_URL}/admin/login", json={
                "username": "superadmin",
                "password": "super123456"
            })
            
            if resp.status_code == 200:
                result = resp.json()
                self.admin_token = result.get("access_token")
                self.session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}'
                })
                self.log_test("管理员认证", "登录测试", "PASS", 
                            f"用户: {result.get('admin', {}).get('username')}")
                return True
            else:
                self.log_test("管理员认证", "登录测试", "FAIL", 
                            f"状态码: {resp.status_code}")
                return False
                
        except Exception as e:
            self.log_test("管理员认证", "登录测试", "FAIL", f"异常: {str(e)}")
            return False
    
    def test_admin_stats(self):
        """测试管理员统计数据"""
        try:
            resp = self.session.get(f"{BASE_URL}/admin/stats")
            
            if resp.status_code == 200:
                stats = resp.json()
                
                # 检查文章统计
                articles_total = stats.get("articles", {}).get("total", 0)
                articles_by_type = stats.get("articles", {}).get("by_type", {})
                
                self.log_test("统计数据", "文章总数", "PASS", 
                            f"总数: {articles_total}")
                
                # 检查文章类型分布
                for article_type, count in articles_by_type.items():
                    self.log_test("统计数据", f"文章类型-{article_type}", "PASS", 
                                f"数量: {count}")
                
                # 检查用户统计
                users_total = stats.get("users", {}).get("total", 0)
                users_admins = stats.get("users", {}).get("admins", 0)
                users_regular = stats.get("users", {}).get("regular", 0)
                
                self.log_test("统计数据", "用户总数", "PASS", 
                            f"总数: {users_total}")
                self.log_test("统计数据", "管理员数", "PASS", 
                            f"数量: {users_admins}")
                self.log_test("统计数据", "普通用户数", "PASS", 
                            f"数量: {users_regular}")
                
                # 验证数据结构
                expected_structure = {
                    "articles": {"total": int, "by_type": dict},
                    "users": {"total": int, "admins": int, "regular": int}
                }
                
                structure_valid = True
                for key, expected_type in expected_structure.items():
                    if key not in stats:
                        structure_valid = False
                        break
                    if isinstance(expected_type, dict):
                        for subkey, subtype in expected_type.items():
                            if subkey not in stats[key] or not isinstance(stats[key][subkey], subtype):
                                structure_valid = False
                                break
                
                self.log_test("数据结构", "API响应结构", 
                            "PASS" if structure_valid else "FAIL",
                            "符合预期结构" if structure_valid else "结构不匹配")
                
                return stats
                
            else:
                self.log_test("统计数据", "API调用", "FAIL", 
                            f"状态码: {resp.status_code}")
                return None
                
        except Exception as e:
            self.log_test("统计数据", "API调用", "FAIL", f"异常: {str(e)}")
            return None
    
    def test_frontend_calculation(self, stats):
        """测试前端计算逻辑"""
        if not stats:
            return
            
        # 模拟前端计算逻辑
        total_articles = stats.get("articles", {}).get("total", 0)
        type_distribution = stats.get("articles", {}).get("by_type", {})
        
        # 验证计算结果
        calculated_total = sum(type_distribution.values())
        
        if total_articles == calculated_total:
            self.log_test("前端逻辑", "文章总数计算", "PASS", 
                        f"API总数({total_articles}) = 类型统计总和({calculated_total})")
        else:
            self.log_test("前端逻辑", "文章总数计算", "FAIL", 
                        f"API总数({total_articles}) ≠ 类型统计总和({calculated_total})")
        
        # 检查前端显示逻辑
        if total_articles > 0:
            self.log_test("前端逻辑", "数据显示", "PASS", 
                        "应该显示非零数值")
        else:
            self.log_test("前端逻辑", "数据显示", "FAIL", 
                        "显示为0，前端可能有问题")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=== 管理员仪表板测试 ===")
        
        # 1. 管理员登录
        if not self.admin_login():
            print("❌ 管理员登录失败，终止测试")
            return
        
        # 2. 测试统计数据API
        stats = self.test_admin_stats()
        
        # 3. 测试前端计算逻辑
        self.test_frontend_calculation(stats)
        
        print("\n=== 测试完成 ===")
        
        if stats:
            print(f"📊 统计数据摘要:")
            print(f"  文章总数: {stats.get('articles', {}).get('total', 0)}")
            print(f"  用户总数: {stats.get('users', {}).get('total', 0)}")
            print(f"  文章类型分布: {stats.get('articles', {}).get('by_type', {})}")

if __name__ == "__main__":
    test = AdminDashboardTest()
    test.run_all_tests() 