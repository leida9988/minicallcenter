from typing import Any, Dict, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.system import Permission, RolePermission, Role, UserRole
from app.services.base import CRUDBase
from app.schemas.permission import PermissionCreate, PermissionUpdate
from app.utils.logger import logger
class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Permission]:
        """
        根据权限编码获取权限
        """
        result = await db.execute(select(Permission).where(Permission.code == code, Permission.is_deleted == False))
        return result.scalar_one_or_none()
    async def get_by_parent_id(self, db: AsyncSession, parent_id: int = 0) -> List[Permission]:
        """
        根据父ID获取子权限列表
        """
        result = await db.execute(
            select(Permission)
            .where(Permission.parent_id == parent_id, Permission.is_deleted == False)
            .order_by(Permission.sort)
        )
        return result.scalars().all()
    async def get_menu_tree(self, db: AsyncSession, user_id: int, is_superuser: bool = False) -> List[Dict[str, Any]]:
        """
        获取用户的菜单树
        """
        if is_superuser:
            # 超级管理员获取所有菜单
            result = await db.execute(
                select(Permission)
                .where(Permission.type.in_([1, 2]), Permission.status == True, Permission.is_deleted == False)
                .order_by(Permission.sort)
            )
            permissions = result.scalars().all()
        else:
            # 普通用户根据角色获取权限
            result = await db.execute(
                select(Permission)
                .distinct()
                .join(RolePermission, Permission.id == RolePermission.permission_id)
                .join(Role, Role.id == RolePermission.role_id)
                .join(UserRole, Role.id == UserRole.role_id)
                .where(
                    UserRole.user_id == user_id,
                    Permission.type.in_([1, 2]),
                    Permission.status == True,
                    Permission.is_deleted == False,
                    Role.status == True,
                    Role.is_deleted == False
                )
                .order_by(Permission.sort)
            )
            permissions = result.scalars().all()
        # 构建树形结构
        return self._build_tree(permissions, parent_id=0)
    async def get_permission_codes(self, db: AsyncSession, user_id: int, is_superuser: bool = False) -> List[str]:
        """
        获取用户的权限编码列表
        """
        if is_superuser:
            return ["*"]  # 超级管理员拥有所有权限
        result = await db.execute(
            select(Permission.code)
            .distinct()
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(
                UserRole.user_id == user_id,
                Permission.type == 3,  # 接口权限
                Permission.status == True,
                Permission.is_deleted == False,
                Role.status == True,
                Role.is_deleted == False
            )
        )
        return [row[0] for row in result.all()]
    def _build_tree(self, permissions: List[Permission], parent_id: int = 0) -> List[Dict[str, Any]]:
        """
        构建权限树形结构
        """
        tree = []
        for perm in permissions:
            if perm.parent_id == parent_id:
                perm_dict = {
                    "id": perm.id,
                    "name": perm.name,
                    "code": perm.code,
                    "type": perm.type,
                    "path": perm.path,
                    "component": perm.component,
                    "icon": perm.icon,
                    "sort": perm.sort,
                    "visible": perm.visible,
                    "children": self._build_tree(permissions, parent_id=perm.id)
                }
                tree.append(perm_dict)
        return tree
permission_service = CRUDPermission(Permission)
