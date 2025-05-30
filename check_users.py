#!/usr/bin/env python3
import asyncio
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient

async def check_users():
    client = None
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/')
        
        # 检查多个可能的数据库名称
        for db_name in ['energy_info_db', 'energy_info']:
            db = client[db_name]
            users_count = await db.users.count_documents({})
            content_count = await db.content.count_documents({})
            tags_count = await db.user_tags.count_documents({})
            
            print(f'\n数据库: {db_name}')
            print(f'  用户数: {users_count}')
            print(f'  文章数: {content_count}')
            print(f'  用户标签数: {tags_count}')
            
            if users_count > 0:
                print('  用户列表:')
                async for user in db.users.find().limit(5):
                    print(f'    - {user.get("email", "N/A")} ({user.get("username", "N/A")})')
    except Exception as e:
        print(f'错误: {e}')
    finally:
        if client:
            await client.close()

asyncio.run(check_users()) 