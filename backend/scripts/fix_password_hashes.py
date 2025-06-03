#!/usr/bin/env python3
"""
修复用户密码哈希脚本
用于修复bcrypt兼容性问题导致的密码哈希问题
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_database
from app.core.security import get_password_hash
from app.models.user import UserRole
import motor.motor_asyncio

# 预设用户密码映射
USER_PASSWORDS = {
    'zhang@shanghai.com': 'demo123',
    'li@beijing.com': 'demo123', 
    'wang@shenzhen.com': 'demo123',
    'chen@guangzhou.com': 'demo123',
    'liu@chengdu.com': 'demo123',
    'admin@energy-system.com': 'admin123456',
    'superadmin@energy-system.com': 'super123456'
}

async def fix_password_hashes():
    """修复所有用户的密码哈希"""
    
    # 连接数据库
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.energy_info
    users_collection = db.users
    
    try:
        print("🔧 开始修复用户密码哈希...")
        
        # 获取所有用户
        users = await users_collection.find({}).to_list(None)
        print(f"📊 找到 {len(users)} 个用户记录")
        
        fixed_count = 0
        for user in users:
            email = user.get('email')
            username = user.get('username', 'Unknown')
            current_hash = user.get('hashed_password', '')
            
            print(f"\n👤 处理用户: {username} ({email})")
            
            # 确定密码
            password = USER_PASSWORDS.get(email)
            if not password:
                print(f"   ⚠️  未找到预设密码，跳过")
                continue
            
            # 生成新的哈希
            try:
                new_hash = get_password_hash(password)
                print(f"   🔐 生成新哈希: {new_hash[:20]}...")
                
                # 更新数据库
                result = await users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"hashed_password": new_hash}}
                )
                
                if result.modified_count > 0:
                    print(f"   ✅ 密码哈希更新成功")
                    fixed_count += 1
                else:
                    print(f"   ❌ 密码哈希更新失败")
                    
            except Exception as e:
                print(f"   ❌ 生成哈希失败: {str(e)}")
        
        print(f"\n📋 修复完成统计:")
        print(f"   总用户数: {len(users)}")
        print(f"   修复成功: {fixed_count}")
        print(f"   修复失败: {len(users) - fixed_count}")
        
        # 验证修复结果
        print(f"\n🧪 验证修复结果...")
        test_user = await users_collection.find_one({"email": "zhang@shanghai.com"})
        if test_user and test_user.get('hashed_password'):
            from app.core.security import verify_password
            test_result = verify_password('demo123', test_user['hashed_password'])
            print(f"   测试用户验证: {'✅ 成功' if test_result else '❌ 失败'}")
        else:
            print(f"   ❌ 测试用户未找到或密码哈希为空")
            
    except Exception as e:
        print(f"❌ 修复过程发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_password_hashes()) 