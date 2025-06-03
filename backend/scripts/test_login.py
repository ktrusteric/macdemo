import asyncio
import motor.motor_asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import verify_password

async def test_login():
    print("测试登录验证...")
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.energy_info
    
    # 测试用户
    test_emails = ['zhang@shanghai.com', 'li@beijing.com', 'wang@shenzhen.com']
    
    for email in test_emails:
        user = await db.users.find_one({'email': email})
        if user:
            result = verify_password('demo123', user['hashed_password'])
            print(f'{email}: {"✅ 成功" if result else "❌ 失败"}')
        else:
            print(f'{email}: ❌ 用户不存在')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_login()) 