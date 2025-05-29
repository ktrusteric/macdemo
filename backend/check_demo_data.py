import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import connect_to_mongo, get_database
from app.services.user_service import UserService

async def check_demo_data():
    """检查演示用户和标签数据"""
    try:
        await connect_to_mongo()
        db = await get_database()
        user_service = UserService(db)
        
        print("🔍 检查演示用户数据...")
        demo_users = await user_service.get_demo_users()
        print(f"📊 演示用户数量: {len(demo_users)}")
        
        if not demo_users:
            print("❌ 未找到演示用户数据")
            return
        
        for user in demo_users:
            print(f"\n👤 演示用户: {user.get('demo_user_id')} - {user.get('username')}")
            print(f"   邮箱: {user.get('email')}")
            print(f"   注册城市: {user.get('register_city')}")
            
            # 检查标签
            try:
                tags = await user_service.get_demo_user_tags(user.get('demo_user_id'))
                if tags:
                    print(f"   ✅ 标签数量: {len(tags.tags)}")
                    print("   🏷️ 标签详情:")
                    for tag in tags.tags[:5]:  # 只显示前5个标签
                        print(f"     - {tag.category}: {tag.name} (权重: {tag.weight})")
                else:
                    print("   ❌ 无标签数据")
            except Exception as tag_error:
                print(f"   ❌ 标签获取失败: {tag_error}")
        
        # 检查内容数据
        print("\n🔍 检查内容数据...")
        from app.services.content_service import ContentService
        content_service = ContentService(db)
        contents = await content_service.get_content_list(limit=5)
        print(f"📊 内容数量（前5条）: {len(contents)}")
        
        if contents:
            for content in contents:
                print(f"   📄 {content.title} ({content.type})")
                all_tags = (
                    content.basic_info_tags + content.region_tags + 
                    content.energy_type_tags + content.business_field_tags +
                    content.beneficiary_tags + content.policy_measure_tags +
                    content.importance_tags
                )
                print(f"      标签: {all_tags[:3]}")
        else:
            print("❌ 未找到内容数据")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_demo_data()) 