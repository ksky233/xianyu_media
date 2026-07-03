#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT认证系统测试脚本

测试用户登录、JWT token生成和验证功能
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.jwt_auth import jwt_auth
from app.schemas.user_schema import UserLogin, UserChangePassword, JWTPayload
from app.models.user import UserRole


def test_jwt_token_operations():
    """测试JWT token的生成和验证"""
    print("\n=== JWT Token 操作测试 ===")
    
    # 测试数据
    user_id = 1
    username = "admin"
    role = UserRole.ADMIN.value
    
    print(f"测试用户: ID={user_id}, 用户名={username}, 角色={role}")
    
    # 生成JWT token
    print("\n1. 生成JWT token...")
    token = jwt_auth.create_user_token(user_id, username, role)
    print(f"生成的token: {token[:50]}...")
    
    # 验证JWT token
    print("\n2. 验证JWT token...")
    payload = jwt_auth.verify_token(token)
    
    if payload:
        print("✅ Token验证成功!")
        print(f"   用户ID: {payload.sub}")
        print(f"   用户名: {payload.username}")
        print(f"   角色: {payload.role}")
        print(f"   过期时间: {datetime.fromtimestamp(payload.exp) if payload.exp else 'N/A'}")
    else:
        print("❌ Token验证失败!")
        return False
    
    # 测试无效token
    print("\n3. 测试无效token...")
    invalid_token = "invalid.token.here"
    invalid_payload = jwt_auth.verify_token(invalid_token)
    
    if invalid_payload is None:
        print("✅ 无效token正确被拒绝!")
    else:
        print("❌ 无效token验证异常!")
        return False
    
    return True


def test_user_schema_validation():
    """测试用户相关的Pydantic模型验证"""
    print("\n=== 用户模型验证测试 ===")
    
    # 测试用户登录模型
    print("\n1. 测试用户登录模型...")
    try:
        login_data = UserLogin(username="admin", password="password123")
        print(f"✅ 登录数据验证成功: {login_data.username}")
    except Exception as e:
        print(f"❌ 登录数据验证失败: {str(e)}")
        return False
    
    # 测试密码修改模型
    print("\n2. 测试密码修改模型...")
    try:
        change_data = UserChangePassword(
            old_password="old123",
            new_password="new123",
            confirm_password="new123"
        )
        print("✅ 密码修改数据验证成功")
        
        # 测试密码匹配验证
        if change_data.validate_passwords_match():
            print("✅ 密码匹配验证通过")
        else:
            print("❌ 密码匹配验证失败")
            return False
            
    except Exception as e:
        print(f"❌ 密码修改数据验证失败: {str(e)}")
        return False
    
    # 测试密码不匹配的情况
    print("\n3. 测试密码不匹配情况...")
    try:
        mismatch_data = UserChangePassword(
            old_password="old123",
            new_password="new123",
            confirm_password="different123"
        )
        
        if not mismatch_data.validate_passwords_match():
            print("✅ 密码不匹配正确被检测")
        else:
            print("❌ 密码不匹配检测失败")
            return False
            
    except Exception as e:
        print(f"❌ 密码不匹配测试异常: {str(e)}")
        return False
    
    return True


def test_jwt_payload_model():
    """测试JWT载荷模型"""
    print("\n=== JWT载荷模型测试 ===")
    
    try:
        # 创建JWT载荷
        payload = JWTPayload(
            sub="1",
            username="admin",
            role="admin",
            exp=1234567890
        )
        
        print(f"✅ JWT载荷创建成功:")
        print(f"   用户ID: {payload.sub}")
        print(f"   用户名: {payload.username}")
        print(f"   角色: {payload.role}")
        print(f"   过期时间戳: {payload.exp}")
        
        return True
        
    except Exception as e:
        print(f"❌ JWT载荷创建失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始JWT认证系统测试...")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        test_jwt_token_operations,
        test_user_schema_validation,
        test_jwt_payload_model
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_func.__name__} 测试通过")
            else:
                print(f"\n❌ {test_func.__name__} 测试失败")
        except Exception as e:
            print(f"\n💥 {test_func.__name__} 测试异常: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过! JWT认证系统基础功能正常")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关功能")
        return False


if __name__ == "__main__":
    # 设置环境变量（测试用）
    os.environ.setdefault("SECRET_KEY", "test-secret-key-for-jwt-testing-only")
    os.environ.setdefault("ALGORITHM", "HS256")
    os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    
    success = main()
    sys.exit(0 if success else 1)