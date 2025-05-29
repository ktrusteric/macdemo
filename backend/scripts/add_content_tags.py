#!/usr/bin/env python3
"""
为现有内容添加标签脚本
基于内容标题的关键词匹配来自动生成标签
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings

class ContentTagger:
    def __init__(self):
        self.client = None
        self.db = None
        
        # 定义标签映射规则
        self.tag_rules = {
            'region_tags': {
                '华东': ['上海', '浙江', '江苏', '山东', '福建', '安徽', '江西'],
                '华北': ['北京', '天津', '河北', '山西', '内蒙古'],
                '华南': ['广东', '广西', '海南', '深圳', '广州'],
                '华中': ['湖北', '湖南', '河南'],
                '西南': ['四川', '重庆', '贵州', '云南', '西藏', '成都'],
                '西北': ['陕西', '甘肃', '青海', '宁夏', '新疆', '西安'],
                '东北': ['辽宁', '吉林', '黑龙江', '大连']
            },
            'energy_type_tags': {
                '天然气': ['天然气', 'LNG', '液化天然气', '管道气', '压缩天然气', 'CNG'],
                '石油': ['原油', '石油', '汽油', '柴油', '燃料油', '重油'],
                '煤炭': ['煤炭', '煤', '焦炭', '焦煤', '动力煤'],
                '电力': ['电力', '发电', '电网', '用电', '供电'],
                '新能源': ['太阳能', '风能', '风电', '光伏', '新能源', '清洁能源'],
                '生物质': ['生物质', '生物柴油', '乙醇', '生物燃料'],
                '氢能': ['氢能', '氢气', '燃料电池']
            },
            'business_field_tags': {
                '交易': ['交易', '竞价', '挂牌', '拍卖', '买卖'],
                '储运': ['储存', '运输', '管道', '储气', '储罐', '物流'],
                '生产': ['生产', '开采', '勘探', '钻井', '炼化'],
                '销售': ['销售', '零售', '批发', '供应'],
                '投资': ['投资', '融资', '并购', 'IPO', '上市'],
                '政策': ['政策', '法规', '标准', '规范', '监管']
            },
            'importance_tags': {
                '高': ['重大', '突破', '创新', '首次', '最大', '最高', '纪录'],
                '中': ['重要', '关键', '主要', '核心'],
                '低': ['一般', '常规', '普通']
            }
        }
    
    async def connect(self):
        """连接数据库"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client[settings.DATABASE_NAME]
            await self.client.admin.command('ping')
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise

    async def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()
            print("📡 数据库连接已关闭")

    def extract_tags_from_title(self, title: str) -> dict:
        """从标题中提取标签"""
        tags = {
            'basic_info_tags': [],
            'region_tags': [],
            'energy_type_tags': [],
            'business_field_tags': [],
            'beneficiary_tags': [],
            'policy_measure_tags': [],
            'importance_tags': []
        }
        
        title_lower = title.lower()
        
        # 地区标签
        for region, keywords in self.tag_rules['region_tags'].items():
            for keyword in keywords:
                if keyword in title:
                    tags['region_tags'].append(region)
                    break
        
        # 能源类型标签
        for energy_type, keywords in self.tag_rules['energy_type_tags'].items():
            for keyword in keywords:
                if keyword in title:
                    tags['energy_type_tags'].append(energy_type)
                    break
        
        # 业务领域标签
        for business, keywords in self.tag_rules['business_field_tags'].items():
            for keyword in keywords:
                if keyword in title:
                    tags['business_field_tags'].append(business)
                    break
        
        # 重要性标签
        for importance, keywords in self.tag_rules['importance_tags'].items():
            for keyword in keywords:
                if keyword in title:
                    tags['importance_tags'].append(importance)
                    break
        
        # 基础信息标签（基于业务类型推断）
        if tags['business_field_tags']:
            tags['basic_info_tags'] = ['行业动态']
        
        # 政策措施标签
        if any(keyword in title for keyword in ['公告', '通知', '规定', '办法', '政策']):
            tags['policy_measure_tags'].append('政策发布')
        
        # 受益主体标签
        if any(keyword in title for keyword in ['企业', '公司', '集团']):
            tags['beneficiary_tags'].append('企业')
        
        return tags

    async def add_tags_to_content(self):
        """为所有内容添加标签"""
        try:
            print("🏷️ 开始为内容添加标签...")
            
            # 获取所有内容
            content_collection = self.db.content
            cursor = content_collection.find({})
            contents = await cursor.to_list(length=None)
            
            print(f"📊 找到 {len(contents)} 条内容")
            
            updated_count = 0
            
            for content in contents:
                title = content.get('title', '')
                if not title:
                    continue
                
                # 提取标签
                extracted_tags = self.extract_tags_from_title(title)
                
                # 检查是否已有标签
                has_tags = any(content.get(tag_type, []) for tag_type in extracted_tags.keys())
                
                if not has_tags:  # 只为没有标签的内容添加标签
                    # 更新内容
                    update_data = {
                        **extracted_tags,
                        'updated_at': datetime.utcnow()
                    }
                    
                    await content_collection.update_one(
                        {'_id': content['_id']},
                        {'$set': update_data}
                    )
                    
                    updated_count += 1
                    
                    # 显示处理进度
                    if updated_count % 10 == 0:
                        print(f"⏳ 已处理 {updated_count} 条内容...")
                    
                    # 显示标签示例
                    if updated_count <= 3:
                        print(f"📝 [{updated_count}] {title[:40]}...")
                        for tag_type, tag_list in extracted_tags.items():
                            if tag_list:
                                print(f"   {tag_type}: {tag_list}")
            
            print(f"✅ 成功为 {updated_count} 条内容添加了标签")
            
        except Exception as e:
            print(f"❌ 添加标签失败: {e}")
            raise

async def main():
    """主函数"""
    tagger = ContentTagger()
    
    try:
        await tagger.connect()
        await tagger.add_tags_to_content()
    except Exception as e:
        print(f"❌ 脚本执行失败: {e}")
        return 1
    finally:
        await tagger.close()
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 