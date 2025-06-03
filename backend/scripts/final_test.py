#!/usr/bin/env python3
import asyncio
import motor.motor_asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import verify_password

async def final_test():
    print("🧪 最终登录功能验证")
    print("=" * 50)
    
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.energy_info
    
    # 测试用户列表
    test_users = [
        ('zhang@shanghai.com', 'demo123'),
        ('li@beijing.com', 'demo123'),
        ('wang@shenzhen.com', 'demo123'),
        ('chen@guangzhou.com', 'demo123'),
        ('liu@chengdu.com', 'demo123')
    ]
    
    print("1. 密码哈希验证测试:")
    all_passed = True
    
    for email, password in test_users:
        user = await db.users.find_one({'email': email})
        if user:
            has_required_fields = all(field in user for field in ['id', 'role', 'is_active', 'hashed_password'])
            password_valid = verify_password(password, user['hashed_password'])
            
            status = "✅" if has_required_fields and password_valid else "❌"
            print(f"   {status} {user['username']} ({email})")
            
            if not (has_required_fields and password_valid):
                all_passed = False
                if not has_required_fields:
                    print(f"     - 缺少必要字段")
                if not password_valid:
                    print(f"     - 密码验证失败")
        else:
            print(f"   ❌ {email} - 用户不存在")
            all_passed = False
    
    print(f"\n2. 总体测试结果:")
    if all_passed:
        print("   ✅ 所有用户登录功能正常")
        print("   ✅ bcrypt哈希问题已解决")
        print("   ✅ 用户数据结构完整")
        print("\n🎉 登录功能修复完成！")
        print("\n📱 可以测试的账号:")
        for email, password in test_users:
            user = await db.users.find_one({'email': email})
            if user:
                print(f"   - {user['username']}: {email} / {password}")
    else:
        print("   ❌ 仍有问题需要解决")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(final_test()) 