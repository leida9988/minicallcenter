from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permission import PermissionChecker, get_current_active_user
from app.db.session import get_db
from app.models.system import User
from app.schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleQuery,
    RoleAssignPermission
)
from app.schemas.base import PageResponse, ResponseBase
from app.services.role import role_service
from app.utils.logger import logger
router = APIRouter()
@router.get("/list", response_model=ResponseBase[PageResponse[RoleResponse]], summary="获取角色列表")
async def get_role_list(
    query: RoleQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/role/list", method="GET"))
):
    """
    获取角色列表，支持分页和条件查询
    """
    filters = {}
    if query.name:
        filters["name"] = query.name
    if query.code:
        filters["code"] = query.code
    if query.status is not None:
        filters["status"] = query.status
    result = await role_service.get_multi(
        db,
        page=query.page,
        page_size=query.page_size,
        filters=filters
    )
    return ResponseBase(data=result)
@router.get("/all", response_model=ResponseBase[List[RoleResponse]], summary="获取所有角色")
async def get_all_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有启用的角色列表，用于下拉选择
    """
    result = await role_service.get_multi(db, page=1, page_size=1000, filters={"status": True})
    return ResponseBase(data=result["list"])
@router.get("/{role_id}", response_model=ResponseBase[RoleResponse], summary="获取角色详情")
async def get_role_detail(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/role/detail", method="GET"))
):
    """
    根据角色ID获取角色详情
    """
    role = await role_service.get_with_permissions(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return ResponseBase(data=role)
@router.post("/create", response_model=ResponseBase[RoleResponse], summary="创建角色")
async def create_role(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/role/create", method="POST"))
):
    """
    创建新角色
    """
    try:
        role = await role_service.create(db, obj_in=role_in)
        return ResponseBase(data=role, message="创建角色成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
@router.put("/update/{role_id}", response_model=ResponseBase[RoleResponse], summary="更新角色")
async def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/role/update", method="PUT"))
):
    """
    更新角色信息
    """
    role = await role_service.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    try:
        role = await role_service.update(db, db_obj=role, obj_in=role_in)
        return ResponseBase(data=role, message="更新角色成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
@router.delete("/delete/{role_id}", response_model=ResponseBase, summary="删除角色")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/role/delete", method="DELETE"))
):
    """
    删除角色（软删除）
    """
    role = await role_service.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    # 检查是否有用户使用该角色
    # TODO: 实现检查逻辑
    await role_service.remove(db, id=role_id)
    logger.info(f"删除角色成功: {role.name}")
    return ResponseBase(message="删除角色成功")
@router.get("/permissions/{role_id}", response_model=ResponseBase[List[int]], summary="获取角色权限ID列表")
async def get_role_permissions(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/role/permissions", method="GET"))
):
    """
    获取角色的权限ID列表
    """
    permissions = await role_service.get_permission_ids(db, role_id=role_id)
    return ResponseBase(data=permissions)
@router.post("/assign-permissions", response_model=ResponseBase, summary="分配角色权限")
async def assign_role_permissions(
    assign_in: RoleAssignPermission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/role/assign-permissions", method="POST"))
):
    """
    为角色分配权限
    """
    try:
        await role_service.assign_permissions(
            db,
            role_id=assign_in.role_id,
            permission_ids=assign_in.permission_ids
        )
        return ResponseBase(message="分配权限成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
