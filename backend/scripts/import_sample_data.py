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
from passlib.context import CryptContext
from typing import List

# 内容类型映射
CONTENT_TYPE_MAP = {
    "政策法规": ContentType.POLICY,
    "行业资讯": ContentType.NEWS,
    "调价公告": ContentType.PRICE,
    "交易公告": ContentType.ANNOUNCEMENT
}

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def import_articles(use_simplified=False):
    """导入示例文章数据"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    content_collection = db.content
    
    # 清除现有数据
    await content_collection.delete_many({})
    print("Cleared existing content data")
    
    # 选择数据文件
    if use_simplified:
        json_file_path = os.path.join(os.path.dirname(__file__), "简化测试数据.json")
        print("🔧 使用简化测试数据（每篇文章3-6个标签，便于测试）")
    else:
        json_file_path = os.path.join(os.path.dirname(__file__), "信息发布文章与标签.json")
        print("📋 使用完整原始数据（每篇文章15+个标签）")
    
    # 检查文件是否存在
    if not os.path.exists(json_file_path):
        if use_simplified:
            print("❌ 简化测试数据文件不存在，请先运行 create_test_data.py 生成")
            return
        else:
            print("❌ 原始数据文件不存在")
            return
    
    # 读取JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        articles_data = json.load(f)
    
    # 导入文章
    imported_count = 0
    for article_data in articles_data:
        try:
            # 转换文章类型
            content_type = CONTENT_TYPE_MAP.get(article_data.get("文档类型", ""), ContentType.NEWS)
            
            # 处理标签 - 支持两种数据格式
            content_tags = []
            if "标签" in article_data and article_data["标签"]:
                for tag_name in article_data["标签"]:
                    if isinstance(tag_name, str):
                        content_tags.append(ContentTag(category="general", name=tag_name))

            # 处理各类标签 - 统一处理逻辑
            def extract_tags(data, key, fallback_key=None):
                """提取标签的统一函数"""
                tags = []
                # 尝试主键
                if key in data and data[key]:
                    raw_value = data[key]
                    if isinstance(raw_value, str):
                        try:
                            import ast
                            tags = ast.literal_eval(raw_value)
                            if not isinstance(tags, list):
                                tags = [raw_value]
                        except:
                            tags = [raw_value]
                    elif isinstance(raw_value, list):
                        tags = raw_value
                # 尝试备选键（用于简化数据）
                elif fallback_key and fallback_key in data and data[fallback_key]:
                    raw_value = data[fallback_key]
                    if isinstance(raw_value, list):
                        tags = raw_value
                # 特殊处理：如果是基础信息标签且没有找到，使用文档类型
                elif key == "基础信息标签" and "文档类型" in data:
                    tags = [data["文档类型"]]
                return tags

            # 提取各类标签
            basic_info_tags = extract_tags(article_data, "基础信息标签", "basic_info_tags")
            region_tags = extract_tags(article_data, "地域标签", "region_tags")
            energy_type_tags = extract_tags(article_data, "能源品种标签", "energy_type_tags")
            business_field_tags = extract_tags(article_data, "业务领域/主题标签", "business_field_tags")
            beneficiary_tags = extract_tags(article_data, "受益主体标签", "beneficiary_tags")
            policy_measure_tags = extract_tags(article_data, "关键措施/政策标签", "policy_measure_tags")
            importance_tags = extract_tags(article_data, "重要性/影响力标签", "importance_tags")

            # 处理发布时间
            publish_time = None
            for k in ["发布日期", "发布时间"]:
                if k in article_data and article_data[k]:
                    try:
                        publish_time = datetime.strptime(article_data[k], "%Y-%m-%d")
                        break
                    except Exception:
                        pass
            if not publish_time:
                publish_time = datetime.now()

            # 创建内容对象
            content = Content(
                title=article_data.get("标题", ""),
                content=article_data.get("文章内容", ""),
                type=content_type,
                source=article_data.get("来源机构", "官方发布"),
                tags=content_tags,
                publish_time=publish_time,
                link=article_data.get("链接"),
                basic_info_tags=basic_info_tags,
                region_tags=region_tags,
                energy_type_tags=energy_type_tags,
                business_field_tags=business_field_tags,
                beneficiary_tags=beneficiary_tags,
                policy_measure_tags=policy_measure_tags,
                importance_tags=importance_tags
            )
            
            await content_collection.insert_one(content.dict())
            imported_count += 1
            print(f"Imported: {content.title[:50]}...")
            print(f"  basic_info_tags={basic_info_tags}")
            print(f"  region_tags={region_tags}")
            print(f"  energy_type_tags={energy_type_tags}")
            print(f"  business_field_tags={business_field_tags}")
            print(f"  beneficiary_tags={beneficiary_tags}")
            print(f"  policy_measure_tags={policy_measure_tags}")
            print(f"  importance_tags={importance_tags}")
            
        except Exception as e:
            print(f"Error importing article: {str(e)}")
            continue
    
    print(f"\nTotal articles imported: {imported_count}")
    client.close()

async def create_sample_users():
    """创建示例用户数据（包含完整账户信息和正确的能源类型标签）"""
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
    
    # 预设的5个演示用户 - 使用正确的能源类型 (与前端energyTypes对应)
    demo_users = [
        {
            "email": "zhang@newenergy.com",
            "username": "张先生",
            "password": "demo123",
            "register_city": "上海",
            "energy_types": ["电力", "生物柴油", "天然气"],  # 新能源投资者
            "user_id": "user001",
            "description": "新能源投资者 - 关注太阳能、风能项目"
        },
        {
            "email": "li@traditional.com", 
            "username": "李女士",
            "password": "demo123",
            "register_city": "北京",
            "energy_types": ["原油", "天然气", "液化天然气(LNG)", "煤炭"],  # 传统能源
            "user_id": "user002",
            "description": "传统能源企业主 - 石油、天然气行业专家"
        },
        {
            "email": "wang@carbon.com",
            "username": "王先生", 
            "password": "demo123",
            "register_city": "深圳",
            "energy_types": ["电力", "生物柴油", "天然气"],  # 节能减排
            "user_id": "user003",
            "description": "节能减排顾问 - 专注碳中和、环保政策"
        },
        {
            "email": "chen@power.com",
            "username": "陈女士",
            "password": "demo123", 
            "register_city": "广州",
            "energy_types": ["电力", "煤炭", "天然气"],  # 电力系统
            "user_id": "user004",
            "description": "电力系统工程师 - 电网、储能技术专家"
        },
        {
            "email": "liu@policy.com",
            "username": "刘先生",
            "password": "demo123",
            "register_city": "成都",
            "energy_types": ["原油", "天然气", "电力", "煤炭"],  # 政策研究
            "user_id": "user005", 
            "description": "能源政策研究员 - 政策法规、市场分析"
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
            
            # 追加9大类标签（如已存在则跳过）
            extra_tags = [
                {"category": "business_field", "name": "市场动态", "weight": 1.0, "source": "preset", "created_at": datetime.utcnow()},
                {"category": "beneficiary", "name": "能源企业", "weight": 1.0, "source": "preset", "created_at": datetime.utcnow()},
                {"category": "policy_measure", "name": "市场监管", "weight": 1.0, "source": "preset", "created_at": datetime.utcnow()},
                {"category": "importance", "name": "国家级", "weight": 1.0, "source": "preset", "created_at": datetime.utcnow()},
                {"category": "basic_info", "name": "政策法规", "weight": 1.0, "source": "preset", "created_at": datetime.utcnow()},
                {"category": "region", "name": "华东地区", "weight": 1.0, "source": "preset", "created_at": datetime.utcnow()},
                {"category": "region", "name": "全国", "weight": 1.0, "source": "preset", "created_at": datetime.utcnow()}
            ]
            await user_tags_collection.update_one(
                {"user_id": user.id},
                {"$push": {"tags": {"$each": extra_tags}}}
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
    
    client.close()

async def main():
    """主函数"""
    import sys
    
    # 检查命令行参数
    use_simplified = False
    if len(sys.argv) > 1:
        if sys.argv[1] == '--simplified' or sys.argv[1] == '-s':
            use_simplified = True
        elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("使用方法:")
            print("  python import_sample_data.py           # 使用完整原始数据（每篇15+标签）")
            print("  python import_sample_data.py -s        # 使用简化测试数据（每篇3-6标签）")
            print("  python import_sample_data.py --simplified  # 同上")
            return
    
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