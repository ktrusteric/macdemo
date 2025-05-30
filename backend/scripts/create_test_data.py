import json
import random
from datetime import datetime, timedelta

# 简化的7大类标签池 - 每类只保留核心标签
SIMPLIFIED_TAGS = {
    'basic_info': ['政策法规', '行业资讯', '交易公告', '调价公告'],
    'region': ['华东地区', '华南地区', '华北地区', '全国', '上海', '北京', '广州'],
    'energy_type': ['天然气', '电力', '原油', '煤炭', '可再生能源'],
    'business_field': ['市场动态', '价格变化', '政策解读', '国际合作'],
    'beneficiary': ['能源企业', '政府机构', '民营企业'],
    'policy_measure': ['市场监管', '投资支持', '技术合作'],
    'importance': ['国家级', '重要政策', '权威发布', '常规公告']
}

# 文章模板
ARTICLE_TEMPLATES = [
    {
        "title": "国家能源局发布2025年能源发展指导意见",
        "type": "政策法规",
        "content": "为深入贯彻落实党中央、国务院关于能源工作的重大决策部署，国家能源局制定了《2025年能源工作指导意见》...",
        "source": "国家能源局",
        "preferred_tags": {
            'basic_info': ['政策法规'],
            'region': ['全国'],
            'energy_type': ['可再生能源', '电力'],
            'business_field': ['政策解读'],
            'beneficiary': ['政府机构', '能源企业'],
            'policy_measure': ['投资支持'],
            'importance': ['国家级', '重要政策']
        }
    },
    {
        "title": "上海天然气价格调整通知",
        "type": "调价公告", 
        "content": "根据国家发改委相关规定，结合本市天然气成本变化情况，决定调整本市天然气销售价格...",
        "source": "上海市发改委",
        "preferred_tags": {
            'basic_info': ['调价公告'],
            'region': ['华东地区', '上海'],
            'energy_type': ['天然气'],
            'business_field': ['价格变化'],
            'beneficiary': ['能源企业'],
            'policy_measure': ['市场监管'],
            'importance': ['重要政策']
        }
    },
    {
        "title": "华南地区电力市场交易情况通报",
        "type": "交易公告",
        "content": "本月华南地区电力市场交易活跃，累计成交电量XX亿千瓦时，市场化程度进一步提升...",
        "source": "华南电力交易中心", 
        "preferred_tags": {
            'basic_info': ['交易公告'],
            'region': ['华南地区'],
            'energy_type': ['电力'],
            'business_field': ['市场动态'],
            'beneficiary': ['能源企业'],
            'policy_measure': ['市场监管'],
            'importance': ['常规公告']
        }
    },
    {
        "title": "国际石油市场价格波动分析",
        "type": "行业资讯",
        "content": "受地缘政治因素影响，国际原油价格出现大幅波动，对国内成品油市场产生重要影响...",
        "source": "能源研究院",
        "preferred_tags": {
            'basic_info': ['行业资讯'], 
            'region': ['全国'],
            'energy_type': ['原油'],
            'business_field': ['价格变化', '国际合作'],
            'beneficiary': ['能源企业'],
            'policy_measure': ['市场监管'],
            'importance': ['权威发布']
        }
    },
    {
        "title": "民营企业参与能源投资新政策解读",
        "type": "政策法规",
        "content": "为支持民营企业参与能源领域投资，国家出台了一系列扶持政策，降低准入门槛...",
        "source": "国家能源局",
        "preferred_tags": {
            'basic_info': ['政策法规'],
            'region': ['全国'],
            'energy_type': ['可再生能源'],
            'business_field': ['政策解读'],
            'beneficiary': ['民营企业'],
            'policy_measure': ['投资支持'],
            'importance': ['国家级', '重要政策']
        }
    },
    {
        "title": "北京市煤炭消费总量控制工作进展",
        "type": "行业资讯",
        "content": "北京市持续推进煤炭消费总量控制，清洁能源替代工作取得显著成效...",
        "source": "北京市环保局",
        "preferred_tags": {
            'basic_info': ['行业资讯'],
            'region': ['华北地区', '北京'],
            'energy_type': ['煤炭', '可再生能源'],
            'business_field': ['政策解读'],
            'beneficiary': ['政府机构'],
            'policy_measure': ['市场监管'],
            'importance': ['权威发布']
        }
    },
    {
        "title": "广州电力系统智能化升级项目启动",
        "type": "行业资讯",
        "content": "广州供电局启动大规模电力系统智能化升级项目，提升电网运行效率和可靠性...",
        "source": "南方电网",
        "preferred_tags": {
            'basic_info': ['行业资讯'],
            'region': ['华南地区', '广州'],
            'energy_type': ['电力'],
            'business_field': ['技术创新'],
            'beneficiary': ['能源企业'],
            'policy_measure': ['技术合作'],
            'importance': ['常规公告']
        }
    }
]

