from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declared_attr
from app.db.session import Base
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    is_deleted = Column(Boolean, default=False, comment="是否删除")
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    def to_dict(self, exclude: list = None) -> dict:
        exclude = exclude or []
        data = {}
        for column in self.__table__.columns:
            if column.name in exclude:
                continue
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            data[column.name] = value
        return data
