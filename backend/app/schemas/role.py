from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema, PageRequest
class RoleBase(BaseSchema):
    name: str = Field(description="角色名称")
    code: str = Field(description="角色编码")
    description: Optional[str] = Field(None, description="角色描述")
    sort: Optional[int] = Field(0, description="排序")
    status: Optional[bool] = Field(True, description="状态")
    data_scope: Optional[int] = Field(1, description="数据范围：1-全部数据 2-部门及以下数据 3-本部门数据 4-仅本人数据")
class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = Field(None, description="权限ID列表")
class RoleUpdate(RoleBase):
    permission_ids: Optional[List[int]] = Field(None, description="权限ID列表")
class RoleResponse(RoleBase):
    permission_names: Optional[List[str]] = Field(None, description="权限名称列表")
class RoleQuery(PageRequest):
    name: Optional[str] = Field(None, description="角色名称")
    code: Optional[str] = Field(None, description="角色编码")
    status: Optional[bool] = Field(None, description="状态")
class RoleAssignPermission(BaseModel):
    role_id: int = Field(description="角色ID")
    permission_ids: List[int] = Field(description="权限ID列表")
