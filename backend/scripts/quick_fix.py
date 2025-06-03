import asyncio
import motor.motor_asyncio
import sys
import os

# 添加上级目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import get_password_hash

async def quick_fix():
    print("开始修复密码哈希...")
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.energy_info
    users = await db.users.find({}).to_list(None)
    
    passwords = {
        'zhang@shanghai.com': 'demo123',
        'li@beijing.com': 'demo123', 
        'wang@shenzhen.com': 'demo123',
        'chen@guangzhou.com': 'demo123',
        'liu@chengdu.com': 'demo123'
    }
    
    for user in users:
        email = user.get('email')
        if email in passwords:
            new_hash = get_password_hash(passwords[email])
            await db.users.update_one({'_id': user['_id']}, {'$set': {'hashed_password': new_hash}})
            print(f'修复完成: {email}')
    
    client.close()
    print("修复完成！")

if __name__ == "__main__":
    asyncio.run(quick_fix()) 