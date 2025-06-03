import asyncio
import motor.motor_asyncio
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.user import UserRole

async def fix_user_schema():
    print("修复用户数据结构...")
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.energy_info
    
    users = await db.users.find({}).to_list(None)
    print(f"找到 {len(users)} 个用户")
    
    for user in users:
        updates = {}
        
        # 修复ID字段
        if 'demo_user_id' in user and 'id' not in user:
            updates['id'] = user['demo_user_id']
        elif 'id' not in user:
            # 生成一个ID
            import uuid
            updates['id'] = str(uuid.uuid4())
        
        # 添加缺失的role字段
        if 'role' not in user:
            if user.get('email', '').startswith('admin'):
                updates['role'] = UserRole.ADMIN
            else:
                updates['role'] = UserRole.FREE
        
        # 添加缺失的is_active字段
        if 'is_active' not in user:
            updates['is_active'] = True
        
        # 添加缺失的has_initial_tags字段
        if 'has_initial_tags' not in user:
            updates['has_initial_tags'] = True
        
        # 添加缺失的created_at字段
        if 'created_at' not in user:
            updates['created_at'] = datetime.utcnow().isoformat()
        
        # 执行更新
        if updates:
            await db.users.update_one(
                {'_id': user['_id']},
                {'$set': updates}
            )
            print(f"更新用户: {user.get('username', user.get('email'))} - {list(updates.keys())}")
    
    print("用户数据结构修复完成！")
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_user_schema()) 