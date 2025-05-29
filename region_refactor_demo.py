#!/usr/bin/env python3
"""
用户功能重构演示脚本

展示了重构后的两层地区逻辑：
1. 前台页面逻辑：城市级别选择（上海、深圳、广州等）
2. 后台标签逻辑：根据城市自动计算区域标签（如上海→华东地区）
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.utils.region_mapper import RegionMapper, RegionCode
from backend.app.services.user_service import UserService
from backend.app.models.user import UserCreate, TagCategory, TagSource
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

def print_header(title: str):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)

def print_section(title: str):
    """打印小节标题"""
    print(f"\n--- {title} ---")

async def demonstrate_region_refactor():
    """演示区域重构功能"""
    
    print_header("用户功能重构演示：两层地区逻辑")
    
    # 1. 展示城市-区域映射
    print_section("1. 城市-区域映射展示")
    
    demo_cities = ["上海", "深圳", "广州", "北京", "成都", "西安", "沈阳", "武汉"]
    
    print("支持的城市及其对应区域：")
    for city in demo_cities:
        region_code = RegionMapper.get_region_by_city(city)
        region_name = RegionMapper.get_region_name(region_code) if region_code else "未知"
        print(f"  📍 {city:6} → {region_name}")
    
    print(f"\n总计支持 {len(RegionMapper.get_all_cities())} 个城市")
    
    # 2. 展示区域分布
    print_section("2. 区域分布统计")
    
    regions = RegionMapper.get_all_regions()
    for region in regions:
        cities_in_region = RegionMapper.get_cities_by_region(region["code"])
        print(f"  🌍 {region['name']:8} ({region['code']:15}): {len(cities_in_region):2}个城市")
        if len(cities_in_region) <= 5:
            print(f"     城市列表: {', '.join(cities_in_region)}")
        else:
            print(f"     示例城市: {', '.join(cities_in_region[:5])}...")
    
    # 3. 演示用户注册流程
    print_section("3. 用户注册流程演示")
    
    try:
        # 连接数据库
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        database = client.demo_energy_info
        user_service = UserService(database)
        
        # 模拟三个不同城市的用户注册
        demo_users = [
            {
                "city": "上海",
                "username": "shanghai_user",
                "energy_types": ["天然气", "LNG"]
            },
            {
                "city": "深圳", 
                "username": "shenzhen_user",
                "energy_types": ["电力", "原油"]
            },
            {
                "city": "成都",
                "username": "chengdu_user", 
                "energy_types": ["天然气", "煤炭"]
            }
        ]
        
        created_users = []
        
        for user_data in demo_users:
            city = user_data["city"]
            print(f"\n👤 模拟用户注册 - 注册城市：{city}")
            
            # 创建用户
            test_user = UserCreate(
                email=f"{user_data['username']}@example.com",
                username=user_data["username"],
                password="demo123456",
                register_city=city
            )
            
            user = await user_service.create_user(test_user, user_data["energy_types"])
            created_users.append(user)
            
            print(f"   ✅ 用户创建成功：{user.username}")
            print(f"   📧 邮箱：{user.email}")
            print(f"   🏙️  注册城市：{user.register_city}")
            
            # 获取自动生成的标签
            user_tags = await user_service.get_user_tags(user.id)
            if user_tags:
                region_tags = [tag for tag in user_tags.tags if tag.category == TagCategory.REGION]
                energy_tags = [tag for tag in user_tags.tags if tag.category == TagCategory.ENERGY_TYPE]
                
                print(f"   🏷️  自动生成的区域标签：")
                for tag in region_tags:
                    source_desc = {
                        TagSource.PRESET: "城市标签",
                        TagSource.REGION_AUTO: "区域标签(自动)",
                        TagSource.MANUAL: "手动标签"
                    }.get(tag.source, "未知")
                    print(f"      - {tag.name} (权重:{tag.weight}, 来源:{source_desc})")
                
                print(f"   ⚡ 能源品种标签：")
                for tag in energy_tags:
                    print(f"      - {tag.name} (权重:{tag.weight})")
            
            # 获取区域信息
            region_info = await user_service.get_user_region_info(user.id)
            print(f"   🌍 区域信息：{region_info}")
        
        # 4. 展示标签分析
        print_section("4. 用户标签分析")
        
        print("各城市用户的标签分布：")
        for user in created_users:
            user_tags = await user_service.get_user_tags(user.id)
            if user_tags:
                region_tags = [tag for tag in user_tags.tags if tag.category == TagCategory.REGION]
                print(f"\n  👤 {user.username} ({user.register_city}):")
                print(f"     标签总数：{len(user_tags.tags)}")
                print(f"     区域标签：{len(region_tags)}个")
                for tag in region_tags:
                    tag_type = "🏙️ 城市" if tag.source == TagSource.PRESET else "🌍 区域"
                    print(f"       {tag_type}: {tag.name} (权重:{tag.weight})")
        
        # 5. 展示API响应数据结构
        print_section("5. API响应数据结构示例")
        
        # 支持的城市列表API响应
        cities_api_response = {
            "cities": sorted(RegionMapper.get_all_cities())[:10],  # 只显示前10个
            "regions": RegionMapper.get_all_regions(),
            "total_cities": len(RegionMapper.get_all_cities())
        }
        
        print("GET /api/v1/users/supported-cities 响应：")
        print(f"  城市列表（前10个）: {cities_api_response['cities']}")
        print(f"  总城市数: {cities_api_response['total_cities']}")
        print("  区域列表:")
        for region in cities_api_response['regions'][:3]:  # 只显示前3个
            print(f"    - {region['name']} ({region['code']})")
        print("    ...")
        
        # 用户区域信息API响应
        first_user = created_users[0]
        region_info = await user_service.get_user_region_info(first_user.id)
        user_region_api_response = {
            "user_id": first_user.id,
            "city": region_info["city"],
            "region": region_info["region"], 
            "region_code": str(region_info["region_code"])
        }
        
        print(f"\nGET /api/v1/users/{first_user.id[:8]}.../region-info 响应：")
        for key, value in user_region_api_response.items():
            print(f"  {key}: {value}")
        
        # 清理演示数据
        print_section("6. 清理演示数据")
        for user in created_users:
            await user_service.users_collection.delete_one({"id": user.id})
            await user_service.user_tags_collection.delete_one({"user_id": user.id})
            print(f"   🗑️  已清理用户：{user.username}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ 演示过程中出错：{str(e)}")
        import traceback
        traceback.print_exc()
    
    # 7. 总结重构效果
    print_section("7. 重构总结")
    
    print("🎉 用户功能重构完成！")
    print("\n📋 重构内容：")
    print("  1. ✅ 前台页面逻辑：从区域选择改为城市选择")
    print("  2. ✅ 后台标签逻辑：根据城市自动生成区域标签")
    print("  3. ✅ 两层标签体系：城市标签(页面展示) + 区域标签(推荐算法)")
    print("  4. ✅ 支持68个主要城市，覆盖7大区域")
    print("  5. ✅ 新增API接口：获取支持城市列表、用户区域信息")
    
    print("\n🔧 技术实现：")
    print("  - RegionMapper：城市-区域映射工具类")
    print("  - TagSource.REGION_AUTO：区域自动生成标签源")
    print("  - UserCreate.register_city：用户注册城市字段")
    print("  - 权重设计：城市标签(2.0) > 区域标签(1.5) > 其他标签(1.0)")
    
    print("\n💡 用户体验改进：")
    print("  - 用户注册时选择具体城市，更精确的地理定位")
    print("  - 系统自动计算区域归属，减少用户选择负担")
    print("  - 前台显示城市，后台用区域做内容推荐")
    print("  - 支持城市搜索，提升选择效率")

async def main():
    """主函数"""
    await demonstrate_region_refactor()

if __name__ == "__main__":
    asyncio.run(main()) 