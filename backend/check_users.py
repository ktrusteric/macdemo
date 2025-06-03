import asyncio
import motor.motor_asyncio

async def check_users():
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.energy_info
    
    # 检查所有用户
    users = await db.users.find({}).to_list(None)
    print(f'总共 {len(users)} 个用户:')
    for user in users:
        print(f'  - {user.get("username", "未知")} ({user.get("email", "未知")}) - {user.get("role", "未知")}')
    
    # 检查管理员用户
    admins = await db.users.find({'role': 'admin'}).to_list(None)
    print(f'\n找到 {len(admins)} 个管理员用户:')
    for admin in admins:
        print(f'  - {admin.get("username", "未知")} ({admin.get("email", "未知")})')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_users()) 