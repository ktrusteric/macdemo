#!/usr/bin/env python3
"""
导入v2版本内容数据到数据库
基于上海石油天然气交易中心网站最新内容
"""

import asyncio
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.content import ContentType

# v2版本数据
V2_CONTENT_DATA = [
    {
        "版本": "v2",
        "标题": "密集投产潮下利用率不足50%，LNG接收站市场竞争加剧，如何保障效益",
        "content": "随着全球LNG贸易量持续增长，中国LNG接收站建设进入密集投产期。然而，受市场供需变化影响，部分接收站利用率不足50%，面临严峻的市场竞争压力。行业专家指出，接收站运营商需要通过技术升级、服务优化、商业模式创新等方式提升竞争力，确保投资效益。未来LNG接收站发展需要统筹规划，避免重复建设，提高整体利用效率。",
        "type": "news",
        "source": "上海石油天然气交易中心",
        "publish_time": "2025-05-30",
        "link": "https://www.shpgx.com/html/xyzx/20250530/7850.html",
        "basic_info_tags": ["行业资讯"],
        "energy_type_tags": ["液化天然气(LNG)"],
        "region_tags": ["中国", "全国"],
        "business_field_tags": ["接收站运营", "市场竞争", "投资效益"],
        "beneficiary_tags": ["LNG运营商", "能源企业"],
        "policy_measure_tags": ["技术升级", "商业模式创新"],
        "importance_tags": ["行业级"]
    },
    {
        "版本": "v2",
        "标题": "新奥股份重大资产重组获股东大会超99.9%高票通过，天然气产业链一体化战略取得关键进展",
        "content": "新奥股份重大资产重组方案获得股东大会超99.9%的高票通过，标志着公司天然气产业链一体化战略取得关键性进展。此次重组将进一步完善新奥在天然气全产业链的布局，提升公司在LNG贸易、终端销售等关键环节的竞争优势。市场分析认为，这一举措将有助于新奥股份实现规模化发展，提高抗风险能力。",
        "type": "news",
        "source": "上海石油天然气交易中心",
        "publish_time": "2025-05-30",
        "link": "https://www.shpgx.com/html/xyzx/20250530/7849.html",
        "basic_info_tags": ["行业资讯"],
        "energy_type_tags": ["天然气", "液化天然气(LNG)"],
        "region_tags": ["中国", "全国"],
        "business_field_tags": ["资产重组", "产业链一体化", "LNG贸易"],
        "beneficiary_tags": ["新奥股份", "上市公司", "能源企业"],
        "policy_measure_tags": ["资产重组", "产业链整合"],
        "importance_tags": ["行业级"]
    },
    {
        "版本": "v2",
        "标题": "中国石油发布3000亿参数昆仑大模型",
        "content": "中国石油正式发布3000亿参数规模的昆仑大模型，这是石油天然气行业首个千亿级参数大模型。该模型将在勘探开发、炼化生产、销售服务等多个业务场景中应用，通过AI技术提升作业效率和决策水平。专家表示，大模型技术的应用将推动传统能源行业数字化转型，为行业发展注入新动能。",
        "type": "news",
        "source": "上海石油天然气交易中心",
        "publish_time": "2025-05-30",
        "link": "https://www.shpgx.com/html/xyzx/20250530/7848.html",
        "basic_info_tags": ["行业资讯"],
        "energy_type_tags": ["石油", "天然气"],
        "region_tags": ["中国", "全国"],
        "business_field_tags": ["人工智能", "数字化转型", "技术创新"],
        "beneficiary_tags": ["中国石油", "能源企业", "技术公司"],
        "policy_measure_tags": ["技术创新", "AI应用", "数字化升级"],
        "importance_tags": ["行业级", "技术突破"]
    },
    {
        "版本": "v2",
        "标题": "5月19日-25日中国LNG综合进口到岸价格指数为131.78点",
        "content": "5月19日-25日当周，中国LNG综合进口到岸价格指数为131.78点，价格相对稳定。随着夏季用气需求逐步减少，LNG市场供需趋于平衡。业内分析认为，二季度LNG价格将保持相对平稳，但需关注国际市场供应端变化和下半年冬季备货需求。",
        "type": "news",
        "source": "上海石油天然气交易中心",
        "publish_time": "2025-05-29",
        "link": "https://www.shpgx.com/html/xyzx/20250529/7845.html",
        "basic_info_tags": ["行业资讯"],
        "energy_type_tags": ["液化天然气(LNG)"],
        "region_tags": ["中国", "全国"],
        "business_field_tags": ["价格指数", "进口贸易", "市场分析"],
        "beneficiary_tags": ["LNG贸易商", "城市燃气公司", "能源企业"],
        "policy_measure_tags": ["价格监测", "供需调节"],
        "importance_tags": ["市场级"]
    },
    {
        "版本": "v2",
        "标题": "大港油田储气库群加快扩容 为京津冀冬季保供蓄能",
        "content": "大港油田储气库群正在加快扩容建设，为即将到来的冬季天然气保供做好准备。作为华北地区重要的天然气储备基地，大港储气库群承担着京津冀地区冬季调峰保供的重要任务。预计新增储气能力将有效缓解冬季用气紧张局面，为区域能源安全提供坚实保障。",
        "type": "news",
        "source": "上海石油天然气交易中心",
        "publish_time": "2025-05-29",
        "link": "https://www.shpgx.com/html/xyzx/20250529/7844.html",
        "basic_info_tags": ["行业资讯"],
        "energy_type_tags": ["天然气"],
        "region_tags": ["北京", "天津", "河北", "华北地区", "京津冀"],
        "business_field_tags": ["储气库", "冬季保供", "调峰储备", "基础设施"],
        "beneficiary_tags": ["京津冀用户", "城市燃气公司", "能源企业"],
        "policy_measure_tags": ["储气库建设", "保供措施", "基础设施投资"],
        "importance_tags": ["区域级", "民生保障"]
    },
    {
        "版本": "v2",
        "标题": "非洲渐成LNG供应新主力",
        "content": "随着全球LNG需求持续增长，非洲正逐渐成为LNG供应的新主力。尼日利亚、莫桑比克、坦桑尼亚等非洲国家拥有丰富的天然气资源，正在大力发展LNG出口项目。分析师预计，未来5年非洲LNG产能将显著增长，为全球LNG市场供应多元化做出重要贡献。中国企业也积极参与非洲LNG项目开发。",
        "type": "news",
        "source": "上海石油天然气交易中心",
        "publish_time": "2025-05-28",
        "link": "https://www.shpgx.com/html/xyzx/20250528/7840.html",
        "basic_info_tags": ["行业资讯"],
        "energy_type_tags": ["液化天然气(LNG)", "天然气"],
        "region_tags": ["非洲", "尼日利亚", "莫桑比克", "坦桑尼亚", "国际"],
        "business_field_tags": ["LNG出口", "供应格局", "资源开发", "国际贸易"],
        "beneficiary_tags": ["非洲国家", "LNG生产商", "中国企业"],
        "policy_measure_tags": ["资源开发", "国际合作", "项目投资"],
        "importance_tags": ["国际级"]
    },
    # 政策法规内容
    {
        "版本": "v2",
        "标题": "国家能源局关于促进能源领域民营经济发展若干举措的通知",
        "content": "国家能源局关于促进能源领域民营经济发展若干举措的通知。为深入贯彻落实习近平总书记在民营企业座谈会上的重要讲话精神，促进能源领域民营经济加快发展，引导民营经济在推进能源绿色低碳转型和建设新型能源体系中做大做优做强。支持民营企业参股投资核电项目，投资建设水电、油气储备设施、液化天然气接收站等基础设施项目。",
        "type": "policy",
        "source": "国家能源局",
        "publish_time": "2025-04-30",
        "link": "https://www.shpgx.com/html/zcsd/20250430/7765.html",
        "basic_info_tags": ["政策法规"],
        "energy_type_tags": ["液化天然气(LNG)", "天然气", "电力", "核电"],
        "region_tags": ["全国"],
        "business_field_tags": ["民营经济发展", "市场准入优化", "投资支持", "科技创新"],
        "beneficiary_tags": ["民营企业"],
        "policy_measure_tags": ["投资支持", "市场准入措施", "科技创新"],
        "importance_tags": ["国家级", "重要政策"]
    },
    {
        "版本": "v2",
        "标题": "上海市发展和改革委员会：关于核定本市管道天然气配气价格及上海天然气管网有限公司管输价格的通知",
        "content": "按照国家发展改革委相关规定，根据成本监审情况，结合本市实际，现就本市管道天然气配气价格及上海天然气管网有限公司管输价格等有关事项通知。本市管道天然气综合配气价格核定为0.41元/立方米（含税）。管输价格核定为0.12元/立方米（含税）。",
        "type": "policy",
        "source": "上海市发展和改革委员会",
        "publish_time": "2025-04-28",
        "link": "https://www.shpgx.com/html/zcsd/20250428/7757.html",
        "basic_info_tags": ["政策法规"],
        "energy_type_tags": ["管道天然气(PNG)", "天然气"],
        "region_tags": ["上海", "上海市", "华东地区"],
        "business_field_tags": ["价格政策", "配气价格", "管输价格", "成本监审"],
        "beneficiary_tags": ["管道燃气企业", "天然气用户"],
        "policy_measure_tags": ["价格核定", "成本监审", "政府定价"],
        "importance_tags": ["省级", "价格政策"]
    }
]

