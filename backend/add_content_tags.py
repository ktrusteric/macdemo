import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import connect_to_mongo, get_database
from app.services.content_service import ContentService

async def add_content_tags():
    """为现有内容添加标签"""
    try:
        await connect_to_mongo()
        db = await get_database()
        content_service = ContentService(db)
        
        print("🔍 获取现有内容...")
        contents = await content_service.get_content_list(limit=100)
        print(f"📊 找到 {len(contents)} 条内容")
        
        updates = []
        
        for content in contents:
            print(f"\n📄 处理内容: {content.title}")
            
            # 根据标题内容智能添加标签
            title_lower = content.title.lower()
            
            # 基础信息标签
            basic_info_tags = []
            if "公告" in content.title or "通知" in content.title:
                basic_info_tags.append("公告通知")
            if "价格" in content.title:
                basic_info_tags.append("价格信息")
            if "交易" in content.title:
                basic_info_tags.append("交易信息")
            
            # 地区标签
            region_tags = []
            if "华东" in content.title or "浙沪" in content.title or "浙江" in content.title or "上海" in content.title:
                region_tags.extend(["华东地区", "上海", "浙江省"])
            if "华北" in content.title or "北京" in content.title:
                region_tags.extend(["华北地区", "北京"])
            if "华南" in content.title or "广东" in content.title or "深圳" in content.title or "广州" in content.title:
                region_tags.extend(["华南地区", "广东省"])
            if "西南" in content.title or "四川" in content.title or "成都" in content.title:
                region_tags.extend(["西南地区", "四川省"])
            if "中国" in content.title:
                region_tags.append("全国")
            
            # 能源类型标签
            energy_type_tags = []
            if "天然气" in title_lower or "lng" in title_lower or "管道气" in title_lower:
                energy_type_tags.extend(["天然气", "LNG"])
            if "重烃" in content.title:
                energy_type_tags.append("重烃")
            if "原油" in title_lower:
                energy_type_tags.append("原油")
            if "电力" in title_lower:
                energy_type_tags.append("电力")
            if "煤炭" in title_lower:
                energy_type_tags.append("煤炭")
            
            # 业务领域标签
            business_field_tags = []
            if "竞价" in content.title or "拍卖" in content.title:
                business_field_tags.append("竞价交易")
            if "进口" in content.title:
                business_field_tags.append("进口贸易")
            if "集团" in content.title or "公司" in content.title:
                business_field_tags.append("企业动态")
            if "系统" in content.title:
                business_field_tags.append("系统运营")
            
            # 受益主体标签
            beneficiary_tags = []
            if "燃气" in content.title:
                beneficiary_tags.append("燃气企业")
            if "集团" in content.title:
                beneficiary_tags.append("能源集团")
            
            # 政策措施标签
            policy_measure_tags = []
            if "关于" in content.title and "公告" in content.title:
                policy_measure_tags.append("政策公告")
            
            # 重要性标签
            importance_tags = []
            if "重要" in content.title or "重大" in content.title:
                importance_tags.append("重要")
            elif "公告" in content.title:
                importance_tags.append("一般")
            
            # 构建更新数据
            update_data = {
                "basic_info_tags": basic_info_tags,
                "region_tags": list(set(region_tags)),  # 去重
                "energy_type_tags": list(set(energy_type_tags)),
                "business_field_tags": business_field_tags,
                "beneficiary_tags": beneficiary_tags,
                "policy_measure_tags": policy_measure_tags,
                "importance_tags": importance_tags
            }
            
            print(f"   🏷️ 添加标签:")
            for category, tags in update_data.items():
                if tags:
                    print(f"     {category}: {tags}")
            
            # 更新到数据库
            try:
                from bson import ObjectId
                await db.content.update_one(
                    {"_id": ObjectId(content.id)},
                    {"$set": update_data}
                )
                updates.append(content.id)
            except Exception as update_error:
                print(f"   ❌ 更新失败: {update_error}")
        
        print(f"\n✅ 完成！成功更新了 {len(updates)} 条内容的标签")
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_content_tags()) 