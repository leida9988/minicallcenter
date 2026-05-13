from app.db.session import Base, engine, AsyncSessionLocal, get_db
from app.db.base import BaseModel
# 导入所有模型，方便alembic自动检测
from app.models.system import *
from app.models.customer import *
from app.models.call import *
from app.models.ai import *
__all__ = [
    "Base",
    "engine",
    "AsyncSessionLocal",
    "get_db",
    "BaseModel",
]
