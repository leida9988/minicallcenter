from typing import Any, Dict, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.core.security import get_password_hash
from app.models.system import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import CRUDBase
from app.utils.logger import logger
class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        """
        result = await db.execute(
            select(User)
            .options(joinedload(User.roles))
            .where(User.username == username, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    async def get_by_phone(self, db: AsyncSession, phone: str) -> Optional[User]:
        """
        根据手机号获取用户
        """
        result = await db.execute(select(User).where(User.phone == phone, User.is_deleted == False))
        return result.scalar_one_or_none()
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """
        创建用户
        """
        # 检查用户名是否存在
        existing_user = await self.get_by_username(db, username=obj_in.username)
        if existing_user:
            raise ValueError(f"用户名 {obj_in.username} 已存在")
        # 检查手机号是否存在
        if obj_in.phone:
            existing_phone = await self.get_by_phone(db, phone=obj_in.phone)
            if existing_phone:
                raise ValueError(f"手机号 {obj_in.phone} 已存在")
        # 创建用户
        db_obj = User(
            username=obj_in.username,
            password=get_password_hash(obj_in.password),
            nickname=obj_in.nickname,
            email=obj_in.email,
            phone=obj_in.phone,
            avatar=obj_in.avatar,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
            department_id=obj_in.department_id,
        )
        db.add(db_obj)
        await db.flush()
        # 分配角色
        if obj_in.role_ids:
            for role_id in obj_in.role_ids:
                user_role = UserRole(user_id=db_obj.id, role_id=role_id)
                db.add(user_role)
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"创建用户成功: {db_obj.username}")
        return db_obj
    async def update(self, db: AsyncSession, *, db_obj: User, obj_in: UserUpdate) -> User:
        """
        更新用户
        """
        # 检查用户名是否重复
        if obj_in.username and obj_in.username != db_obj.username:
            existing_user = await self.get_by_username(db, username=obj_in.username)
            if existing_user:
                raise ValueError(f"用户名 {obj_in.username} 已存在")
        # 检查手机号是否重复
        if obj_in.phone and obj_in.phone != db_obj.phone:
            existing_phone = await self.get_by_phone(db, phone=obj_in.phone)
            if existing_phone:
                raise ValueError(f"手机号 {obj_in.phone} 已存在")
        # 如果有密码，加密密码
        update_data = obj_in.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["password"] = get_password_hash(update_data["password"])
        else:
            update_data.pop("password", None)
        # 更新用户基本信息
        for field in update_data:
            if field != "role_ids" and hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.flush()
        # 更新角色分配
        if "role_ids" in update_data and update_data["role_ids"] is not None:
            # 删除原有角色
            await db.execute(
                UserRole.__table__.delete().where(UserRole.user_id == db_obj.id)
            )
            # 添加新角色
            for role_id in update_data["role_ids"]:
                user_role = UserRole(user_id=db_obj.id, role_id=role_id)
                db.add(user_role)
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"更新用户成功: {db_obj.username}")
        return db_obj
    async def update_password(self, db: AsyncSession, *, user: User, new_password: str) -> User:
        """
        更新用户密码
        """
        user.password = get_password_hash(new_password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"用户密码更新成功: {user.username}")
        return user
user_service = CRUDUser(User)
