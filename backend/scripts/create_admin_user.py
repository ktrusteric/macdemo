#!/usr/bin/env python3
"""
创建管理员用户脚本
用于初始化系统管理员账户
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
from bson import ObjectId
import motor.motor_asyncio

async def create_admin_user():
    """创建默认管理员用户"""
    
    # 连接数据库
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.energy_info
    users_collection = db.users
    
    try:
        print("🔧 开始创建管理员用户...")
        
        # 默认管理员信息
        admin_data = {
            "username": "admin",
            "email": "admin@energy-system.com",
            "password": "admin123456",  # 默认密码，建议首次登录后修改
            "role": UserRole.ADMIN
        }
        
        # 检查是否已存在管理员用户
        existing_admin = await users_collection.find_one({
            "$or": [
                {"username": admin_data["username"]},
                {"email": admin_data["email"]}
            ]
        })
        
        if existing_admin:
            print(f"⚠️  管理员用户已存在:")
            print(f"   用户名: {existing_admin.get('username')}")
            print(f"   邮箱: {existing_admin.get('email')}")
            print(f"   角色: {existing_admin.get('role')}")
            return
        
        # 创建管理员用户
        hashed_password = get_password_hash(admin_data["password"])
        
        admin_user = {
            "_id": str(ObjectId()),
            "username": admin_data["username"],
            "email": admin_data["email"],
            "password": hashed_password,
            "role": admin_data["role"],
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "has_initial_tags": False,
            "register_city": "北京"
        }
        
        # 插入数据库
        result = await users_collection.insert_one(admin_user)
        
        if result.inserted_id:
            print("✅ 管理员用户创建成功!")
            print(f"   用户名: {admin_data['username']}")
            print(f"   邮箱: {admin_data['email']}")
            print(f"   默认密码: {admin_data['password']}")
            print(f"   用户ID: {admin_user['_id']}")
            print("\n🔒 安全提醒:")
            print("   1. 请立即登录并修改默认密码")
            print("   2. 建议使用强密码（至少8位，包含字母、数字、特殊字符）")
            print("   3. 定期更换密码以确保账户安全")
            print("\n🌐 管理员登录地址:")
            print("   后端API: http://localhost:8001/docs")
            print("   前端管理: http://localhost:5173/admin/login")
        else:
            print("❌ 管理员用户创建失败")
            
    except Exception as e:
        print(f"❌ 创建管理员用户时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

async def create_multiple_admin_users():
    """创建多个管理员用户（用于测试）"""
    
    # 连接数据库
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.energy_info
    users_collection = db.users
    
    try:
        print("🔧 开始创建多个管理员用户...")
        
        # 多个管理员用户信息
        admin_users = [
            {
                "username": "admin",
                "email": "admin@energy-system.com",
                "password": "admin123456",
                "role": UserRole.ADMIN,
                "register_city": "北京"
            },
            {
                "username": "superadmin",
                "email": "superadmin@energy-system.com", 
                "password": "super123456",
                "role": UserRole.ADMIN,
                "register_city": "上海"
            },
            {
                "username": "manager",
                "email": "manager@energy-system.com",
                "password": "manager123456", 
                "role": UserRole.ADMIN,
                "register_city": "深圳"
            }
        ]
        
        created_count = 0
        
        for admin_data in admin_users:
            # 检查是否已存在
            existing_admin = await users_collection.find_one({
                "$or": [
                    {"username": admin_data["username"]},
                    {"email": admin_data["email"]}
                ]
            })
            
            if existing_admin:
                print(f"⚠️  用户 {admin_data['username']} 已存在，跳过创建")
                continue
            
            # 创建用户
            hashed_password = get_password_hash(admin_data["password"])
            
            admin_user = {
                "_id": str(ObjectId()),
                "username": admin_data["username"],
                "email": admin_data["email"],
                "password": hashed_password,
                "role": admin_data["role"],
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "has_initial_tags": False,
                "register_city": admin_data["register_city"]
            }
            
            # 插入数据库
            result = await users_collection.insert_one(admin_user)
            
            if result.inserted_id:
                print(f"✅ 管理员用户 {admin_data['username']} 创建成功")
                created_count += 1
            else:
                print(f"❌ 管理员用户 {admin_data['username']} 创建失败")
        
        print(f"\n📊 创建完成统计:")
        print(f"   成功创建: {created_count} 个管理员用户")
        print(f"   总计尝试: {len(admin_users)} 个用户")
        
        if created_count > 0:
            print("\n🔒 安全提醒:")
            print("   1. 请立即登录并修改所有默认密码")
            print("   2. 建议为每个管理员设置不同的强密码")
            print("   3. 定期审查管理员账户权限")
            
    except Exception as e:
        print(f"❌ 创建管理员用户时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

async def list_admin_users():
    """列出所有管理员用户"""
    
    # 连接数据库
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.energy_info
    users_collection = db.users
    
    try:
        print("📋 查询所有管理员用户...")
        
        # 查询所有管理员用户
        cursor = users_collection.find({"role": UserRole.ADMIN})
        admin_users = await cursor.to_list(length=None)
        
        if not admin_users:
            print("❌ 未找到任何管理员用户")
            print("💡 提示: 运行 'python create_admin_user.py' 创建默认管理员")
            return
        
        print(f"✅ 找到 {len(admin_users)} 个管理员用户:")
        print("-" * 80)
        
        for i, user in enumerate(admin_users, 1):
            print(f"{i}. 用户名: {user.get('username')}")
            print(f"   邮箱: {user.get('email')}")
            print(f"   角色: {user.get('role')}")
            print(f"   状态: {'激活' if user.get('is_active') else '禁用'}")
            print(f"   注册城市: {user.get('register_city', '未设置')}")
            print(f"   创建时间: {user.get('created_at', '未知')}")
            print(f"   用户ID: {user.get('_id')}")
            print("-" * 80)
            
    except Exception as e:
        print(f"❌ 查询管理员用户时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="管理员用户管理脚本")
    parser.add_argument(
        "--action", 
        choices=["create", "create-multiple", "list"], 
        default="create",
        help="执行的操作: create(创建单个), create-multiple(创建多个), list(列出所有)"
    )
    
    args = parser.parse_args()
    
    if args.action == "create":
        asyncio.run(create_admin_user())
    elif args.action == "create-multiple":
        asyncio.run(create_multiple_admin_users())
    elif args.action == "list":
        asyncio.run(list_admin_users())

if __name__ == "__main__":
    main() 