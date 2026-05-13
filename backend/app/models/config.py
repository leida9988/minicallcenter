from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.sql import func
from .base import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    config_key = Column(String(100), unique=True, index=True, nullable=False, comment="配置键")
    config_value = Column(Text, nullable=False, comment="配置值")
    description = Column(String(255), comment="配置描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    @classmethod
    async def get_by_key(cls, db: AsyncSession, config_key: str):
        """根据键名获取配置"""
        result = await db.execute(select(cls).filter(cls.config_key == config_key))
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, db: AsyncSession):
        """获取所有配置"""
        result = await db.execute(select(cls))
        return result.scalars().all()

    async def save(self, db: AsyncSession):
        """保存配置"""
        db.add(self)
        await db.commit()
        await db.refresh(self)

    async def delete(self, db: AsyncSession):
        """删除配置"""
        await db.delete(self)
        await db.commit()
