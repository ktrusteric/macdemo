#!/usr/bin/env python3
"""
能源信息服务系统 - 整合数据导入脚本 v3.0
合并所有文章到统一的v3版本，简化数据管理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.database import get_database, connect_to_mongo

async def load_complete_articles_data():
    """从JSON文件加载完整的文章数据，并添加v2版本的额外文章"""
    try:
        # 加载v1版本的45篇文章
        json_file_path = os.path.join(os.path.dirname(__file__), '信息发布文章与标签_规范化.json')
        with open(json_file_path, 'r', encoding='utf-8') as f:
            v1_articles = json.load(f)
        
        # v2版本的6篇额外文章
        v2_articles = [
            {
                "发布日期": "2025-05-30",
                "文档类型": "行业资讯",
                "发布时间": "2025-05-30",
                "来源机构": "上海石油天然气交易中心",
                "标题": "密集投产潮下利用率不足50%，LNG接收站市场竞争加剧，如何保障效益",
                "文章内容": "随着全球LNG贸易量持续增长，中国LNG接收站建设进入密集投产期。然而，受市场供需变化影响，部分接收站利用率不足50%，面临严峻的市场竞争压力。行业专家指出，接收站运营商需要通过技术升级、服务优化、商业模式创新等方式提升竞争力，确保投资效益。未来LNG接收站发展需要统筹规划，避免重复建设，提高整体利用效率。",
                "链接": "https://www.shpgx.com/html/xyzx/20250530/7850.html",
                "基础信息标签": "['行业资讯']",
                "地域标签": "['全国']",
                "能源品种标签": ["液化天然气(LNG)"],
                "业务领域/主题标签": "['接收站运营', '市场竞争']",
                "受益主体标签": "['LNG运营商', '能源企业']",
                "关键措施/政策标签": "['技术升级', '商业模式创新']",
                "重要性/影响力标签": "['行业级']",
                "规范化地域标签": ["中国", "全国"]
            },
            {
                "发布日期": "2025-05-30",
                "文档类型": "行业资讯",
                "发布时间": "2025-05-30",
                "来源机构": "上海石油天然气交易中心",
                "标题": "新奥股份重大资产重组获股东大会超99.9%高票通过，天然气产业链一体化战略取得关键进展",
                "文章内容": "新奥股份重大资产重组方案获得股东大会超99.9%的高票通过，标志着公司天然气产业链一体化战略取得关键性进展。此次重组将进一步完善新奥在天然气全产业链的布局，提升公司在LNG贸易、终端销售等关键环节的竞争优势。市场分析认为，这一举措将有助于新奥股份实现规模化发展，提高抗风险能力。",
                "链接": "https://www.shpgx.com/html/xyzx/20250530/7849.html",
                "基础信息标签": "['行业资讯']",
                "地域标签": "['全国']",
                "能源品种标签": ["天然气", "液化天然气(LNG)"],
                "业务领域/主题标签": "['资产重组', '产业链一体化']",
                "受益主体标签": "['新奥股份', '上市公司']",
                "关键措施/政策标签": "['资产重组', '产业链整合']",
                "重要性/影响力标签": "['行业级']",
                "规范化地域标签": ["中国", "全国"]
            },
            {
                "发布日期": "2025-05-30",
                "文档类型": "行业资讯",
                "发布时间": "2025-05-30",
                "来源机构": "上海石油天然气交易中心",
                "标题": "中国石油发布3000亿参数昆仑大模型",
                "文章内容": "中国石油正式发布3000亿参数规模的昆仑大模型，这是石油天然气行业首个千亿级参数大模型。该模型将在勘探开发、炼化生产、销售服务等多个业务场景中应用，通过AI技术提升作业效率和决策水平。专家表示，大模型技术的应用将推动传统能源行业数字化转型，为行业发展注入新动能。",
                "链接": "https://www.shpgx.com/html/xyzx/20250530/7848.html",
                "基础信息标签": "['行业资讯']",
                "地域标签": "['全国']",
                "能源品种标签": ["原油", "天然气"],
                "业务领域/主题标签": "['人工智能', '数字化转型']",
                "受益主体标签": "['中国石油', '能源企业']",
                "关键措施/政策标签": "['技术创新', 'AI应用']",
                "重要性/影响力标签": "['行业级', '技术突破']",
                "规范化地域标签": ["中国", "全国"]
            },
            {
                "发布日期": "2025-05-29",
                "文档类型": "行业资讯",
                "发布时间": "2025-05-29",
                "来源机构": "上海石油天然气交易中心",
                "标题": "5月19日-25日中国LNG综合进口到岸价格指数为131.78点",
                "文章内容": "5月19日-25日当周，中国LNG综合进口到岸价格指数为131.78点，价格相对稳定。随着夏季用气需求逐步减少，LNG市场供需趋于平衡。业内分析认为，二季度LNG价格将保持相对平稳，但需关注国际市场供应端变化和下半年冬季备货需求。",
                "链接": "https://www.shpgx.com/html/xyzx/20250529/7845.html",
                "基础信息标签": "['行业资讯']",
                "地域标签": "['全国']",
                "能源品种标签": ["液化天然气(LNG)"],
                "业务领域/主题标签": "['价格指数', '进口贸易']",
                "受益主体标签": "['LNG贸易商', '城市燃气公司']",
                "关键措施/政策标签": "['价格监测', '供需调节']",
                "重要性/影响力标签": "['市场级']",
                "规范化地域标签": ["中国", "全国"]
            },
            {
                "发布日期": "2025-05-29",
                "文档类型": "行业资讯",
                "发布时间": "2025-05-29",
                "来源机构": "上海石油天然气交易中心",
                "标题": "大港油田储气库群加快扩容 为京津冀冬季保供蓄能",
                "文章内容": "大港油田储气库群正在加快扩容建设，为即将到来的冬季天然气保供做好准备。作为华北地区重要的天然气储备基地，大港储气库群承担着京津冀地区冬季调峰保供的重要任务。预计新增储气能力将有效缓解冬季用气紧张局面，为区域能源安全提供坚实保障。",
                "链接": "https://www.shpgx.com/html/xyzx/20250529/7844.html",
                "基础信息标签": "['行业资讯']",
                "地域标签": "['华北地区']",
                "能源品种标签": ["天然气"],
                "业务领域/主题标签": "['储气库', '冬季保供']",
                "受益主体标签": "['京津冀用户', '城市燃气公司']",
                "关键措施/政策标签": "['储气库建设', '保供措施']",
                "重要性/影响力标签": "['区域级', '民生保障']",
                "规范化地域标签": ["北京", "天津", "河北", "华北地区", "京津冀"]
            },
            {
                "发布日期": "2025-05-28",
                "文档类型": "行业资讯",
                "发布时间": "2025-05-28",
                "来源机构": "上海石油天然气交易中心",
                "标题": "非洲渐成LNG供应新主力",
                "文章内容": "随着全球LNG需求持续增长，非洲正逐渐成为LNG供应的新主力。尼日利亚、莫桑比克、坦桑尼亚等非洲国家拥有丰富的天然气资源，正在大力发展LNG出口项目。分析师预计，未来5年非洲LNG产能将显著增长，为全球LNG市场供应多元化做出重要贡献。中国企业也积极参与非洲LNG项目开发。",
                "链接": "https://www.shpgx.com/html/xyzx/20250528/7840.html",
                "基础信息标签": "['行业资讯']",
                "地域标签": "['国际']",
                "能源品种标签": ["液化天然气(LNG)", "天然气"],
                "业务领域/主题标签": "['LNG出口', '供应格局']",
                "受益主体标签": "['非洲国家', 'LNG生产商']",
                "关键措施/政策标签": "['资源开发', '国际合作']",
                "重要性/影响力标签": "['国际级']",
                "规范化地域标签": ["非洲", "尼日利亚", "莫桑比克", "坦桑尼亚", "国际"]
            }
        ]
        
        # 合并v1和v2数据
        all_articles = v1_articles + v2_articles
        
        print(f"✅ 成功加载完整数据: v1版本{len(v1_articles)}篇 + v2版本{len(v2_articles)}篇 = 总计{len(all_articles)}篇")
        return all_articles
        
    except Exception as e:
        print(f"❌ 加载文章数据失败: {e}")
        return []

def parse_tag_string(tag_str: str) -> List[str]:
    """解析标签字符串，支持多种格式"""
    if not tag_str:
        return []
    
    # 如果已经是列表，直接返回
    if isinstance(tag_str, list):
        return tag_str
    
    # 处理字符串格式的标签
    tag_str = str(tag_str).strip()
    if not tag_str or tag_str in ['[]', '[""]', "['']"]:
        return []
    
    # 尝试解析JSON格式
    try:
        import ast
        parsed = ast.literal_eval(tag_str)
        if isinstance(parsed, list):
            return [str(tag).strip() for tag in parsed if tag and str(tag).strip()]
    except:
        pass
    
    # 简单分割处理
    if ',' in tag_str:
        return [tag.strip().strip("'\"") for tag in tag_str.split(',') if tag.strip()]
    
    return [tag_str.strip().strip("'\"")]

def convert_article_format(article: Dict[str, Any]) -> Dict[str, Any]:
    """将JSON格式的文章转换为数据库格式"""
    
    # 解析各种标签
    basic_info_tags = parse_tag_string(article.get('基础信息标签', ''))
    region_tags = parse_tag_string(article.get('规范化地域标签', []))
    energy_type_tags = article.get('能源品种标签', [])
    business_field_tags = parse_tag_string(article.get('业务领域/主题标签', ''))
    beneficiary_tags = parse_tag_string(article.get('受益主体标签', ''))
    policy_measure_tags = parse_tag_string(article.get('关键措施/政策标签', ''))
    importance_tags = parse_tag_string(article.get('重要性/影响力标签', ''))
    
    # 确保能源类型标签是列表格式
    if isinstance(energy_type_tags, str):
        energy_type_tags = parse_tag_string(energy_type_tags)
    
    return {
        "标题": article.get('标题', ''),
        "文章内容": article.get('文章内容', ''),
        "发布日期": article.get('发布日期', ''),
        "发布时间": article.get('发布时间', ''),
        "来源机构": article.get('来源机构', ''),
        "链接": article.get('链接', ''),
        "文档类型": article.get('文档类型', ''),
        
        # 标签字段
        "basic_info_tags": basic_info_tags,
        "region_tags": region_tags,
        "energy_type_tags": energy_type_tags,
        "business_field_tags": business_field_tags,
        "beneficiary_tags": beneficiary_tags,
        "policy_measure_tags": policy_measure_tags,
        "importance_tags": importance_tags,
        
        # 元数据
        "版本": "v3",
        "导入时间": datetime.now().isoformat(),
        "数据来源": "信息发布文章与标签_规范化.json"
    }

async def clear_existing_data():
    """清理现有数据"""
    print("🧹 清理现有数据...")
    
    db = await get_database()
    
    # 删除现有文章
    result = await db.content.delete_many({})
    print(f"   已删除 {result.deleted_count} 篇文章")
    
    # 删除现有用户标签（保留用户基础信息）
    await db.user_tags.delete_many({})
    print("   已清理用户标签数据")

async def import_v3_articles():
    """导入v3版本文章"""
    print("📚 导入v3版本文章数据...")
    
    # 加载完整文章数据
    articles_data = await load_complete_articles_data()
    if not articles_data:
        print("❌ 无法加载文章数据")
        return 0
    
    db = await get_database()
    
    # 转换并导入文章
    converted_articles = []
    for article in articles_data:
        converted_article = convert_article_format(article)
        converted_articles.append(converted_article)
    
    if converted_articles:
        await db.content.insert_many(converted_articles)
        print(f"   v3版本导入完成: {len(converted_articles)} 篇")
    
    return len(converted_articles)

async def analyze_data_distribution():
    """分析数据分布"""
    print("📊 分析数据分布...")
    
    db = await get_database()
    
    # 统计文章数量
    total_count = await db.content.count_documents({})
    v3_count = await db.content.count_documents({"版本": "v3"})
    
    print(f"   总文章数: {total_count} 篇")
    print(f"   v3版本: {v3_count} 篇")
    
    # 按基础信息标签统计
    pipeline = [
        {"$unwind": "$basic_info_tags"},
        {"$group": {"_id": "$basic_info_tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    basic_info_stats = await db.content.aggregate(pipeline).to_list(length=10)
    
    print("\n📈 按基础信息标签统计:")
    for item in basic_info_stats:
        print(f"   {item['_id']}: {item['count']} 篇")
    
    # 能源类型分布
    energy_pipeline = [
        {"$unwind": "$energy_type_tags"},
        {"$group": {"_id": "$energy_type_tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    energy_stats = await db.content.aggregate(energy_pipeline).to_list(length=15)
    
    print("\n💡 能源类型分布:")
    for item in energy_stats:
        print(f"   {item['_id']}: {item['count']} 篇")

async def create_demo_users():
    """创建演示用户"""
    print("👥 创建演示用户...")
    
    db = await get_database()
    
    # 清理现有演示用户
    await db.users.delete_many({"demo_user_id": {"$exists": True}})
    await db.user_tags.delete_many({"demo_user_id": {"$exists": True}})
    
    # 演示用户配置
    demo_users = [
        {
            "demo_user_id": "user001",
            "username": "张工程师",
            "email": "zhang@shanghai.com",
            "register_city": "上海",
            "description": "天然气市场分析师 - 关注天然气价格与政策",
            "energy_types": ["天然气"]
        },
        {
            "demo_user_id": "user002",
            "username": "李经理", 
            "email": "li@beijing.com",
            "register_city": "北京",
            "description": "石油贸易专家 - 原油进口与价格分析",
            "energy_types": ["原油"]
        },
        {
            "demo_user_id": "user003",
            "username": "王主任",
            "email": "wang@shenzhen.com",
            "register_city": "深圳", 
            "description": "LNG项目经理 - 液化天然气接收站运营",
            "energy_types": ["液化天然气(LNG)"]
        },
        {
            "demo_user_id": "user004",
            "username": "陈总监",
            "email": "chen@guangzhou.com",
            "register_city": "广州",
            "description": "管道天然气运营专家 - 天然气管网建设", 
            "energy_types": ["管道天然气(PNG)"]
        },
        {
            "demo_user_id": "user005",
            "username": "刘研究员",
            "email": "liu@chengdu.com",
            "register_city": "成都",
            "description": "电力系统研究员 - 可再生能源发电",
            "energy_types": ["电力"]
        }
    ]
    
    # 导入演示用户
    for user_data in demo_users:
        # 创建用户基础信息
        user_doc = {
            "demo_user_id": user_data["demo_user_id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "register_city": user_data["register_city"],
            "description": user_data["description"],
            "created_at": datetime.now().isoformat(),
            "version": "v3"
        }
        
        await db.users.insert_one(user_doc)
        
        # 创建用户标签
        user_tags = []
        
        # 添加城市标签
        user_tags.append({
            "demo_user_id": user_data["demo_user_id"],
            "tag_name": user_data["register_city"],
            "tag_category": "city",
            "tag_source": "preset",
            "weight": 2.5,
            "created_at": datetime.now().isoformat()
        })
        
        # 添加能源类型标签
        for energy_type in user_data["energy_types"]:
            user_tags.append({
                "demo_user_id": user_data["demo_user_id"],
                "tag_name": energy_type,
                "tag_category": "energy_type", 
                "tag_source": "preset",
                "weight": 2.0,
                "created_at": datetime.now().isoformat()
            })
        
        if user_tags:
            await db.user_tags.insert_many(user_tags)
    
    print(f"   创建了 {len(demo_users)} 个演示用户")

async def main():
    """主函数"""
    print("=" * 50)
    print("🚀 能源信息服务系统 - v3版本数据导入")
    print("   统一数据管理，简化维护流程")
    print("=" * 50)
    
    try:
        # 连接数据库
        await connect_to_mongo()
        
        # 1. 清理现有数据
        await clear_existing_data()
        
        # 2. 导入v3版本文章
        article_count = await import_v3_articles()
        
        # 3. 创建演示用户
        await create_demo_users()
        
        # 4. 分析数据分布
        await analyze_data_distribution()
        
        print("\n" + "=" * 50)
        print("✅ v3版本数据导入完成！")
        print(f"📊 导入统计:")
        print(f"   文章总数: {article_count} 篇")
        print(f"   数据版本: v3 (统一版本)")
        print(f"   演示用户: 5 个")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 导入过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 