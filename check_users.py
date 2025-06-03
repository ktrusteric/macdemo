#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient

def check_users():
    """检查用户数据"""
    client = MongoClient('mongodb://localhost:27017')
    db = client.energy_info
    users_collection = db.users
    
    print("=== 用户数据检查 ===")
    
    # 获取所有用户
    users = list(users_collection.find({}, {'username': 1, 'role': 1, 'email': 1, 'register_city': 1}))
    
    print(f"数据库中的用户 (总计: {len(users)} 个):")
    for user in users:
        username = user.get('username', 'N/A')
        role = user.get('role', 'N/A') 
        email = user.get('email', 'N/A')
        city = user.get('register_city', 'N/A')
        print(f"  {username} - {role} - {email} - {city}")
    
    # 统计角色分布
    admin_count = users_collection.count_documents({"role": "admin"})
    user_count = users_collection.count_documents({"role": "user"})
    total_count = users_collection.count_documents({})
    
    print(f"\n角色统计:")
    print(f"  管理员: {admin_count}")
    print(f"  普通用户: {user_count}")
    print(f"  总用户数: {total_count}")
    
    # 检查内置管理员账户
    print(f"\n内置管理员账户 (不在数据库中):")
    print(f"  superadmin - admin - superadmin@energy-system.com")
    print(f"  admin - admin - admin@energy-system.com")
    
    # 实际统计应该包含内置管理员
    actual_admin_count = admin_count + 2  # 加上2个内置管理员
    actual_total_count = total_count + 2
    
    print(f"\n实际统计 (包含内置管理员):")
    print(f"  管理员: {actual_admin_count}")
    print(f"  普通用户: {user_count}")
    print(f"  总用户数: {actual_total_count}")
    
    return {
        "db_users": total_count,
        "db_admins": admin_count,
        "db_regular": user_count,
        "actual_total": actual_total_count,
        "actual_admins": actual_admin_count,
        "actual_regular": user_count
    }

if __name__ == "__main__":
    check_users() 