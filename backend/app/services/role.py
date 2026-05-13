from typing import Any, Dict, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models.system import Role, RolePermission, Permission
from app.schemas.role import RoleCreate, RoleUpdate
from app.services.base import CRUDBase
from app.utils.logger import logger
class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Role]:
        """
        根据角色编码获取角色
        """
        result = await db.execute(select(Role).where(Role.code == code, Role.is_deleted == False))
        return result.scalar_one_or_none()
    async def get_with_permissions(self, db: AsyncSession, role_id: int) -> Optional[Role]:
        """
        获取角色及其权限
        """
        result = await db.execute(
            select(Role)
            .options(joinedload(Role.permissions))
            .where(Role.id == role_id, Role.is_deleted == False)
        )
        return result.scalar_one_or_none()
    async def create(self, db: AsyncSession, *, obj_in: RoleCreate) -> Role:
        """
        创建角色
        """
        # 检查角色编码是否存在
        existing_role = await self.get_by_code(db, code=obj_in.code)
        if existing_role:
            raise ValueError(f"角色编码 {obj_in.code} 已存在")
        # 创建角色
        db_obj = Role(
            name=obj_in.name,
            code=obj_in.code,
            description=obj_in.description,
            sort=obj_in.sort,
            status=obj_in.status,
            data_scope=obj_in.data_scope,
        )
        db.add(db_obj)
        await db.flush()
        # 分配权限
        if obj_in.permission_ids:
            for permission_id in obj_in.permission_ids:
                role_permission = RolePermission(role_id=db_obj.id, permission_id=permission_id)
                db.add(role_permission)
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"创建角色成功: {db_obj.name}")
        return db_obj
    async def update(self, db: AsyncSession, *, db_obj: Role, obj_in: RoleUpdate) -> Role:
        """
        更新角色
        """
        # 检查角色编码是否重复
        if obj_in.code and obj_in.code != db_obj.code:
            existing_role = await self.get_by_code(db, code=obj_in.code)
            if existing_role:
                raise ValueError(f"角色编码 {obj_in.code} 已存在")
        # 更新角色基本信息
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            if field != "permission_ids" and hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.flush()
        # 更新权限分配
        if "permission_ids" in update_data and update_data["permission_ids"] is not None:
            # 删除原有权限
            await db.execute(
                RolePermission.__table__.delete().where(RolePermission.role_id == db_obj.id)
            )
            # 添加新权限
            for permission_id in update_data["permission_ids"]:
                role_permission = RolePermission(role_id=db_obj.id, permission_id=permission_id)
                db.add(role_permission)
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"更新角色成功: {db_obj.name}")
        return db_obj
    async def assign_permissions(self, db: AsyncSession, *, role_id: int, permission_ids: List[int]) -> Role:
        """
        分配角色权限
        """
        role = await self.get(db, id=role_id)
        if not role:
            raise ValueError(f"角色ID {role_id} 不存在")
        # 删除原有权限
        await db.execute(
            RolePermission.__table__.delete().where(RolePermission.role_id == role_id)
        )
        # 添加新权限
        for permission_id in permission_ids:
            role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
            db.add(role_permission)
        await db.commit()
        await db.refresh(role)
        logger.info(f"分配角色权限成功: {role.name}")
        return role
    async def get_permission_ids(self, db: AsyncSession, role_id: int) -> List[int]:
        """
        获取角色的权限ID列表
        """
        result = await db.execute(
            select(RolePermission.permission_id)
            .where(RolePermission.role_id == role_id)
        )
        return [row[0] for row in result.all()]
role_service = CRUDRole(Role)
