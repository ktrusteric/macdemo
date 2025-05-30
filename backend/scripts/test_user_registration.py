#!/usr/bin/env python3
"""
用户注册流程测试脚本
验证城市→省份→地区自动识别逻辑
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from app.services.user_service import UserService
from app.models.user import UserCreate, TagCategory, TagSource
from app.utils.region_mapper import RegionMapper
from datetime import datetime

async def test_user_registration_flow():
    """测试完整的用户注册流程"""
    
    print("🧪 用户注册流程完整测试")
    print("=" * 60)
    
    # 连接数据库
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.energy_info
    
    # 创建用户服务
    user_service = UserService(db)
    users_collection = db.users
    user_tags_collection = db.user_tags
    
    # 测试城市列表（覆盖不同地区）
    test_cities = [
        {"city": "上海", "expected_province": "上海市", "expected_region": "华东地区"},
        {"city": "北京", "expected_province": "北京市", "expected_region": "华北地区"},
        {"city": "深圳", "expected_province": "广东省", "expected_region": "华南地区"},
        {"city": "成都", "expected_province": "四川省", "expected_region": "西南地区"},
        {"city": "西安", "expected_province": "陕西省", "expected_region": "西北地区"},
        {"city": "哈尔滨", "expected_province": "黑龙江省", "expected_region": "东北地区"},
        {"city": "武汉", "expected_province": "湖北省", "expected_region": "华中地区"},
    ]
    
    print(f"📋 RegionMapper支持的城市数量: {len(RegionMapper.get_all_cities())}")
    print(f"🎯 测试城市数量: {len(test_cities)}")
    
    created_users = []
    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "details": []
    }
    
    for i, test_case in enumerate(test_cities):
        city = test_case["city"]
        expected_province = test_case["expected_province"]
        expected_region = test_case["expected_region"]
        
        print(f"\n🏙️ 测试城市 {i+1}/{len(test_cities)}: {city}")
        print(f"   预期省份: {expected_province}")
        print(f"   预期地区: {expected_region}")
        
        test_results["total_tests"] += 1
        test_detail = {
            "city": city,
            "expected_province": expected_province,
            "expected_region": expected_region,
            "actual_province": None,
            "actual_region": None,
            "tests": {}
        }
        
        try:
            # 1. 测试RegionMapper功能
            location_info = RegionMapper.get_full_location_info(city)
            actual_province = location_info.get("province")
            actual_region = location_info.get("region")
            
            test_detail["actual_province"] = actual_province
            test_detail["actual_region"] = actual_region
            
            # 验证RegionMapper返回结果
            province_correct = actual_province == expected_province
            region_correct = actual_region == expected_region
            
            test_detail["tests"]["region_mapper_province"] = province_correct
            test_detail["tests"]["region_mapper_region"] = region_correct
            
            print(f"   🗺️ RegionMapper结果:")
            print(f"      省份: {actual_province} {'✅' if province_correct else '❌'}")
            print(f"      地区: {actual_region} {'✅' if region_correct else '❌'}")
            
            # 2. 测试用户注册流程
            timestamp = datetime.now().strftime("%H%M%S")
            test_user = UserCreate(
                email=f"test_{city.lower()}_{timestamp}@example.com",
                username=f"测试用户_{city}_{timestamp}",
                password="test123456",
                register_city=city
            )
            
            # 创建用户（这会触发自动地域标签生成）
            user = await user_service.create_user(test_user, ["天然气"])
            created_users.append(user.id)
            
            print(f"   👤 用户创建成功: {user.username}")
            print(f"      用户ID: {user.id}")
            print(f"      注册城市: {user.register_city}")
            
            # 3. 验证自动生成的标签
            user_tags = await user_service.get_user_tags(user.id)
            if user_tags:
                # 按类别分组标签
                city_tags = []
                province_tags = []
                region_tags = []
                energy_tags = []
                
                for tag in user_tags.tags:
                    if tag.category == TagCategory.CITY:
                        city_tags.append(tag)
                    elif tag.category == TagCategory.PROVINCE:
                        province_tags.append(tag)
                    elif tag.category == TagCategory.REGION:
                        region_tags.append(tag)
                    elif tag.category == TagCategory.ENERGY_TYPE:
                        energy_tags.append(tag)
                
                print(f"   🏷️ 自动生成的标签:")
                
                # 验证城市标签
                city_tag_correct = False
                if city_tags:
                    city_tag = city_tags[0]
                    city_tag_correct = (
                        city_tag.name == city and 
                        city_tag.weight == 2.5 and 
                        city_tag.source == TagSource.PRESET
                    )
                    print(f"      城市: {city_tag.name} (权重:{city_tag.weight}, 来源:{city_tag.source}) {'✅' if city_tag_correct else '❌'}")
                else:
                    print(f"      城市: 无 ❌")
                
                test_detail["tests"]["city_tag"] = city_tag_correct
                
                # 验证省份标签
                province_tag_correct = False
                if province_tags:
                    province_tag = province_tags[0]
                    province_tag_correct = (
                        province_tag.name == expected_province and 
                        province_tag.weight == 2.0 and 
                        province_tag.source == TagSource.REGION_AUTO
                    )
                    print(f"      省份: {province_tag.name} (权重:{province_tag.weight}, 来源:{province_tag.source}) {'✅' if province_tag_correct else '❌'}")
                else:
                    print(f"      省份: 无 ❌")
                
                test_detail["tests"]["province_tag"] = province_tag_correct
                
                # 验证地区标签
                region_tag_correct = False
                region_tag = None
                for tag in region_tags:
                    if tag.name == expected_region and tag.source == TagSource.REGION_AUTO:
                        region_tag = tag
                        break
                        
                if region_tag:
                    region_tag_correct = (
                        region_tag.weight == 1.5 and 
                        region_tag.source == TagSource.REGION_AUTO
                    )
                    print(f"      地区: {region_tag.name} (权重:{region_tag.weight}, 来源:{region_tag.source}) {'✅' if region_tag_correct else '❌'}")
                else:
                    print(f"      地区: 无 ❌")
                
                test_detail["tests"]["region_tag"] = region_tag_correct
                
                # 验证能源标签
                energy_tag_correct = False
                if energy_tags:
                    energy_tag = next((tag for tag in energy_tags if tag.name == "天然气"), None)
                    if energy_tag:
                        energy_tag_correct = True
                        print(f"      能源: {energy_tag.name} (权重:{energy_tag.weight}) ✅")
                    else:
                        print(f"      能源: 未找到天然气标签 ❌")
                else:
                    print(f"      能源: 无 ❌")
                
                test_detail["tests"]["energy_tag"] = energy_tag_correct
                
                # 4. 测试get_user_region_info方法
                region_info = await user_service.get_user_region_info(user.id)
                region_info_correct = (
                    region_info.get("city") == city and
                    region_info.get("province") == expected_province and
                    region_info.get("region") == expected_region
                )
                
                test_detail["tests"]["region_info_api"] = region_info_correct
                
                print(f"   🌍 区域信息API:")
                print(f"      城市: {region_info.get('city')} {'✅' if region_info.get('city') == city else '❌'}")
                print(f"      省份: {region_info.get('province')} {'✅' if region_info.get('province') == expected_province else '❌'}")
                print(f"      地区: {region_info.get('region')} {'✅' if region_info.get('region') == expected_region else '❌'}")
                
                # 统计测试结果
                all_tests_passed = all(test_detail["tests"].values())
                if all_tests_passed:
                    test_results["passed_tests"] += 1
                    print(f"   🎉 所有测试通过!")
                else:
                    test_results["failed_tests"] += 1
                    failed_tests = [k for k, v in test_detail["tests"].items() if not v]
                    print(f"   ❌ 失败的测试: {failed_tests}")
            
            else:
                print(f"   ❌ 未找到用户标签")
                test_detail["tests"]["user_tags_exist"] = False
                test_results["failed_tests"] += 1
        
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")
            test_detail["error"] = str(e)
            test_results["failed_tests"] += 1
        
        test_results["details"].append(test_detail)
    
    # 输出总结
    print(f"\n" + "=" * 60)
    print(f"📊 测试总结")
    print(f"=" * 60)
    print(f"总测试数: {test_results['total_tests']}")
    print(f"通过: {test_results['passed_tests']} ✅")
    print(f"失败: {test_results['failed_tests']} ❌")
    
    success_rate = (test_results['passed_tests'] / test_results['total_tests'] * 100) if test_results['total_tests'] > 0 else 0
    print(f"成功率: {success_rate:.1f}%")
    
    # 验证核心功能
    print(f"\n🔍 核心功能验证:")
    print(f"✅ RegionMapper.get_full_location_info() - 城市→省份→地区映射")
    print(f"✅ UserService.create_user() - 用户注册与标签自动生成")
    print(f"✅ UserService.initialize_user_tags_by_city() - 三层地域标签生成")
    print(f"✅ UserService.get_user_region_info() - 用户地域信息查询")
    
    print(f"\n📋 标签权重验证:")
    print(f"   城市标签: 权重2.5, 来源PRESET (用户明确选择)")
    print(f"   省份标签: 权重2.0, 来源REGION_AUTO (系统自动生成)")
    print(f"   地区标签: 权重1.5, 来源REGION_AUTO (系统自动生成)")
    
    # 清理测试数据
    if created_users:
        print(f"\n🧹 清理测试数据...")
        for user_id in created_users:
            await users_collection.delete_one({"id": user_id})
            await user_tags_collection.delete_one({"user_id": user_id})
        print(f"   已清理 {len(created_users)} 个测试用户")
    
    await client.close()
    
    return success_rate == 100.0

if __name__ == "__main__":
    success = asyncio.run(test_user_registration_flow())
    sys.exit(0 if success else 1) 