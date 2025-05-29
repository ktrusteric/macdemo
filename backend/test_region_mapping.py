#!/usr/bin/env python3
"""
城市-区域映射功能测试脚本
用于验证重构后的用户功能是否正常工作
"""

import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.region_mapper import RegionMapper, RegionCode
from app.services.user_service import UserService
from app.models.user import UserCreate, TagCategory, TagSource
from app.core.database import get_database
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

class TestRegionMapping:
    """区域映射测试类"""
    
    def __init__(self):
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append((test_name, success, message))
        print(f"{status} {test_name}: {message}")
    
    def test_region_mapper_basic(self):
        """测试基础的城市-区域映射"""
        print("\n=== 测试基础城市-区域映射 ===")
        
        # 测试1：城市到区域映射
        test_cases = [
            ("上海", RegionCode.EAST_CHINA, "华东地区"),
            ("深圳", RegionCode.SOUTH_CHINA, "华南地区"),
            ("北京", RegionCode.NORTH_CHINA, "华北地区"),
            ("成都", RegionCode.SOUTHWEST_CHINA, "西南地区"),
            ("西安", RegionCode.NORTHWEST_CHINA, "西北地区"),
            ("沈阳", RegionCode.NORTHEAST_CHINA, "东北地区"),
            ("武汉", RegionCode.CENTRAL_CHINA, "华中地区"),
        ]
        
        for city, expected_code, expected_name in test_cases:
            region_code = RegionMapper.get_region_by_city(city)
            region_name = RegionMapper.get_region_name(region_code) if region_code else None
            
            success = region_code == expected_code and region_name == expected_name
            self.log_test(
                f"城市映射-{city}", 
                success, 
                f"{city} -> {region_code} ({region_name})"
            )
        
        # 测试2：获取所有城市
        all_cities = RegionMapper.get_all_cities()
        self.log_test(
            "获取所有城市", 
            len(all_cities) > 50, 
            f"共{len(all_cities)}个支持的城市"
        )
        
        # 测试3：根据区域获取城市
        east_china_cities = RegionMapper.get_cities_by_region(RegionCode.EAST_CHINA)
        self.log_test(
            "根据区域获取城市", 
            "上海" in east_china_cities and "杭州" in east_china_cities,
            f"华东地区城市: {east_china_cities[:5]}..."
        )
        
        # 测试4：批量城市转区域
        test_cities = ["上海", "深圳", "北京"]
        regions = RegionMapper.get_regions_by_cities(test_cities)
        expected_regions = [RegionCode.EAST_CHINA, RegionCode.SOUTH_CHINA, RegionCode.NORTH_CHINA]
        success = all(r in regions for r in expected_regions)
        self.log_test(
            "批量城市转区域",
            success,
            f"{test_cities} -> {regions}"
        )
    
    async def test_user_service_integration(self):
        """测试用户服务集成"""
        print("\n=== 测试用户服务集成 ===")
        
        try:
            # 连接数据库（测试环境）
            client = AsyncIOMotorClient("mongodb://localhost:27017")
            database = client.test_energy_info
            user_service = UserService(database)
            
            # 创建测试用户数据
            test_user = UserCreate(
                email=f"test_{uuid.uuid4().hex[:8]}@example.com",
                username=f"test_user_{uuid.uuid4().hex[:8]}",
                password="test123456",
                register_city="上海"
            )
            
            # 测试用户创建
            try:
                user = await user_service.create_user(test_user, ["天然气", "LNG"])
                self.log_test(
                    "创建用户",
                    user.register_city == "上海",
                    f"用户ID: {user.id[:8]}..., 注册城市: {user.register_city}"
                )
                
                # 测试用户标签生成
                user_tags = await user_service.get_user_tags(user.id)
                if user_tags:
                    region_tags = [tag for tag in user_tags.tags if tag.category == TagCategory.REGION]
                    
                    # 应该有两个区域标签：城市标签和区域标签
                    city_tag = next((tag for tag in region_tags if tag.name == "上海"), None)
                    region_tag = next((tag for tag in region_tags if tag.name == "华东地区"), None)
                    
                    self.log_test(
                        "城市标签生成",
                        city_tag is not None and city_tag.source == TagSource.PRESET,
                        f"城市标签: {city_tag.name if city_tag else 'None'}, 权重: {city_tag.weight if city_tag else 'None'}"
                    )
                    
                    self.log_test(
                        "区域标签自动生成",
                        region_tag is not None and region_tag.source == TagSource.REGION_AUTO,
                        f"区域标签: {region_tag.name if region_tag else 'None'}, 权重: {region_tag.weight if region_tag else 'None'}"
                    )
                    
                    # 测试获取用户区域信息
                    region_info = await user_service.get_user_region_info(user.id)
                    expected_info = {
                        "city": "上海",
                        "region": "华东地区", 
                        "region_code": RegionCode.EAST_CHINA
                    }
                    
                    success = all(region_info.get(k) == v for k, v in expected_info.items())
                    self.log_test(
                        "获取用户区域信息",
                        success,
                        f"区域信息: {region_info}"
                    )
                else:
                    self.log_test("获取用户标签", False, "无法获取用户标签")
                
                # 清理测试数据
                await user_service.users_collection.delete_one({"id": user.id})
                await user_service.user_tags_collection.delete_one({"user_id": user.id})
                
            except Exception as e:
                self.log_test("用户服务测试", False, f"错误: {str(e)}")
            
            # 关闭数据库连接
            client.close()
            
        except Exception as e:
            self.log_test("数据库连接", False, f"无法连接到测试数据库: {str(e)}")
    
    def test_api_data_structure(self):
        """测试API数据结构"""
        print("\n=== 测试API数据结构 ===")
        
        # 测试支持的城市API数据结构
        cities = RegionMapper.get_all_cities()
        regions = RegionMapper.get_all_regions()
        
        api_response = {
            "cities": sorted(cities),
            "regions": regions,
            "total_cities": len(cities)
        }
        
        self.log_test(
            "API数据结构",
            isinstance(api_response["cities"], list) and 
            isinstance(api_response["regions"], list) and
            isinstance(api_response["total_cities"], int),
            f"城市数: {api_response['total_cities']}, 区域数: {len(api_response['regions'])}"
        )
        
        # 检查区域数据结构
        if regions:
            first_region = regions[0]
            has_required_keys = "code" in first_region and "name" in first_region
            self.log_test(
                "区域数据结构",
                has_required_keys,
                f"示例区域: {first_region}"
            )
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*50)
        print("测试总结")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, success, _ in self.test_results if success)
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n失败的测试:")
            for test_name, success, message in self.test_results:
                if not success:
                    print(f"  ❌ {test_name}: {message}")
        
        print("\n重构验证结果:")
        if failed_tests == 0:
            print("✅ 所有测试通过！城市-区域映射功能重构成功。")
        else:
            print("❌ 部分测试失败，需要检查和修复。")

async def main():
    """主测试函数"""
    print("🔍 开始测试城市-区域映射功能重构")
    print("="*50)
    
    tester = TestRegionMapping()
    
    # 运行所有测试
    tester.test_region_mapper_basic()
    await tester.test_user_service_integration()
    tester.test_api_data_structure()
    
    # 打印总结
    tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main()) 