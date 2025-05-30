#!/usr/bin/env python3
"""
添加缺失的交易公告和调价公告文章
解决Dashboard页面咨询概览、交易公告、调价公告不显示的问题
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.core.config import settings

async def add_missing_announcements():
    """添加缺失的公告类型文章"""
    client = None
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        
        # 创建交易公告文章
        trade_announcements = [
            {
                'title': '关于开展安平管道天然气竞价交易的公告',
                'content': '''
                交易中心办〔2025〕第54号
                
                为进一步响应国家天然气市场化改革要求，服务行业健康持续稳定发展，上海石油天然气交易中心拟定于2025年5月26日通过上海交易中心交易平台开展6月份安平管道天然气竞价交易。
                
                一、交易时间
                2025年5月26日 10:00-11:00
                
                二、产品介绍
                1.产品名称：天然气
                2.卖方：于报名审核通过后进行通知
                3.交易量：2000万立方米
                4.交收期：线上成交后第5个自然日8:00起至2025年6月30日8:00
                5.交收地：国家管网安平枢纽点
                6.交收方式：自主交收
                
                三、交易参数
                - 竞拍底价：2.45元/方（含税价格）
                - 最小加价幅度：0.001元/方
                - 倒计时规则：5分钟倒计时
                ''',
                'type': 'news',
                'source': '上海石油天然气交易中心',
                'publish_time': (datetime.now() - timedelta(hours=3)).isoformat(),
                'link': 'https://www.shpgx.com/html/jygg/20250520/7825.html',
                'basic_info_tags': ['交易公告'],
                'energy_type_tags': ['管道天然气(PNG)', '天然气'],
                'region_tags': ['全国'],
                'business_field_tags': ['交易市场'],
                'beneficiary_tags': ['能源企业'],
                'policy_measure_tags': ['市场交易'],
                'importance_tags': ['国家级'],
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'title': '关于开展华港燃气集团有限公司重烃竞价交易的公告',
                'content': '''
                本着公平、公正、公开、市场化定价的原则，华港燃气集团有限公司在上海石油天然气交易中心平台开展重烃竞价交易。
                
                一、交易时间
                5月20日14:30-15:00
                
                二、产品信息
                1.产品名称：液厂重烃(C5+)
                2.卖方：华港燃气集团有限公司
                3.交易量：约100吨
                4.交收期：5月20日-6月30日
                5.交收地：华港任丘液化天然气工厂
                6.交收方式：槽车运输方式自提
                
                三、交易参数
                - 最小加价幅度：5元/吨
                - 最大加价幅度：100元/吨
                - 倒计时规则：5分钟倒计时
                ''',
                'type': 'news',
                'source': '华港燃气集团有限公司',
                'publish_time': (datetime.now() - timedelta(hours=2)).isoformat(),
                'link': 'https://www.shpgx.com/html/jygg/20250520/7825.html',
                'basic_info_tags': ['交易公告'],
                'energy_type_tags': ['液化天然气(LNG)', '液化石油气(LPG)'],
                'region_tags': ['河北', '全国'],
                'business_field_tags': ['交易市场'],
                'beneficiary_tags': ['能源企业'],
                'policy_measure_tags': ['市场交易'],
                'importance_tags': ['行业级'],
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'title': '关于开展线上管道气天然气竞价交易的公告',
                'content': '''
                交易中心办〔2025〕第43号
                
                为进一步响应国家天然气市场化改革要求，服务行业健康持续稳定发展，上海石油天然气交易中心拟定于2025年5月7日通过上海交易中心交易平台开展5月份线上管道天然气竞价交易。
                
                一、交易时间
                2025年5月7日10:00-11:00
                
                二、产品介绍
                1.产品名称：天然气
                2.卖方：于报名审核通过后进行通知
                3.交易量：1550万立方米
                4.交收期：线上成交后第5个自然日8:00起至2025年5月31日8:00
                5.交收地：国家管网安平枢纽点
                6.交收方式：自主交收
                
                三、交易参数
                - 竞拍底价：2.36元/方（含税价格）
                - 最小加价幅度：0.01元/方
                - 倒计时规则：5分钟倒计时
                ''',
                'type': 'news',
                'source': '上海石油天然气交易中心',
                'publish_time': (datetime.now() - timedelta(hours=1)).isoformat(),
                'link': 'https://www.shpgx.com/html/jygg/20250520/7825.html',
                'basic_info_tags': ['交易公告'],
                'energy_type_tags': ['管道天然气(PNG)', '天然气'],
                'region_tags': ['全国'],
                'business_field_tags': ['交易市场'],
                'beneficiary_tags': ['能源企业'],
                'policy_measure_tags': ['市场交易'],
                'importance_tags': ['国家级'],
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        ]
        
        # 创建调价公告文章
        price_announcements = [
            {
                'title': '中国石油浙江分公司液化天然气(LNG)销售价格调整公告',
                'content': '''
                根据市场供需情况和成本变化，现对液化天然气销售价格进行调整：
                
                一、调整时间
                自2025年5月30日12:00起执行
                
                二、价格调整
                1. 工业用户：上调200元/吨
                2. 城市燃气：上调150元/吨
                3. 化工用户：上调180元/吨
                
                三、备注
                浙江分公司保留调整销售价格及政策的权利，在未发布新的调价公告之前，
                地区内价格及销售政策保持不变。
                ''',
                'type': 'news',
                'source': '中国石油浙江分公司',
                'publish_time': (datetime.now() - timedelta(minutes=30)).isoformat(),
                'link': 'https://www.shpgx.com/html/hyzq/20250507/7783.html',
                'basic_info_tags': ['调价公告'],
                'energy_type_tags': ['液化天然气(LNG)'],
                'region_tags': ['浙江', '华东地区'],
                'business_field_tags': ['价格调整', '市场动态'],
                'beneficiary_tags': ['工业用户', '城市燃气', '化工企业'],
                'policy_measure_tags': ['价格政策'],
                'importance_tags': ['省级'],
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'title': '华润燃气上海地区天然气门站价格调整通知',
                'content': '''
                根据国家发改委天然气门站价格政策，结合市场情况，现对上海地区
                天然气门站价格进行调整：
                
                一、执行时间
                2025年5月30日零时起执行
                
                二、价格调整内容
                1. 居民用气：维持现价不变
                2. 非居民用气：上调0.05元/立方米
                3. 工业用气：上调0.08元/立方米
                
                三、调整原因
                受国际天然气价格上涨和运输成本增加影响。
                ''',
                'type': 'news',
                'source': '华润燃气上海公司',
                'publish_time': (datetime.now() - timedelta(minutes=15)).isoformat(),
                'link': 'https://www.shpgx.com/html/hyzq/20250510/7795.html',
                'basic_info_tags': ['调价公告'],
                'energy_type_tags': ['天然气'],
                'region_tags': ['上海', '华东地区'],
                'business_field_tags': ['价格调整', '门站价格'],
                'beneficiary_tags': ['居民用户', '工业用户'],
                'policy_measure_tags': ['价格政策'],
                'importance_tags': ['市级'],
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        ]
        
        # 插入交易公告
        if trade_announcements:
            await db.content.insert_many(trade_announcements)
            print(f"✅ 成功添加 {len(trade_announcements)} 篇交易公告")
        
        # 插入调价公告
        if price_announcements:
            await db.content.insert_many(price_announcements)
            print(f"✅ 成功添加 {len(price_announcements)} 篇调价公告")
        
        # 统计验证
        trade_count = await db.content.count_documents({'basic_info_tags': '交易公告'})
        price_count = await db.content.count_documents({'basic_info_tags': '调价公告'})
        total_count = await db.content.count_documents({})
        
        print(f"\n📊 数据库统计:")
        print(f"   交易公告: {trade_count} 篇")
        print(f"   调价公告: {price_count} 篇")
        print(f"   总文章数: {total_count} 篇")
        
    except Exception as e:
        print(f"❌ 添加公告失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if client:
            await client.close()

if __name__ == "__main__":
    asyncio.run(add_missing_announcements()) 