async def import_v2_content():
    """导入v2版本内容数据"""
    client = None
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        collection = db.content
        
        print("🚀 开始导入v2版本内容数据...")
        
        imported_count = 0
        for article_data in V2_CONTENT_DATA:
            # 转换为数据库格式
            db_article = {
                "title": article_data["标题"],
                "content": article_data["content"],
                "type": article_data["type"],
                "source": article_data["source"],
                "publish_time": article_data["publish_time"],
                "link": article_data["link"],
                "basic_info_tags": article_data["basic_info_tags"],
                "energy_type_tags": article_data["energy_type_tags"],
                "region_tags": article_data["region_tags"],
                "business_field_tags": article_data["business_field_tags"],
                "beneficiary_tags": article_data["beneficiary_tags"],
                "policy_measure_tags": article_data["policy_measure_tags"],
                "importance_tags": article_data["importance_tags"],
                "version": "v2",  # 标记为v2版本
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # 检查是否已存在相同标题的文章
            existing = await collection.find_one({"title": db_article["title"]})
            if not existing:
                await collection.insert_one(db_article)
                imported_count += 1
                print(f"✅ 导入文章: {db_article['title'][:50]}...")
            else:
                print(f"⚠️  文章已存在，跳过: {db_article['title'][:50]}...")
        
        # 统计验证
        total_v1 = await collection.count_documents({"version": {"$ne": "v2"}})
        total_v2 = await collection.count_documents({"version": "v2"})
        total_all = await collection.count_documents({})
        
        print(f"\n📊 导入完成统计:")
        print(f"   本次导入: {imported_count} 篇")
        print(f"   v1版本文章: {total_v1} 篇")
        print(f"   v2版本文章: {total_v2} 篇")
        print(f"   总文章数: {total_all} 篇")
        
        # 按类型统计v2版本
        news_count = await collection.count_documents({"version": "v2", "basic_info_tags": "行业资讯"})
        policy_count = await collection.count_documents({"version": "v2", "basic_info_tags": "政策法规"})
        
        print(f"\n📈 v2版本分类统计:")
        print(f"   行业资讯: {news_count} 篇")
        print(f"   政策法规: {policy_count} 篇")
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    asyncio.run(import_v2_content()) 