"""
用户认证API - 使用psycopg2
"""
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt

from fastapi import APIRouter, HTTPException, status, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.core.config import settings
from app.core.db import Database

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer(auto_error=False)

# JWT配置
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


# 请求/响应模型
class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str


class UserLoginRequest(BaseModel):
    identifier: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str]
    token_type: str
    expires_in: int
    user: UserResponse


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegisterRequest):
    """用户注册"""
    # 检查密码确认
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码不匹配"
        )
    
    # 检查用户名是否已存在
    existing = Database.fetchrow(
        "SELECT id FROM users WHERE username = %s",
        user_data.username
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    existing_email = Database.fetchrow(
        "SELECT id FROM users WHERE email = %s",
        user_data.email
    )
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 创建用户
    hashed_password = get_password_hash(user_data.password)
    now = datetime.utcnow()
    
    # 使用直接执行方式确保事务提交
    from app.core.db import get_connection
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (username, email, password_hash, display_name, role, is_active, is_verified, preferences, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, username, email, display_name, role, is_active, is_verified, created_at, updated_at
            """, (
                user_data.username,
                user_data.email,
                hashed_password,
                user_data.username,  # display_name
                'user',  # role
                True,  # is_active
                False,  # is_verified
                '{}',  # preferences
                now,
                now
            ))
            result = cur.fetchone()
            conn.commit()
            # 将元组转换为字典
            columns = ['id', 'username', 'email', 'display_name', 'role', 'is_active', 'is_verified', 'created_at', 'updated_at']
            result = dict(zip(columns, result))
    
    return UserResponse(
        id=result['id'],
        username=result['username'],
        email=result['email'],
        role=result['role'],
        is_active=result['is_active'],
        is_verified=result['is_verified'],
        created_at=result['created_at'],
        updated_at=result['updated_at']
    )


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLoginRequest):
    """用户登录"""
    # 查找用户
    user = Database.fetchrow(
        "SELECT * FROM users WHERE username = %s OR email = %s",
        login_data.identifier,
        login_data.identifier
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user['is_active']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账户已被禁用"
        )
    
    if not verify_password(login_data.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 更新最后登录时间
    Database.execute(
        "UPDATE users SET last_login_at = %s WHERE id = %s",
        datetime.utcnow(),
        user['id']
    )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user['id']), "role": user['role']},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_access_token(
        data={"sub": str(user['id']), "type": "refresh"},
        expires_delta=timedelta(days=7)
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        user=UserResponse(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            role=user['role'],
            is_active=user['is_active'],
            is_verified=user['is_verified'],
            created_at=user['created_at'],
            updated_at=user['updated_at']
        )
    )


@router.post("/logout")
def logout():
    """用户登出"""
    return {"message": "登出成功"}


def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """从Bearer token获取当前用户"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌",
            )
        
        # 获取用户信息
        user = Database.fetchrow(
            "SELECT * FROM users WHERE id = %s AND is_active = true",
            int(user_id)
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用",
            )
        
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
        )


@router.get("/me", response_model=UserResponse)
def get_current_user(user: dict = Depends(get_current_user_from_token)):
    """获取当前用户信息（需要Bearer token）"""
    return UserResponse(
        id=user['id'],
        username=user['username'],
        email=user['email'],
        role=user['role'],
        is_active=user['is_active'],
        is_verified=user['is_verified'],
        created_at=user['created_at'],
        updated_at=user['updated_at']
    )
