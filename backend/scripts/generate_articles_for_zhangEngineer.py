#!/usr/bin/env python3
"""
为张工程师生成匹配标签的测试文章
根据张工程师的标签：上海、上海市、华东地区、天然气
生成4篇不同类型的文章：行业资讯、政策法规、调价公告、交易公告
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from app.models.content import Content, ContentType
from datetime import datetime, timedelta
import json

async def generate_articles_for_zhang_engineer():
    """为张工程师生成4篇匹配标签的文章"""
    
    print("🎯 为张工程师生成匹配标签的文章")
    print("=" * 60)
    
    # 连接数据库
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.energy_info
    content_collection = db.content
    
    # 张工程师的标签配置
    zhang_tags = {
        "city": "上海",
        "province": "上海市", 
        "region": "华东地区",
        "energy_type": "天然气"
    }
    
    print(f"👤 张工程师标签: {zhang_tags}")
    
    # 定义4篇文章的配置
    articles_config = [
        {
            "type": "news",
            "title": f"上海天然气市场行情分析：华东地区供需平衡态势良好",
            "content": """
            据上海石油天然气交易中心最新数据显示，华东地区天然气市场呈现供需平衡的良好态势。本月上海天然气现货价格保持稳定，主要受以下因素影响：

            一、供应端分析
            1. 进口LNG到港量稳定，上海洋山港接收站运行正常
            2. 国产气源供应充足，西气东输管道气量保持高位
            3. 华东地区储气库存处于合理水平

            二、需求端分析  
            1. 工业用气需求平稳，化工企业开工率维持在80%以上
            2. 居民用气进入平峰期，消费量较上月下降15%
            3. 发电用气需求增加，燃气电厂利用小时数上升

            三、价格走势预测
            预计下月上海天然气价格将维持震荡走势，华东地区整体供需格局有利于价格稳定。建议相关企业合理安排采购计划，关注国际LNG价格变化。

            数据来源：上海石油天然气交易中心、华东天然气管网公司
            """,
            "source": "上海石油天然气交易中心",
            "basic_info_tags": ["行业资讯", "市场分析", "供需分析"],
            "region_tags": ["上海", "上海市", "华东地区"],
            "energy_type_tags": ["天然气", "液化天然气(LNG)"],
            "business_field_tags": ["销售贸易", "运输储存"],
            "importance_tags": ["市级", "重要"]
        },
        {
            "type": "policy", 
            "title": f"上海市发布天然气利用管理新政策：推进华东地区清洁能源发展",
            "content": """
            上海市发展和改革委员会今日发布《关于进一步规范天然气利用管理的实施意见》，旨在推进华东地区清洁能源发展，提高天然气利用效率。

            政策要点如下：

            一、优化天然气利用结构
            1. 优先保障居民生活和公共服务用气
            2. 支持工业企业"煤改气"项目，给予财政补贴
            3. 鼓励发展天然气分布式能源项目

            二、完善价格机制
            1. 建立天然气价格联动机制，与国际市场接轨
            2. 实施阶梯气价制度，促进节约用气
            3. 对清洁能源项目给予价格优惠政策

            三、加强基础设施建设
            1. 加快上海LNG接收站扩建工程
            2. 完善华东地区天然气管网互联互通
            3. 建设区域性天然气储备设施

            四、监管措施
            1. 建立天然气安全监管体系
            2. 强化市场准入管理
            3. 完善应急保供机制

            该政策自2024年1月1日起施行，有效期5年。预计将为华东地区天然气行业发展注入新动力。

            政策文件编号：沪发改能源〔2024〕001号
            """,
            "source": "上海市发展和改革委员会", 
            "basic_info_tags": ["政策法规", "政策解读"],
            "region_tags": ["上海", "上海市", "华东地区"],
            "energy_type_tags": ["天然气", "液化天然气(LNG)"],
            "business_field_tags": ["管网建设", "终端应用"],
            "policy_measure_tags": ["价格调整", "补贴政策", "准入管理"],
            "beneficiary_tags": ["生产企业", "终端用户"],
            "importance_tags": ["市级", "重要"]
        },
        {
            "type": "price",
            "title": f"上海天然气价格调整公告：华东地区统一执行新价格标准",
            "content": """
            上海燃气集团股份有限公司
            天然气销售价格调整公告

            各用气单位及广大用户：

            根据国家发展改革委《关于建立健全天然气价格机制的通知》和上海市相关规定，结合华东地区天然气市场供需状况，经市政府批准，决定对天然气销售价格进行调整。现公告如下：

            一、调整内容
            1. 居民用气价格：由3.20元/立方米调整为3.35元/立方米，上调0.15元/立方米
            2. 工业用气价格：由4.85元/立方米调整为4.95元/立方米，上调0.10元/立方米  
            3. 商业用气价格：由5.20元/立方米调整为5.35元/立方米，上调0.15元/立方米

            二、执行时间
            新价格自2024年2月1日起执行，华东地区其他城市参照执行。

            三、调价原因
            1. 国际LNG价格上涨，进口成本增加
            2. 上游气源价格调整，传导至终端销售
            3. 管网建设和安全运营成本上升

            四、配套措施
            1. 对低收入家庭继续实施燃气补贴政策
            2. 工业企业可申请分期缴费
            3. 加强价格监管，严禁乱收费

            如有疑问，请拨打客服电话：962777

            特此公告

            上海燃气集团股份有限公司
            2024年1月25日
            """,
            "source": "上海燃气集团",
            "basic_info_tags": ["调价公告", "价格信息", "价格动态"],
            "region_tags": ["上海", "上海市", "华东地区"],
            "energy_type_tags": ["天然气"],
            "business_field_tags": ["销售贸易", "终端应用"],
            "policy_measure_tags": ["价格调整"],
            "beneficiary_tags": ["终端用户", "生产企业"],
            "importance_tags": ["市级", "重要"]
        },
        {
            "type": "announcement",
            "title": f"上海石油天然气交易中心：华东地区天然气竞价交易公告",
            "content": """
            上海石油天然气交易中心
            华东地区天然气竞价交易公告
            交易公告编号：SHPGX-2024-001

            一、交易基本信息
            交易名称：华东地区天然气现货竞价交易
            交易时间：2024年2月15日 09:30-11:30
            交易地点：上海石油天然气交易中心（线上平台）
            交易标的：管道天然气现货

            二、资源信息
            气源：西气东输二线
            交割地点：上海天然气管网分输站
            交易气量：500万立方米
            气质标准：符合GB17820-2018标准
            交割周期：2024年2月16日-2月28日

            三、参与条件
            1. 具有天然气经营资质的企业
            2. 在上海石油天然气交易中心开户
            3. 缴纳履约保证金100万元
            4. 具备华东地区天然气接收能力

            四、交易规则
            1. 采用价格优先、时间优先原则
            2. 最小报价单位：0.01元/立方米
            3. 单笔最小交易量：10万立方米
            4. 价格上下限：±10%

            五、报名方式
            请于2024年2月10日前登录交易平台提交报名申请
            咨询电话：021-20658888
            技术支持：021-20658999

            六、结算安排
            采用T+1结算方式，通过上海清算所进行集中清算
            交易手续费：0.02元/立方米

            欢迎华东地区天然气产业链企业积极参与！

            上海石油天然气交易中心
            2024年2月5日
            """,
            "source": "上海石油天然气交易中心",
            "basic_info_tags": ["交易公告", "交易信息"],
            "region_tags": ["上海", "上海市", "华东地区"],
            "energy_type_tags": ["天然气", "管道天然气(PNG)"],
            "business_field_tags": ["销售贸易", "金融服务"],
            "beneficiary_tags": ["贸易商", "生产企业"],
            "importance_tags": ["市级", "重要"]
        }
    ]
    
    generated_articles = []
    
    for i, article_config in enumerate(articles_config):
        print(f"\n📄 生成第{i+1}篇文章: {article_config['title'][:30]}...")
        
        # 创建文章数据
        article_data = {
            "title": article_config["title"],
            "content": article_config["content"].strip(),
            "type": article_config["type"],
            "source": article_config["source"],
            "publish_time": (datetime.utcnow() - timedelta(days=i)).isoformat(),
            "link": f"https://example.com/articles/{i+1001}",
            "view_count": 100 + i * 50,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            
            # 标签配置（重点匹配张工程师的标签）
            "basic_info_tags": article_config["basic_info_tags"],
            "region_tags": article_config["region_tags"],
            "energy_type_tags": article_config["energy_type_tags"],
            "business_field_tags": article_config["business_field_tags"],
            "policy_measure_tags": article_config.get("policy_measure_tags", []),
            "beneficiary_tags": article_config.get("beneficiary_tags", []),
            "importance_tags": article_config["importance_tags"]
        }
        
        # 插入数据库
        try:
            result = await content_collection.insert_one(article_data)
            article_data["_id"] = str(result.inserted_id)
            generated_articles.append(article_data)
            
            print(f"   ✅ 文章插入成功，ID: {result.inserted_id}")
            print(f"   📋 类型: {article_config['type']}")
            print(f"   🏷️ 地区标签: {article_config['region_tags']}")
            print(f"   ⚡ 能源标签: {article_config['energy_type_tags']}")
            
        except Exception as e:
            print(f"   ❌ 文章插入失败: {str(e)}")
    
    print(f"\n🎉 文章生成完成！")
    print(f"📊 总计生成: {len(generated_articles)}篇文章")
    print(f"🎯 标签匹配度: 100% (专为张工程师定制)")
    
    # 验证生成的文章
    print(f"\n🔍 验证生成的文章:")
    for article in generated_articles:
        type_name = {
            "news": "行业资讯",
            "policy": "政策法规", 
            "price": "调价公告",
            "announcement": "交易公告"
        }.get(article["type"], article["type"])
        
        print(f"   📄 {type_name}: {article['title'][:40]}...")
        print(f"      🏷️ 匹配标签: 上海✓ 华东地区✓ 天然气✓")
    
    # 关闭数据库连接
    client.close()
    
    return generated_articles

if __name__ == "__main__":
    asyncio.run(generate_articles_for_zhang_engineer()) 