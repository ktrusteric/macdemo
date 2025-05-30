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
import ast

# 内容类型映射
CONTENT_TYPE_MAP = {
    "政策法规": ContentType.POLICY,
    "行业资讯": ContentType.NEWS,
    "调价公告": ContentType.PRICE,
    "交易公告": ContentType.ANNOUNCEMENT
}

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_content_type(basic_info_tags):
    """根据基础信息标签确定内容类型"""
    for tag in basic_info_tags:
        if '政策' in tag or '法规' in tag:
            return ContentType.POLICY
        elif '调价' in tag or '价格' in tag:
            return ContentType.PRICE
        elif '公告' in tag:
            return ContentType.ANNOUNCEMENT
    return ContentType.NEWS

async def import_articles(use_simplified=True):
    """导入文章数据"""
    print("📚 导入文章数据...")
    
    # 初始化数据库连接
    client = None
    try:
        # 初始化MongoDB客户端
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        collection = db.content
        
        # 清理现有数据
        await collection.delete_many({})
        print("Cleared existing content data")
        
        # 选择数据文件
        if use_simplified:
            json_file_path = os.path.join(os.path.dirname(__file__), "简化测试数据.json")
            print("🔧 使用简化测试数据（每篇文章3-5个标签，便于测试）")
        else:
            json_file_path = os.path.join(os.path.dirname(__file__), "信息发布文章与标签.json")
            print("📋 使用完整原始数据（每篇文章15+个标签）")
        
        # 检查文件是否存在
        if not os.path.exists(json_file_path):
            print(f"❌ 数据文件不存在: {json_file_path}")
            return
        
        # 读取JSON数据
        with open(json_file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        articles = []
        energy_type_counts = {}
        
        # 提取标签的辅助函数
        def extract_tags(data, key, fallback_key=None):
            tags = data.get(key, [])
            if not tags and fallback_key:
                tags = data.get(fallback_key, [])
            
            # 处理字符串格式的标签（如 "['交易公告']"）
            if isinstance(tags, str):
                try:
                    # 尝试使用ast.literal_eval安全解析
                    tags = ast.literal_eval(tags)
                except (ValueError, SyntaxError):
                    # 如果解析失败，返回空列表
                    tags = []
            
            return tags if isinstance(tags, list) else []
        
        for article_data in raw_data:
            # 标准化标签 - 使用正确的中文字段名
            basic_info_tags = extract_tags(article_data, "基础信息标签")
            energy_type_tags = extract_tags(article_data, "能源品种标签") 
            region_tags = extract_tags(article_data, "地域标签")
            business_field_tags = extract_tags(article_data, "业务领域/主题标签")
            beneficiary_tags = extract_tags(article_data, "受益主体标签") 
            policy_measure_tags = extract_tags(article_data, "关键措施/政策标签")
            importance_tags = extract_tags(article_data, "重要性/影响力标签")
            
            # 统计能源类型
            for energy_type in energy_type_tags:
                energy_type_counts[energy_type] = energy_type_counts.get(energy_type, 0) + 1
            
            # 构建文档
            article = {
                'title': article_data.get('标题', ''),
                'content': article_data.get('文章内容', '') or article_data.get('正文', '') or '暂无内容',
                'link': article_data.get('链接', ''),
                'publish_time': article_data.get('发布时间', datetime.now().isoformat()),
                'type': get_content_type(basic_info_tags),
                'basic_info_tags': basic_info_tags,
                'energy_type_tags': energy_type_tags,
                'region_tags': region_tags,
                'business_field_tags': business_field_tags,
                'beneficiary_tags': beneficiary_tags,
                'policy_measure_tags': policy_measure_tags,
                'importance_tags': importance_tags,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            articles.append(article)
        
        # 批量插入
        if articles:
            await collection.insert_many(articles)
            print(f"\n✅ 成功导入 {len(articles)} 篇文章")
            
            # 统计信息
            total_articles = len(articles)
            articles_with_energy_tags = sum(1 for article in articles if article.get("energy_type_tags"))
            print(f"\n📈 覆盖率统计：")
            print(f"   有能源类型标签的文章: {articles_with_energy_tags}/{total_articles} ({articles_with_energy_tags/total_articles*100:.1f}%)")
            
            if energy_type_counts:
                print(f"\n💡 能源类型分布：")
                for energy_type, count in sorted(energy_type_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / total_articles * 100
                    print(f"   {energy_type}: {count} 篇 ({percentage:.1f}%)")
            
            # 天然气类型细分统计
            lng_count = energy_type_counts.get('液化天然气(LNG)', 0)
            png_count = energy_type_counts.get('管道天然气(PNG)', 0)
            general_gas_count = energy_type_counts.get('天然气', 0)
            total_gas = lng_count + png_count + general_gas_count
            
            if total_gas > 0:
                print(f"\n💨 天然气类型细分：")
                print(f"   液化天然气(LNG): {lng_count} 篇 ({lng_count/total_gas*100:.1f}%)")
                print(f"   管道天然气(PNG): {png_count} 篇 ({png_count/total_gas*100:.1f}%)")
                print(f"   通用天然气: {general_gas_count} 篇 ({general_gas_count/total_gas*100:.1f}%)")
        else:
            print("⚠️ 没有文章数据可导入")
    
    except Exception as e:
        print(f"Error importing articles: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if client:
            await client.close()
    
    print("\n✅ 文章数据导入完成！")

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
                "energy_types": ["天然气"],  # 覆盖率最高：42.2% (19篇)
                "user_id": "user001",
                "description": "天然气市场分析师 - 关注天然气价格与政策"
            },
            {
                "email": "li@beijing.com", 
                "username": "李经理",
                "password": "demo123",
                "register_city": "北京",
                "energy_types": ["原油"],  # 覆盖率最高：42.2% (19篇)
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
            await client.close()

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