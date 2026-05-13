from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from app.schemas.base import BaseSchema, PageRequest
class UserBase(BaseSchema):
    username: str = Field(description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    avatar: Optional[str] = Field(None, description="头像")
    is_active: Optional[bool] = Field(True, description="是否激活")
    is_superuser: Optional[bool] = Field(False, description="是否超级管理员")
    department_id: Optional[int] = Field(None, description="部门ID")
class UserCreate(UserBase):
    password: str = Field(description="密码", min_length=6, max_length=20)
    role_ids: Optional[List[int]] = Field(None, description="角色ID列表")
class UserUpdate(UserBase):
    password: Optional[str] = Field(None, description="密码", min_length=6, max_length=20)
    role_ids: Optional[List[int]] = Field(None, description="角色ID列表")
class UserResponse(UserBase):
    department_name: Optional[str] = Field(None, description="部门名称")
    role_names: Optional[List[str]] = Field(None, description="角色名称列表")
    last_login_at: Optional[str] = Field(None, description="最后登录时间")
    last_login_ip: Optional[str] = Field(None, description="最后登录IP")
class UserQuery(PageRequest):
    username: Optional[str] = Field(None, description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    is_active: Optional[bool] = Field(None, description="是否激活")
    department_id: Optional[int] = Field(None, description="部门ID")
class UserResetPassword(BaseModel):
    old_password: str = Field(description="旧密码", min_length=6, max_length=20)
    new_password: str = Field(description="新密码", min_length=6, max_length=20)
class UserUpdateProfile(BaseModel):
    nickname: Optional[str] = Field(None, description="昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    avatar: Optional[str] = Field(None, description="头像")