def create_test_articles(count=20):
    """创建测试文章数据"""
    articles = []
    
    for i in range(count):
        # 随机选择模板或创建变体
        template = random.choice(ARTICLE_TEMPLATES)
        
        # 创建文章
        article = {
            "发布日期": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
            "文档类型": template["type"],
            "发布时间": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
            "来源机构": template["source"],
            "标题": f"{template['title']} ({i+1})" if i > 0 else template["title"],
            "文章内容": template["content"],
            "链接": f"https://example.com/article/{i+1}",
        }
        
        # 简化标签分配 - 每类只选1-2个标签，总数控制在3-6个
        for category_key, category_name in [
            ('basic_info_tags', 'basic_info'),
            ('region_tags', 'region'), 
            ('energy_type_tags', 'energy_type'),
            ('business_field_tags', 'business_field'),
            ('beneficiary_tags', 'beneficiary'),
            ('policy_measure_tags', 'policy_measure'),
            ('importance_tags', 'importance')
        ]:
            # 从模板的偏好标签中随机选择
            preferred = template["preferred_tags"].get(category_name, [])
            if preferred and random.random() > 0.3:  # 70%概率包含该类标签
                # 每类最多选2个标签
                selected_count = min(2, len(preferred), random.randint(1, 2))
                selected_tags = random.sample(preferred, selected_count)
                article[category_key] = selected_tags
            else:
                article[category_key] = []
        
        articles.append(article)
    
    return articles

def main():
    """生成简化测试数据"""
    print("🔨 正在生成简化的测试数据...")
    
    # 生成20篇测试文章
    articles = create_test_articles(20)
    
    # 检查标签数量分布
    tag_counts = []
    for article in articles:
        total_tags = sum(len(article.get(key, [])) for key in [
            'basic_info_tags', 'region_tags', 'energy_type_tags', 
            'business_field_tags', 'beneficiary_tags', 
            'policy_measure_tags', 'importance_tags'
        ])
        tag_counts.append(total_tags)
    
    print(f"📊 生成统计:")
    print(f"  文章总数: {len(articles)}")
    print(f"  平均标签数: {sum(tag_counts)/len(tag_counts):.1f}")
    print(f"  标签数范围: {min(tag_counts)} - {max(tag_counts)}")
    print()
    
    # 显示前5篇文章的标签情况
    print("📋 前5篇文章示例:")
    for i, article in enumerate(articles[:5]):
        print(f"\n{i+1}. {article['标题']}")
        print(f"   类型: {article['文档类型']}")
        total = 0
        for key in ['basic_info_tags', 'region_tags', 'energy_type_tags', 'business_field_tags', 'beneficiary_tags', 'policy_measure_tags', 'importance_tags']:
            tags = article.get(key, [])
            if tags:
                category = key.replace('_tags', '').replace('_', ' ').title()
                print(f"   {category}: {tags}")
                total += len(tags)
        print(f"   总标签数: {total}")
    
    # 保存到文件
    output_file = '简化测试数据.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 简化测试数据已保存到: {output_file}")
    print("\n💡 建议使用这个简化数据进行测试：")
    print("   - 每篇文章标签数量控制在3-6个")
    print("   - 标签分布更有针对性")
    print("   - 便于测试用户标签变化对推荐内容的影响")

if __name__ == "__main__":
    main() 