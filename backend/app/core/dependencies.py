from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import verify_token
from app.db.session import AsyncSessionLocal
from app.models.system import User
from app.schemas.auth import TokenPayload
# 获取数据库会话
async def get_db() -> Generator[AsyncSession, None, None]:
    async with AsyncSessionLocal() as session:
        yield session
# 获取当前用户
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(settings.oauth2_scheme)
) -> Optional[User]:
    try:
        token_data = verify_token(token)
        if not token_data or not token_data.sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await db.get(User, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user
# 获取当前活跃用户
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    return current_user
# 获取当前超级管理员
async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要超级管理员权限"
        )
    return current_user
