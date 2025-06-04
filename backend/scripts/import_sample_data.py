#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上海石油天然气交易中心信息门户系统 - 统一数据导入脚本
使用完整的51篇文章数据集，确保与TagProcessor的标签一致性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.content import Content, ContentType, ContentTag
from app.models.user import User, UserRole, UserCreate, TagCategory, TagSource
from app.services.user_service import UserService
from app.utils.tag_processor import TagProcessor  # 导入统一标签处理器
from passlib.context import CryptContext
from typing import List
import ast

# 使用统一的标签处理器配置
CONTENT_TYPE_MAP = TagProcessor.CONTENT_TYPE_MAP

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_content_type(basic_info_tags):
    """根据基础信息标签确定内容类型，使用TagProcessor的标准映射"""
    if not basic_info_tags:
        return ContentType.NEWS  # 默认为行业资讯
    
    # 检查是否包含标准化的基础信息标签
    for tag in basic_info_tags:
        if tag in ["政策法规"]:
            return ContentType.POLICY
        elif tag in ["调价公告"]:
            return ContentType.PRICE
        elif tag in ["交易公告"]:
            return ContentType.ANNOUNCEMENT
        elif tag in ["行业资讯", "研报分析"]:
            return ContentType.NEWS
    
    return ContentType.NEWS  # 默认为行业资讯

def parse_tag_string(tag_str) -> List[str]:
    """解析标签字符串，支持多种格式"""
    if not tag_str:
        return []
    
    # 如果已经是列表，直接返回
    if isinstance(tag_str, list):
        return [str(tag).strip() for tag in tag_str if tag and str(tag).strip()]
    
    # 处理字符串格式的标签
    tag_str = str(tag_str).strip()
    if not tag_str or tag_str in ['[]', '[""]', "['']", 'null', 'None']:
        return []
    
    # 尝试解析JSON格式
    try:
        parsed = ast.literal_eval(tag_str)
        if isinstance(parsed, list):
            return [str(tag).strip() for tag in parsed if tag and str(tag).strip()]
    except:
        pass
    
    # 简单分割处理
    if ',' in tag_str:
        return [tag.strip().strip("'\"") for tag in tag_str.split(',') if tag.strip()]
    
    return [tag_str.strip().strip("'\"")]

def normalize_basic_info_tags(tags):
    """标准化基础信息标签，使用TagProcessor的标准"""
    if not tags:
        return ["行业资讯"]  # 默认标签
    
    normalized = []
    for tag in tags:
        tag = str(tag).strip()
        # 使用TagProcessor的标准基础信息标签
        if tag in TagProcessor.STANDARD_BASIC_INFO_TAGS:
            normalized.append(tag)
        else:
            # 映射到标准标签
            tag_lower = tag.lower()
            if "政策" in tag or "法规" in tag or "通知" in tag or "规定" in tag:
                normalized.append("政策法规")
            elif "价格" in tag or "调价" in tag:
                normalized.append("调价公告")
            elif "交易" in tag or "公告" in tag:
                normalized.append("交易公告")
            elif "研报" in tag or "分析" in tag:
                normalized.append("研报分析")
            else:
                normalized.append("行业资讯")  # 默认
    
    return list(set(normalized))  # 去重

def normalize_energy_type_tags(tags):
    """标准化能源类型标签，确保符合TagProcessor标准"""
    if not tags:
        return []
    
    normalized = []
    standard_energy_types = TagProcessor.STANDARD_ENERGY_TYPES
    
    for tag in tags:
        tag = str(tag).strip()
        if tag in standard_energy_types:
            normalized.append(tag)
        else:
            # 映射常见的非标准标签 - 与TagProcessor.STANDARD_ENERGY_TYPES完全一致
            tag_lower = tag.lower()
            if "lng" in tag_lower or "液化天然气" in tag:
                normalized.append("液化天然气(LNG)")
            elif "png" in tag_lower or "管道天然气" in tag:
                normalized.append("管道天然气(PNG)")
            elif "lpg" in tag_lower or "液化石油气" in tag:
                normalized.append("液化石油气(LPG)")
            elif "天然气" in tag and "液化" not in tag and "管道" not in tag:
                normalized.append("天然气")
            elif "原油" in tag:
                normalized.append("原油")
            elif "重烃" in tag:
                normalized.append("重烃")
            elif "电力" in tag:
                normalized.append("电力")
            elif "汽油" in tag:
                normalized.append("汽油")
            elif "柴油" in tag and "生物" not in tag:
                normalized.append("柴油")
            elif "生物柴油" in tag:
                normalized.append("生物柴油")
            elif "沥青" in tag:
                normalized.append("沥青")
            elif "石油焦" in tag:
                normalized.append("石油焦")
            elif "煤炭" in tag or "动力煤" in tag or "煤" in tag:
                normalized.append("煤炭")
            elif "核能" in tag or "核电" in tag:
                normalized.append("核能")
            elif "可再生能源" in tag or ("可再生" in tag and "能源" in tag):
                normalized.append("可再生能源")
            elif "生物质能" in tag or ("生物质" in tag and ("能" in tag or "发电" in tag)):
                normalized.append("生物质能")
            elif "氢能" in tag or "氢燃料" in tag or "氢气" in tag:
                normalized.append("氢能")
            # 如果无法映射，保留原标签（但会在后续验证中标记）
            else:
                normalized.append(tag)
    
    return list(set(normalized))  # 去重

