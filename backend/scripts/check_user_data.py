import asyncio
import motor.motor_asyncio
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def check_user_data():
    print("检查用户数据结构...")
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.energy_info
    
    user = await db.users.find_one({'email': 'zhang@shanghai.com'})
    if user:
        user_data = {k: v for k, v in user.items() if k != '_id'}
        print("用户数据结构:")
        print(json.dumps(user_data, indent=2, ensure_ascii=False))
    else:
        print("用户不存在")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_user_data()) 