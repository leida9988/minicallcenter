from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema, PageRequest
class PermissionBase(BaseSchema):
    name: str = Field(description="权限名称")
    code: str = Field(description="权限编码")
    type: Optional[int] = Field(1, description="权限类型：1-菜单 2-按钮 3-接口")
    parent_id: Optional[int] = Field(0, description="父权限ID")
    path: Optional[str] = Field(None, description="路由路径")
    component: Optional[str] = Field(None, description="组件路径")
    icon: Optional[str] = Field(None, description="图标")
    sort: Optional[int] = Field(0, description="排序")
    status: Optional[bool] = Field(True, description="状态")
    visible: Optional[bool] = Field(True, description="是否可见")
class PermissionCreate(PermissionBase):
    pass
class PermissionUpdate(PermissionBase):
    pass
class PermissionResponse(PermissionBase):
    children: Optional[List["PermissionResponse"]] = Field(None, description="子权限列表")
class PermissionQuery(PageRequest):
    name: Optional[str] = Field(None, description="权限名称")
    code: Optional[str] = Field(None, description="权限编码")
    type: Optional[int] = Field(None, description="权限类型")
    status: Optional[bool] = Field(None, description="状态")
    parent_id: Optional[int] = Field(None, description="父权限ID")
class PermissionTreeResponse(BaseModel):
    id: int = Field(description="权限ID")
    name: str = Field(description="权限名称")
    type: int = Field(description="权限类型")
    path: Optional[str] = Field(None, description="路由路径")
    component: Optional[str] = Field(None, description="组件路径")
    icon: Optional[str] = Field(None, description="图标")
    sort: int = Field(description="排序")
    visible: bool = Field(description="是否可见")
    children: Optional[List["PermissionTreeResponse"]] = Field(None, description="子权限列表")
# 解决循环引用
PermissionResponse.model_rebuild()
PermissionTreeResponse.model_rebuild()
