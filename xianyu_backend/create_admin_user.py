#!/usr/bin/env python3
"""
创建默认admin用户的脚本

使用方法:
1. 直接运行脚本，使用默认密码 'admin123'
2. 或者通过环境变量 ADMIN_PASSWORD 设置自定义密码

示例:
    python create_admin_user.py
    # 或
    ADMIN_PASSWORD=your_password python create_admin_user.py
"""

import os
import asyncio
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User
from app.crud.crud_user import UserCRUD


def get_password_hash(password: str) -> str:
    """生成密码hash
    
    Args:
        password: 明文密码
        
    Returns:
        str: hash后的密码
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


async def create_admin_user():
    """创建默认admin用户"""
    # 获取密码（优先使用环境变量，否则使用默认密码）
    admin_password = os.getenv('ADMIN_PASSWORD', '1234qwer')
    
    # 生成密码hash
    hashed_password = get_password_hash(admin_password)
    
    print(f"生成的密码hash: {hashed_password}")
    print(f"明文密码: {admin_password}")
    print("\n请将以下SQL语句在数据库中执行:")
    print("\n" + "="*50)
    
    # 生成SQL插入语句
    sql = f"""
INSERT INTO users (username, email, hashed_password, role, deleted_at, created_at, updated_at)
VALUES (
    'admin',
    'admin@admin.com',
    '{hashed_password}',
    'admin',
    NULL,
    NOW(),
    NOW()
)
ON CONFLICT (username) DO UPDATE SET
    hashed_password = EXCLUDED.hashed_password,
    role = 'admin',
    deleted_at = NULL,
    updated_at = NOW();
"""
    
    print(sql)
    print("="*50)
    print("\n注意事项:")
    print("1. 如果admin用户已存在，此SQL会更新其密码和状态")
    print("2. 请妥善保管admin密码")
    print(f"3. 默认用户名: admin")
    print(f"4. 默认邮箱: admin@admin.com")
    print(f"5. 密码: {admin_password}")
    
    # 尝试通过程序创建（如果数据库连接可用）
    try:
        # 创建数据库引擎
        engine = create_async_engine(settings.DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            user_crud = UserCRUD(session)
            
            # 检查admin用户是否已存在
            existing_user = await user_crud.get_by_username_or_email('admin')
            
            if existing_user:
                print("\n✅ 检测到admin用户已存在，正在更新密码...")
                # 更新现有用户
                existing_user.hashed_password = hashed_password
                existing_user.deleted_at = None  # 设置为活跃状态
                existing_user.role = 'admin'  # 设置为管理员角色
                await session.commit()
                print("✅ admin用户密码已更新")
            else:
                print("\n✅ 正在创建新的admin用户...")
                # 创建新用户
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    hashed_password=hashed_password,
                    role='admin',  # 设置为管理员角色
                    deleted_at=None  # 设置为活跃状态
                )
                session.add(admin_user)
                await session.commit()
                print("✅ admin用户创建成功")
                
        await engine.dispose()
        
    except Exception as e:
        print(f"\n⚠️  程序创建失败: {e}")
        print("请手动执行上述SQL语句")


if __name__ == "__main__":
    asyncio.run(create_admin_user())