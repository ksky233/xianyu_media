# Token 认证系统说明

本项目实现了双重token认证系统：JWT访问令牌（有时效性）和API令牌（持久有效）。

## 系统架构

### 1. JWT 访问令牌 (Access Token)
- **用途**: 用户身份验证，有时效性
- **有效期**: 30分钟（可配置）
- **使用场景**: 用户登录后的常规API访问
- **格式**: 标准JWT格式

### 2. API 令牌 (API Token)
- **用途**: 系统间调用，持久有效
- **有效期**: 永久有效（直到手动撤销）
- **使用场景**: 第三方集成、自动化脚本
- **格式**: `api_` + 64位十六进制哈希

## 核心文件说明

### `app/core/config.py`
配置文件，包含JWT和API Token的相关设置：
```python
SECRET_KEY: str = "your-secret-key-change-in-production"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
API_TOKEN_PREFIX: str = "api_"
```

### `app/core/security.py`
核心安全功能模块：
- `create_access_token()`: 创建JWT访问令牌
- `verify_access_token()`: 验证JWT访问令牌
- `generate_api_token()`: 生成API令牌
- `hash_api_token()`: 对API令牌进行哈希
- `verify_api_token()`: 验证API令牌
- `get_current_user_from_token()`: JWT令牌验证依赖
- `verify_api_token_dependency()`: API令牌格式验证依赖

### `app/api/deps.py`
依赖注入模块：
- `get_current_user()`: 获取当前用户（JWT认证）
- `get_api_token()`: 获取API令牌
- `verify_api_token_with_db()`: 验证API令牌并查询数据库
- `get_current_active_user()`: 获取活跃用户信息

## API 端点说明

### 认证相关端点 (`/api/v1/auth/`)

#### 1. 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "demo",
    "password": "demo"
}
```

响应：
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
}
```

#### 2. 生成API令牌
```http
POST /api/v1/auth/generate-api-token
Authorization: Bearer <JWT_TOKEN>
```

响应：
```json
{
    "api_token": "api_1234567890abcdef...",
    "token_hash": "abcdef1234567890...",
    "token_type": "bearer",
    "message": "API token generated successfully..."
}
```

#### 3. 获取用户信息（JWT认证）
```http
GET /api/v1/auth/me
Authorization: Bearer <JWT_TOKEN>
```

#### 4. 获取API信息（API Token认证）
```http
GET /api/v1/auth/api-info
Authorization: Bearer <API_TOKEN>
```

## 使用示例

### 1. JWT 认证流程
```python
from fastapi import Depends
from app.api.deps import get_current_active_user

@router.get("/protected")
async def protected_endpoint(
    current_user: dict = Depends(get_current_active_user)
):
    return {"message": "Access granted", "user": current_user}
```

### 2. API Token 认证流程
```python
from fastapi import Depends
from app.api.deps import verify_api_token_with_db

@router.get("/api-endpoint")
async def api_endpoint(
    token_info: dict = Depends(verify_api_token_with_db)
):
    return {"message": "API access granted", "token_info": token_info}
```

## 安全注意事项

1. **生产环境配置**:
   - 修改 `SECRET_KEY` 为强随机字符串
   - 配置适当的CORS策略
   - 使用HTTPS

2. **API Token 管理**:
   - API Token 只在生成时显示一次
   - 建议定期轮换API Token
   - 在数据库中存储token的哈希值，不存储原始token

3. **JWT Token 管理**:
   - 设置合适的过期时间
   - 考虑实现token刷新机制
   - 敏感操作可要求重新认证

## 数据库集成

当前实现中，数据库相关功能使用TODO标记，需要根据实际数据库模型进行实现：

```python
# 示例：API Token 数据库模型
class ApiToken(Base):
    __tablename__ = "api_tokens"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token_hash = Column(String(64), unique=True, index=True)
    name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)
```

## 启动应用

```bash
# 开发环境
python main.py

# 或使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看API文档。