from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.base import BaseModel
class User(BaseModel):
    __tablename__ = "system_user"
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    nickname = Column(String(50), comment="昵称")
    email = Column(String(100), comment="邮箱")
    phone = Column(String(20), comment="手机号")
    avatar = Column(String(255), comment="头像")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_superuser = Column(Boolean, default=False, comment="是否超级管理员")
    department_id = Column(Integer, ForeignKey("system_department.id"), comment="部门ID")
    last_login_at = Column(DateTime, comment="最后登录时间")
    last_login_ip = Column(String(50), comment="最后登录IP")
    # 关联
    department = relationship("Department", back_populates="users")
    roles = relationship("Role", secondary="system_user_role", back_populates="users")
    @classmethod
    async def get_by_username(cls, db: AsyncSession, username: str):
        result = await db.execute(select(cls).where(cls.username == username, cls.is_deleted == False))
        return result.scalar_one_or_none()
    @classmethod
    async def get_by_phone(cls, db: AsyncSession, phone: str):
        result = await db.execute(select(cls).where(cls.phone == phone, cls.is_deleted == False))
        return result.scalar_one_or_none()
class Department(BaseModel):
    __tablename__ = "system_department"
    name = Column(String(100), nullable=False, comment="部门名称")
    parent_id = Column(Integer, default=0, comment="父部门ID")
    sort = Column(Integer, default=0, comment="排序")
    leader = Column(String(50), comment="负责人")
    phone = Column(String(20), comment="联系电话")
    email = Column(String(100), comment="邮箱")
    status = Column(Boolean, default=True, comment="状态")
    # 关联
    users = relationship("User", back_populates="department")
class Role(BaseModel):
    __tablename__ = "system_role"
    name = Column(String(50), nullable=False, comment="角色名称")
    code = Column(String(50), unique=True, nullable=False, comment="角色编码")
    description = Column(String(255), comment="角色描述")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(Boolean, default=True, comment="状态")
    data_scope = Column(Integer, default=1, comment="数据范围：1-全部数据 2-部门及以下数据 3-本部门数据 4-仅本人数据")
    # 关联
    users = relationship("User", secondary="system_user_role", back_populates="roles")
    permissions = relationship("Permission", secondary="system_role_permission", back_populates="roles")
class UserRole(BaseModel):
    __tablename__ = "system_user_role"
    user_id = Column(Integer, ForeignKey("system_user.id"), nullable=False, comment="用户ID")
    role_id = Column(Integer, ForeignKey("system_role.id"), nullable=False, comment="角色ID")
class Permission(BaseModel):
    __tablename__ = "system_permission"
    name = Column(String(50), nullable=False, comment="权限名称")
    code = Column(String(100), unique=True, nullable=False, comment="权限编码")
    type = Column(Integer, default=1, comment="权限类型：1-菜单 2-按钮 3-接口")
    parent_id = Column(Integer, default=0, comment="父权限ID")
    path = Column(String(255), comment="路由路径")
    component = Column(String(255), comment="组件路径")
    icon = Column(String(50), comment="图标")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(Boolean, default=True, comment="状态")
    visible = Column(Boolean, default=True, comment="是否可见")
    # 关联
    roles = relationship("Role", secondary="system_role_permission", back_populates="permissions")
class RolePermission(BaseModel):
    __tablename__ = "system_role_permission"
    role_id = Column(Integer, ForeignKey("system_role.id"), nullable=False, comment="角色ID")
    permission_id = Column(Integer, ForeignKey("system_permission.id"), nullable=False, comment="权限ID")
class OperationLog(BaseModel):
    __tablename__ = "system_operation_log"
    user_id = Column(Integer, comment="用户ID")
    username = Column(String(50), comment="用户名")
    module = Column(String(50), comment="模块名称")
    operation = Column(String(100), comment="操作类型")
    method = Column(String(10), comment="请求方法")
    path = Column(String(255), comment="请求路径")
    ip = Column(String(50), comment="IP地址")
    location = Column(String(100), comment="操作地点")
    user_agent = Column(String(255), comment="User Agent")
    request_params = Column(JSON, comment="请求参数")
    response_result = Column(JSON, comment="响应结果")
    status = Column(Integer, default=1, comment="操作状态：1-成功 2-失败")
    error_msg = Column(Text, comment="错误信息")
    cost_time = Column(Integer, comment="耗时(ms)")
class SystemConfig(BaseModel):
    __tablename__ = "system_config"
    key = Column(String(100), unique=True, index=True, nullable=False, comment="配置键")
    value = Column(Text, comment="配置值")
    name = Column(String(100), comment="配置名称")
    description = Column(String(255), comment="配置描述")
    type = Column(Integer, default=1, comment="配置类型：1-系统配置 2-业务配置")
    sort = Column(Integer, default=0, comment="排序")
    is_public = Column(Boolean, default=False, comment="是否公开")
    @classmethod
    async def get_by_key(cls, db: AsyncSession, key: str, default=None):
        result = await db.execute(select(cls).where(cls.key == key, cls.is_deleted == False))
        config = result.scalar_one_or_none()
        return config.value if config else default
    @classmethod
    async def set_value(cls, db: AsyncSession, key: str, value: str):
        config = await cls.get_by_key(db, key)
        if config:
            config.value = value
            await db.commit()
            await db.refresh(config)
        return config
