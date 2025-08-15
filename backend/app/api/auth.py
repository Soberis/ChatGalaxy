from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from jose import JWTError, jwt

from ..database import get_db
from ..models.user import User, UserCreate, UserUpdate, UserResponse
from ..config import get_settings
from ..services.auth_service import AuthService
from ..services.user_service import UserService
from ..utils.response import success_response
from ..utils.logger import get_logger

# 初始化路由器
router = APIRouter(prefix="/api/auth", tags=["认证"])

# 初始化安全组件
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()
logger = get_logger(__name__)

# 初始化服务
auth_service = AuthService()
user_service = UserService()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    创建JWT刷新令牌
    
    Args:
        data: 要编码的数据
        
    Returns:
        str: JWT刷新令牌
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前用户
    
    Args:
        credentials: HTTP认证凭据
        db: 数据库会话
        
    Returns:
        User: 当前用户对象
        
    Raises:
        HTTPException: 认证失败时抛出异常
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 查询用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    
    return user


@router.post("/register", response_model=dict)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    
    Args:
        user_data: 用户注册数据
        db: 数据库会话
        
    Returns:
        dict: 注册结果
    """
    try:
        logger.info(f"用户注册请求: {user_data.email}")
        
        # 检查邮箱是否已存在
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 检查用户名是否已存在
        if user_data.username:
            result = await db.execute(select(User).where(User.username == user_data.username))
            existing_username = result.scalar_one_or_none()
            
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已被使用"
                )
        
        # 创建用户
        user = await user_service.create_user(db, user_data)
        
        # 创建访问令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        logger.info(f"用户注册成功: {user.email}")
        
        return success_response(
            data={
                "user": UserResponse.from_orm(user),
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            },
            message="注册成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户注册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )


@router.post("/login", response_model=dict)
async def login(
    email: str,
    password: str,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    
    Args:
        email: 邮箱
        password: 密码
        db: 数据库会话
        
    Returns:
        dict: 登录结果
    """
    try:
        logger.info(f"用户登录请求: {email}")
        
        # 验证用户凭据
        user = await auth_service.authenticate_user(db, email, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户账户已被禁用"
            )
        
        # 创建访问令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # 更新最后登录时间
        await user_service.update_last_login(db, user.id)
        
        logger.info(f"用户登录成功: {user.email}")
        
        return success_response(
            data={
                "user": UserResponse.from_orm(user),
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            },
            message="登录成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )


@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新访问令牌
    
    Args:
        refresh_token: 刷新令牌
        db: 数据库会话
        
    Returns:
        dict: 新的访问令牌
    """
    try:
        payload = jwt.decode(
            refresh_token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    
    # 验证用户是否存在
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    # 创建新的访问令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return success_response(
        data={
            "access_token": access_token,
            "token_type": "bearer"
        },
        message="令牌刷新成功"
    )


@router.get("/profile", response_model=dict)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """
    获取用户个人信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        dict: 用户信息
    """
    return success_response(
        data=UserResponse.from_orm(current_user),
        message="获取用户信息成功"
    )


@router.put("/profile", response_model=dict)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户个人信息
    
    Args:
        user_update: 用户更新数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 更新结果
    """
    try:
        # 检查用户名是否已被其他用户使用
        if user_update.username and user_update.username != current_user.username:
            result = await db.execute(
                select(User).where(
                    User.username == user_update.username,
                    User.id != current_user.id
                )
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已被使用"
                )
        
        # 更新用户信息
        updated_user = await user_service.update_user(db, current_user.id, user_update)
        
        logger.info(f"用户信息更新成功: {current_user.email}")
        
        return success_response(
            data=UserResponse.from_orm(updated_user),
            message="用户信息更新成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户信息更新失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败，请稍后重试"
        )


@router.post("/change-password", response_model=dict)
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码
    
    Args:
        current_password: 当前密码
        new_password: 新密码
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 修改结果
    """
    try:
        # 验证当前密码
        if not pwd_context.verify(current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前密码错误"
            )
        
        # 更新密码
        await user_service.change_password(db, current_user.id, new_password)
        
        logger.info(f"用户密码修改成功: {current_user.email}")
        
        return success_response(
            message="密码修改成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"密码修改失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码修改失败，请稍后重试"
        )


@router.post("/logout", response_model=dict)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    用户登出
    
    Args:
        current_user: 当前用户
        
    Returns:
        dict: 登出结果
    """
    logger.info(f"用户登出: {current_user.email}")
    
    return success_response(
        message="登出成功"
    )