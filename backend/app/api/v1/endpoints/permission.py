from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permission import PermissionChecker, get_current_active_user
from app.db.session import get_db
from app.models.system import User
from app.schemas.permission import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    PermissionQuery,
    PermissionTreeResponse
)
from app.schemas.base import PageResponse, ResponseBase
from app.services.permission import permission_service
from app.utils.logger import logger
router = APIRouter()
@router.get("/tree", response_model=ResponseBase[List[PermissionTreeResponse]], summary="获取权限树")
async def get_permission_tree(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户的权限菜单树
    """
    tree = await permission_service.get_menu_tree(
        db,
        user_id=current_user.id,
        is_superuser=current_user.is_superuser
    )
    return ResponseBase(data=tree)
@router.get("/all-tree", response_model=ResponseBase[List[PermissionTreeResponse]], summary="获取完整权限树")
async def get_all_permission_tree(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/permission/all-tree", method="GET"))
):
    """
    获取完整的权限树，用于权限分配
    """
    # 获取所有权限
    result = await permission_service.get_multi(db, page=1, page_size=1000)
    all_permissions = result["list"]
    # 构建树形结构
    tree = permission_service._build_tree(all_permissions, parent_id=0)
    return ResponseBase(data=tree)
@router.get("/list", response_model=ResponseBase[PageResponse[PermissionResponse]], summary="获取权限列表")
async def get_permission_list(
    query: PermissionQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/permission/list", method="GET"))
):
    """
    获取权限列表，支持分页和条件查询
    """
    filters = {}
    if query.name:
        filters["name"] = query.name
    if query.code:
        filters["code"] = query.code
    if query.type is not None:
        filters["type"] = query.type
    if query.status is not None:
        filters["status"] = query.status
    if query.parent_id is not None:
        filters["parent_id"] = query.parent_id
    result = await permission_service.get_multi(
        db,
        page=query.page,
        page_size=query.page_size,
        filters=filters
    )
    return ResponseBase(data=result)
@router.get("/{permission_id}", response_model=ResponseBase[PermissionResponse], summary="获取权限详情")
async def get_permission_detail(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/permission/detail", method="GET"))
):
    """
    根据权限ID获取权限详情
    """
    permission = await permission_service.get(db, id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    return ResponseBase(data=permission)
@router.post("/create", response_model=ResponseBase[PermissionResponse], summary="创建权限")
async def create_permission(
    permission_in: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/permission/create", method="POST"))
):
    """
    创建新权限
    """
    # 检查权限编码是否存在
    existing_permission = await permission_service.get_by_code(db, code=permission_in.code)
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"权限编码 {permission_in.code} 已存在"
        )
    permission = await permission_service.create(db, obj_in=permission_in)
    logger.info(f"创建权限成功: {permission.name}")
    return ResponseBase(data=permission, message="创建权限成功")
@router.put("/update/{permission_id}", response_model=ResponseBase[PermissionResponse], summary="更新权限")
async def update_permission(
    permission_id: int,
    permission_in: PermissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/permission/update", method="PUT"))
):
    """
    更新权限信息
    """
    permission = await permission_service.get(db, id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    # 检查权限编码是否重复
    if permission_in.code and permission_in.code != permission.code:
        existing_permission = await permission_service.get_by_code(db, code=permission_in.code)
        if existing_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"权限编码 {permission_in.code} 已存在"
            )
    permission = await permission_service.update(db, db_obj=permission, obj_in=permission_in)
    logger.info(f"更新权限成功: {permission.name}")
    return ResponseBase(data=permission, message="更新权限成功")
@router.delete("/delete/{permission_id}", response_model=ResponseBase, summary="删除权限")
async def delete_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/permission/delete", method="DELETE"))
):
    """
    删除权限（软删除）
    """
    permission = await permission_service.get(db, id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    # 检查是否有子权限
    children = await permission_service.get_by_parent_id(db, parent_id=permission_id)
    if children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先删除子权限"
        )
    # 检查是否有角色使用该权限
    # TODO: 实现检查逻辑
    await permission_service.remove(db, id=permission_id)
    logger.info(f"删除权限成功: {permission.name}")
    return ResponseBase(message="删除权限成功")
@router.get("/codes/me", response_model=ResponseBase[List[str]], summary="获取当前用户的权限编码列表")
async def get_current_user_permission_codes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户的权限编码列表，用于前端权限控制
    """
    codes = await permission_service.get_permission_codes(
        db,
        user_id=current_user.id,
        is_superuser=current_user.is_superuser
    )
    return ResponseBase(data=codes)
