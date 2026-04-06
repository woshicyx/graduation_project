"""
用户认证和授权API
"""

from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..models_extended import User, UserRole
from ..schemas_extended import (
    UserCreate, UserResponse, UserLogin, TokenResponse,
    UserProfileResponse, SocialLogin, UserUpdate
)

router = APIRouter(prefix="/auth", tags=["认证"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# JWT配置（生产环境应从环境变量读取）
SECRET_KEY = "movieai-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

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
        # bcrypt验证
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前认证用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """获取当前管理员用户"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return current_user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 创建用户
    hashed_password = get_password_hash(user_data.password)
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        display_name=user_data.display_name or user_data.username,
        role=UserRole.USER,
        is_active=True,
        is_verified=False,
        preferences={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/login", response_model=TokenResponse)
async def login(form_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户（支持用户名或邮箱登录）
    user = db.query(User).filter(
        (User.username == form_data.identifier) | (User.email == form_data.identifier)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账户已被禁用"
        )
    
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    # 创建刷新令牌（简化版，生产环境需要更复杂的实现）
    refresh_token = create_access_token(
        data={"sub": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=7)
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        user=user
    )

@router.post("/social-login", response_model=TokenResponse)
async def social_login(login_data: SocialLogin, db: Session = Depends(get_db)):
    """社交登录（GitHub/Google）"""
    # 根据提供商查找用户
    if login_data.provider == "github":
        user = db.query(User).filter(User.github_id == login_data.token).first()
    elif login_data.provider == "google":
        user = db.query(User).filter(User.google_id == login_data.token).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的登录提供商"
        )
    
    # 如果用户不存在，检查是否有匹配的邮箱
    if not user and login_data.email:
        user = db.query(User).filter(User.email == login_data.email).first()
        if user:
            # 关联社交账号
            if login_data.provider == "github":
                user.github_id = login_data.token
            else:
                user.google_id = login_data.token
            db.commit()
    
    # 如果用户仍不存在，创建新用户
    if not user:
        if not login_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新用户需要提供邮箱"
            )
        
        # 生成用户名
        base_username = login_data.email.split('@')[0]
        username = base_username
        counter = 1
        
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User(
            username=username,
            email=login_data.email,
            password_hash="social_login",  # 社交登录用户不需要密码
            display_name=base_username,
            role=UserRole.USER,
            is_active=True,
            is_verified=True,  # 社交登录用户默认已验证
            preferences={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        if login_data.provider == "github":
            user.github_id = login_data.token
        else:
            user.google_id = login_data.token
        
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账户已被禁用"
        )
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_access_token(
        data={"sub": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=7)
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        user=user
    )

@router.post("/logout")
async def logout():
    """用户登出"""
    # 客户端需要删除本地存储的令牌
    return {"message": "登出成功"}

@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    # 计算用户统计数据
    from sqlalchemy import func
    
    watch_count = db.query(func.count(UserWatchHistory.id)).filter(
        UserWatchHistory.user_id == current_user.id
    ).scalar() or 0
    
    favorite_count = db.query(func.count(UserFavorite.id)).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.is_liked == True
    ).scalar() or 0
    
    rating_count = db.query(func.count(UserRating.id)).filter(
        UserRating.user_id == current_user.id
    ).scalar() or 0
    
    # 注意：这里需要导入UserWatchHistory, UserFavorite, UserRating模型
    # 由于模型在models_extended.py中定义，这里使用字符串引用
    
    return UserProfileResponse(
        **current_user.__dict__,
        watch_count=watch_count,
        favorite_count=favorite_count,
        rating_count=rating_count
    )

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    update_data = user_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str = Cookie(None), db: Session = Depends(get_db)):
    """刷新访问令牌"""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌不存在"
        )
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌已过期"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    # 创建新的刷新令牌
    new_refresh_token = create_access_token(
        data={"sub": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=7)
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        user=user
    )