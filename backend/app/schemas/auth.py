from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema
class LoginResponse(BaseSchema):
    username: str = Field(description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    avatar: Optional[str] = Field(None, description="头像")
    is_active: bool = Field(description="是否激活")
    is_superuser: bool = Field(description="是否超级管理员")
class Token(BaseModel):
    access_token: str = Field(description="访问令牌")
    token_type: str = Field(description="令牌类型")
    expires_in: int = Field(description="过期时间(秒)")
    user: LoginResponse = Field(description="用户信息")
class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None
