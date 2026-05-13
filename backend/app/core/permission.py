from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import casbin
from casbin_sqlalchemy_adapter import Adapter
from app.core.config import settings
from app.db.session import get_db
from app.models.system import User
from app.utils.security import decode_token
from app.utils.logger import logger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
# Casbin 权限管理
class Permission:
    _enforcer: Optional[casbin.Enforcer] = None
    @classmethod
    async def get_enforcer(cls, db: AsyncSession) -> casbin.Enforcer:
        if cls._enforcer is None:
            # 使用SQLAlchemy作为适配器
            adapter = Adapter(engine=db.bind)
            # 加载模型配置
            cls._enforcer = casbin.Enforcer("config/rbac_model.conf", adapter)
            # 加载策略
            await cls._enforcer.load_policy()
        return cls._enforcer
    @classmethod
    async def enforce(cls, db: AsyncSession, user_id: int, path: str, method: str) -> bool:
        enforcer = await cls.get_enforcer(db)
        return enforcer.enforce(str(user_id), path, method)
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = await db.get(User, int(user_id))
    if user is None or user.is_deleted or not user.is_active:
        raise credentials_exception
    return user
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
class PermissionChecker:
    def __init__(self, path: str, method: str = "GET"):
        self.path = path
        self.method = method
    async def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        # 超级管理员拥有所有权限
        if current_user.is_superuser:
            return current_user

        # 检查权限
        has_permission = await Permission.enforce(db, current_user.id, self.path, self.method)
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
