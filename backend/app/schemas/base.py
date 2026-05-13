from datetime import datetime
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
T = TypeVar("T")
class ResponseBase(GenericModel, Generic[T]):
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="返回消息")
    data: Optional[T] = Field(None, description="返回数据")
class BaseSchema(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: Optional[bool] = None
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else None
        }
class PageRequest(BaseModel):
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
class PageResponse(GenericModel, Generic[T]):
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total_page: int = Field(description="总页数")
    list: list[T] = Field(description="数据列表")
