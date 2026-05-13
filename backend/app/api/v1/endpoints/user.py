from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permission import PermissionChecker, get_current_active_user
from app.db.session import get_db
from app.models.system import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserQuery,
    UserResetPassword,
    UserUpdateProfile
)
from app.schemas.base import PageResponse, ResponseBase
from app.services.user import user_service
from app.utils.logger import logger
router = APIRouter()
@router.get("/list", response_model=ResponseBase[PageResponse[UserResponse]], summary="获取用户列表")
async def get_user_list(
    query: UserQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/user/list", method="GET"))
):
    """
    获取用户列表，支持分页和条件查询
    """
    filters = {}
    if query.username:
        filters["username"] = query.username
    if query.nickname:
        filters["nickname"] = query.nickname
    if query.phone:
        filters["phone"] = query.phone
    if query.email:
        filters["email"] = query.email
    if query.is_active is not None:
        filters["is_active"] = query.is_active
    if query.department_id is not None:
        filters["department_id"] = query.department_id
    result = await user_service.get_multi(
        db,
        page=query.page,
        page_size=query.page_size,
        filters=filters
    )
    return ResponseBase(data=result)
@router.get("/{user_id}", response_model=ResponseBase[UserResponse], summary="获取用户详情")
async def get_user_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/user/detail", method="GET"))
):
    """
    根据用户ID获取用户详情
    """
    user = await user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return ResponseBase(data=user)
@router.post("/create", response_model=ResponseBase[UserResponse], summary="创建用户")
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/user/create", method="POST"))
):
    """
    创建新用户
    """
    try:
        user = await user_service.create(db, obj_in=user_in)
        return ResponseBase(data=user, message="创建用户成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
@router.put("/update/{user_id}", response_model=ResponseBase[UserResponse], summary="更新用户")
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/user/update", method="PUT"))
):
    """
    更新用户信息
    """
    user = await user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    try:
        user = await user_service.update(db, db_obj=user, obj_in=user_in)
        return ResponseBase(data=user, message="更新用户成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
@router.delete("/delete/{user_id}", response_model=ResponseBase, summary="删除用户")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/user/delete", method="DELETE"))
):
    """
    删除用户（软删除）
    """
    user = await user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    if user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="超级管理员不能删除"
        )
    await user_service.remove(db, id=user_id)
    logger.info(f"删除用户成功: {user.username}")
    return ResponseBase(message="删除用户成功")
@router.post("/reset-password/{user_id}", response_model=ResponseBase, summary="重置用户密码")
async def reset_user_password(
    user_id: int,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/user/reset-password", method="POST"))
):
    """
    重置用户密码（管理员权限）
    """
    user = await user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    if len(new_password) < 6 or len(new_password) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度必须在6-20位之间"
        )
    await user_service.update_password(db, user=user, new_password=new_password)
    return ResponseBase(message="重置密码成功")
@router.get("/profile/me", response_model=ResponseBase[UserResponse], summary="获取当前用户信息")
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前登录用户的信息
    """
    return ResponseBase(data=current_user)
@router.put("/profile/update", response_model=ResponseBase[UserResponse], summary="更新当前用户信息")
async def update_current_user_profile(
    profile_in: UserUpdateProfile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新当前登录用户的个人信息
    """
    user = await user_service.update(db, db_obj=current_user, obj_in=profile_in)
    return ResponseBase(data=user, message="更新个人信息成功")
@router.put("/profile/change-password", response_model=ResponseBase, summary="修改当前用户密码")
async def change_current_user_password(
    password_in: UserResetPassword,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    修改当前登录用户的密码
    """
    from app.utils.security import verify_password
    # 验证旧密码
    if not verify_password(password_in.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    # 验证新密码长度
    if len(password_in.new_password) < 6 or len(password_in.new_password) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度必须在6-20位之间"
        )
    # 不能与旧密码相同
    if verify_password(password_in.new_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与旧密码相同"
        )
    await user_service.update_password(db, user=current_user, new_password=password_in.new_password)
    logger.info(f"用户修改密码成功: {current_user.username}")
    return ResponseBase(message="修改密码成功")