async def import_articles(use_simplified=True):
    """导入文章数据到数据库"""
    try:
        # 使用清理后的统一数据集
        data_file = "scripts/能源信息服务系统_清理重复字段_51篇.json"
        print(f"📖 开始导入数据: {data_file}")
        
        with open(data_file, 'r', encoding='utf-8') as f:
            articles_data = json.load(f)
        
        if not articles_data:
            print("❌ 没有找到文章数据")
            return
        
        print(f"📊 准备导入 {len(articles_data)} 篇文章")
        
        # 初始化数据库连接
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client["energy_info"]
        content_collection = db["content"]
        
        # 清空现有数据
        await content_collection.delete_many({})
        print("🗑️  已清空现有文章数据")
        
        # 统计信息
        success_count = 0
        error_count = 0
        basic_info_counts = {}
        energy_type_counts = {}
        
        # 逐篇导入文章
        for i, article_data in enumerate(articles_data, 1):
            try:
                # 基础字段处理
                title = article_data.get('标题', f'未知标题_{i}')
                content = article_data.get('文章内容', '')
                publish_date_str = article_data.get('发布日期') or article_data.get('发布时间', '2025-01-01')
                source = article_data.get('来源机构', '未知来源')
                link = article_data.get('链接', '')
                
                # 🔥 正确处理发布时间：将发布日期转换为datetime对象
                publish_time = None
                publish_date = None
                
                try:
                    if publish_date_str:
                        # 如果是YYYY-MM-DD格式，补全时分秒为00:00:00
                        if len(publish_date_str) == 10 and '-' in publish_date_str:
                            publish_time = datetime.strptime(publish_date_str + " 00:00:00", "%Y-%m-%d %H:%M:%S")
                            publish_date = publish_date_str
                        else:
                            # 尝试其他格式
                            publish_time = datetime.fromisoformat(publish_date_str.replace('Z', '+00:00'))
                            publish_date = publish_time.strftime('%Y-%m-%d')
                    else:
                        # 如果没有发布时间，使用当前时间
                        publish_time = datetime.now()
                        publish_date = publish_time.strftime('%Y-%m-%d')
                except Exception as e:
                    print(f"⚠️ 解析时间失败: {title[:30]} - {publish_date_str} - {str(e)}")
                    publish_time = datetime.now()
                    publish_date = publish_time.strftime('%Y-%m-%d')
                
                # 🔥 直接使用清理后的basic_info_tags字段
                basic_info_tags_raw = article_data.get('basic_info_tags', [])
                
                # 确保basic_info_tags是数组格式
                if isinstance(basic_info_tags_raw, str):
                    basic_info_tags = parse_tag_string(basic_info_tags_raw)
                elif isinstance(basic_info_tags_raw, list):
                    basic_info_tags = basic_info_tags_raw
                else:
                    basic_info_tags = []
                
                # 标准化基础信息标签
                basic_info_tags = normalize_basic_info_tags(basic_info_tags)
                
                # 🔥 基于基础信息标签确定内容类型
                content_type = get_content_type(basic_info_tags)
                
                # 处理其他标签字段
                energy_type_tags_raw = article_data.get('能源品种标签', [])
                if isinstance(energy_type_tags_raw, str):
                    energy_type_tags = parse_tag_string(energy_type_tags_raw)
                else:
                    energy_type_tags = energy_type_tags_raw if isinstance(energy_type_tags_raw, list) else []
                
                energy_type_tags = normalize_energy_type_tags(energy_type_tags)
                
                # 地域标签处理
                region_tags = []
                if article_data.get('规范化地域标签'):
                    region_tags.extend(article_data['规范化地域标签'])
                
                # 业务领域标签
                business_field_tags_raw = article_data.get('业务领域/主题标签', [])
                business_field_tags = parse_tag_string(business_field_tags_raw) if isinstance(business_field_tags_raw, str) else business_field_tags_raw
                
                # 受益主体标签
                beneficiary_tags_raw = article_data.get('受益主体标签', [])
                beneficiary_tags = parse_tag_string(beneficiary_tags_raw) if isinstance(beneficiary_tags_raw, str) else beneficiary_tags_raw
                
                # 政策措施标签
                policy_measure_tags_raw = article_data.get('关键措施/政策标签', [])
                policy_measure_tags = parse_tag_string(policy_measure_tags_raw) if isinstance(policy_measure_tags_raw, str) else policy_measure_tags_raw
                
                # 重要性标签
                importance_tags_raw = article_data.get('重要性/影响力标签', [])
                importance_tags = parse_tag_string(importance_tags_raw) if isinstance(importance_tags_raw, str) else importance_tags_raw
                
                # 🔥 创建文章文档，同时包含publish_date和publish_time字段
                article_doc = {
                    "title": title,
                    "content": content,
                    "publish_date": publish_date,  # 字符串格式的日期
                    "publish_time": publish_time,  # datetime对象
                    "source": source,
                    "link": link,
                    "type": content_type,  # 🔥 基于basic_info_tags生成
                    "basic_info_tags": basic_info_tags,
                    "region_tags": region_tags,
                    "energy_type_tags": energy_type_tags,
                    "business_field_tags": business_field_tags if isinstance(business_field_tags, list) else [],
                    "beneficiary_tags": beneficiary_tags if isinstance(beneficiary_tags, list) else [],
                    "policy_measure_tags": policy_measure_tags if isinstance(policy_measure_tags, list) else [],
                    "importance_tags": importance_tags if isinstance(importance_tags, list) else [],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                # 插入数据库
                result = await content_collection.insert_one(article_doc)
                
                if result.inserted_id:
                    success_count += 1
                    
                    # 统计基础信息标签
                    for tag in basic_info_tags:
                        basic_info_counts[tag] = basic_info_counts.get(tag, 0) + 1
                    
                    # 统计能源类型标签
                    for tag in energy_type_tags:
                        energy_type_counts[tag] = energy_type_counts.get(tag, 0) + 1
                    
                    if i <= 5:
                        print(f"✅ 文章 {i}: {title[:30]}... -> {publish_date}")
                else:
                    error_count += 1
                    print(f"❌ 文章 {i} 插入失败")
                    
            except Exception as e:
                error_count += 1
                print(f"❌ 处理文章 {i} 时出错: {str(e)}")
        
        # 输出统计信息
        print(f"\n📊 导入完成统计：")
        print(f"成功导入: {success_count} 篇")
        print(f"导入失败: {error_count} 篇")
        print(f"总计: {len(articles_data)} 篇")
        
        # 📋 基础信息标签分布（验证清理效果）
        print(f"\n📊 基础信息标签分布：")
        for tag, count in sorted(basic_info_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tag}: {count} 篇")
        
        print(f"   基础信息标签已标准化: {len(basic_info_counts)} 种")
        
        # 🏷️ 能源类型标签分布
        print(f"\n🏷️ 能源类型标签分布（前10）：")
        sorted_energy = sorted(energy_type_counts.items(), key=lambda x: x[1], reverse=True)
        for tag, count in sorted_energy[:10]:
            print(f"  {tag}: {count} 篇")
        
        # 🔥 关闭数据库连接
        if client:
            client.close()
        print(f"\n✅ 数据导入完成！使用清理后的标准化数据，publish_time字段已正确设置")
        
    except Exception as e:
        print(f"❌ 导入过程出错: {str(e)}")
        raise

async def create_sample_users():
    """创建示例用户数据"""
    client = None
    try:
        # 初始化MongoDB客户端
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        users_collection = db.users
        user_tags_collection = db.user_tags
        
        # 清空现有数据
        await users_collection.delete_many({})
        await user_tags_collection.delete_many({})
        print("Cleared existing user data")
        
        # 创建UserService实例
        user_service = UserService(db)
        
        # 📊 根据能源标签覆盖率优化的演示用户（每用户1个能源标签）
        # 覆盖率统计：天然气42.2%，原油42.2%，LNG24.4%，PNG22.2%，电力8.9%
        demo_users = [
            {
                "email": "zhang@shanghai.com",
                "username": "张工程师",
                "password": "demo123",
                "register_city": "上海",
                "energy_types": ["液化石油气(LPG)"],  # 覆盖率最高：42.2% (19篇)
                "user_id": "user001",
                "description": "石油与天然气市场分析师 - 关注行业价格与政策"
            },
            {
                "email": "li@beijing.com", 
                "username": "李经理",
                "password": "demo123",
                "register_city": "北京",
                "energy_types": ["重烃"],  # 覆盖率最高：42.2% (19篇)
                "user_id": "user002",
                "description": "石油贸易专家 - 原油进口与价格分析"
            },
            {
                "email": "wang@shenzhen.com",
                "username": "王主任", 
                "password": "demo123",
                "register_city": "深圳",
                "energy_types": ["液化天然气(LNG)"],  # 第三高：24.4% (11篇)
                "user_id": "user003",
                "description": "LNG项目经理 - 液化天然气接收站运营"
            },
            {
                "email": "chen@guangzhou.com",
                "username": "陈总监",
                "password": "demo123", 
                "register_city": "广州",
                "energy_types": ["管道天然气(PNG)"],  # 第四高：22.2% (10篇)
                "user_id": "user004",
                "description": "管道天然气运营专家 - 天然气管网建设"
            },
            {
                "email": "liu@chengdu.com",
                "username": "刘研究员",
                "password": "demo123",
                "register_city": "成都",
                "energy_types": ["电力"],  # 第五高：8.9% (4篇)
                "user_id": "user005", 
                "description": "电力系统研究员 - 可再生能源发电"
            }
        ]
        
        created_count = 0
        for user_data in demo_users:
            try:
                # 创建用户对象
                user_create = UserCreate(
                    email=user_data["email"],
                    username=user_data["username"],
                    password=user_data["password"],
                    register_city=user_data["register_city"]
                )
                
                # 创建用户（包含三层地区标签）
                user = await user_service.create_user(
                    user_create, 
                    energy_types=user_data["energy_types"]
                )
                
                # 手动设置用户ID为预设值，确保与前端一致
                await users_collection.update_one(
                    {"id": user.id},
                    {"$set": {"demo_user_id": user_data["user_id"], "description": user_data["description"]}}
                )
                
                # 更新用户标签集合中的用户ID引用
                await user_tags_collection.update_one(
                    {"user_id": user.id},
                    {"$set": {"demo_user_id": user_data["user_id"]}}
                )
                
                created_count += 1
                print(f"Created demo user: {user.username} ({user.email}) - {user_data['register_city']}")
                print(f"  Demo ID: {user_data['user_id']}")
                print(f"  Description: {user_data['description']}")
                
                # 显示生成的标签信息
                user_tags = await user_service.get_user_tags(user.id)
                if user_tags:
                    print(f"  Generated tags:")
                    for tag in user_tags.tags:
                        print(f"    - {tag.category}: {tag.name} (权重: {tag.weight}, 来源: {tag.source})")
                print("")
                
            except Exception as e:
                print(f"Error creating user {user_data['email']}: {str(e)}")
        
        print(f"Total demo users created: {created_count}")
        
    except Exception as e:
        print(f"Error creating sample users: {str(e)}")
    finally:
        if client:
            client.close()

async def main():
    """主函数"""
    import sys
    
    # 检查命令行参数
    use_simplified = True  # 默认使用简化数据
    if len(sys.argv) > 1:
        if sys.argv[1] == '--full' or sys.argv[1] == '-f':
            use_simplified = False
        elif sys.argv[1] == '--use-simplified-data' or sys.argv[1] == '--simplified':
            use_simplified = True
        elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("使用方法:")
            print("  python import_sample_data.py                    # 使用简化测试数据（每篇3-5标签）")
            print("  python import_sample_data.py --simplified       # 使用简化测试数据（同上）")
            print("  python import_sample_data.py --use-simplified-data # 使用简化测试数据（同上）")
            print("  python import_sample_data.py -f                 # 使用完整原始数据（每篇15+标签）")
            print("  python import_sample_data.py --full             # 同上")
            return
    
    print(f"📊 开始数据导入... 使用{'简化' if use_simplified else '完整'}数据")
    print("=" * 60)
    
    print("Starting data import...")
    
    # 导入文章数据
    print("\n1. Importing articles...")
    await import_articles(use_simplified=use_simplified)
    
    # 创建示例用户
    print("\n2. Creating sample users...")
    await create_sample_users()
    
    print("\nData import completed!")
    
    if use_simplified:
        print("\n🎯 已导入简化测试数据！")
        print("💡 测试建议：")
        print("   1. 前端标签管理页面修改用户标签")
        print("   2. 观察首页推荐内容的变化")
        print("   3. 标签少更容易看出推荐差异")
    else:
        print("\n📋 已导入完整原始数据")
        print("⚠️  注意：每篇文章标签较多，可能不利于测试推荐效果")

if __name__ == "__main__":
    asyncio.run(main()) 