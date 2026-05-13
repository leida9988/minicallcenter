from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_db
from app.models.system import User
from app.schemas.auth import Token, LoginResponse
from app.utils.security import create_access_token, verify_password
from app.utils.logger import logger
router = APIRouter()
@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    用户登录接口，获取访问令牌
    - **username**: 用户名
    - **password**: 密码
    """
    # 查询用户
    user = await User.get_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        logger.warning(f"登录失败: 用户名或密码错误 - {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        logger.warning(f"登录失败: 用户已被禁用 - {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    logger.info(f"用户登录成功: {user.username}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": LoginResponse(**user.to_dict())
    }
@router.post("/logout", summary="用户登出")
async def logout():
    """
    用户登出接口
    """
    # TODO: 实现Token黑名单机制
    return {"code": 200, "message": "登出成功", "data": None}
