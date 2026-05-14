from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.schemas.auth import TokenPayload
# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建访问令牌
    :param subject: 令牌主题，通常是用户ID
    :param expires_delta: 过期时间
    :return: JWT令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    :param plain_password: 明文密码
    :param hashed_password: 哈希密码
    :return: 是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password: str) -> str:
    """
    获取密码哈希
    :param password: 明文密码
    :return: 哈希密码
    """
    return pwd_context.hash(password)
def verify_token(token: str) -> Optional[TokenPayload]:
    """
    验证令牌
    :param token: JWT令牌
    :return: 令牌 payload
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(sub=payload.get("sub"))
        return token_data
    except JWTError:
        return None
