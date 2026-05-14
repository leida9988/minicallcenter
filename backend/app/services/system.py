from typing import Any, Dict, Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.system import SystemConfig, OperationLog
from app.services.base import CRUDBase
from app.schemas.system import SystemConfigCreate, SystemConfigUpdate
from app.utils.logger import logger
class CRUDSystemConfig(CRUDBase[SystemConfig, SystemConfigCreate, SystemConfigUpdate]):
    async def get_by_key(self, db: AsyncSession, key: str, default: Any = None) -> Optional[str]:
        """
        根据配置键获取配置值
        """
        result = await db.execute(select(SystemConfig).where(SystemConfig.key == key, SystemConfig.is_deleted == False))
        config = result.scalar_one_or_none()
        return config.value if config else default
    async def get_all(self, db: AsyncSession, is_public: Optional[bool] = None) -> Dict[str, str]:
        """
        获取所有配置
        """
        query = select(SystemConfig).where(SystemConfig.is_deleted == False)
        if is_public is not None:
            query = query.where(SystemConfig.is_public == is_public)
        result = await db.execute(query)
        configs = result.scalars().all()
        return {config.key: config.value for config in configs}
    async def set_value(self, db: AsyncSession, key: str, value: str, description: str = "") -> SystemConfig:
        """
        设置配置值
        """
        config = await self.get_by_key(db, key)
        if config:
            config.value = value
            if description:
                config.description = description
            await db.commit()
            await db.refresh(config)
            logger.info(f"更新系统配置: {key} = {value}")
        else:
            config = SystemConfig(
                key=key,
                value=value,
                name=key,
                description=description,
                type=2,  # 业务配置
                is_public=False
            )
            db.add(config)
            await db.commit()
            await db.refresh(config)
            logger.info(f"创建系统配置: {key} = {value}")
        return config
    async def batch_set(self, db: AsyncSession, configs: Dict[str, str]) -> None:
        """
        批量设置配置
        """
        for key, value in configs.items():
            await self.set_value(db, key, value)
class CRUDOperationLog(CRUDBase[OperationLog, Any, Any]):
    async def get_list(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 10,
        user_id: Optional[int] = None,
        module: Optional[str] = None,
        operation: Optional[str] = None,
        status: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取操作日志列表
        """
        query = select(OperationLog).where(OperationLog.is_deleted == False)
        if user_id:
            query = query.where(OperationLog.user_id == user_id)
        if module:
            query = query.where(OperationLog.module.like(f"%{module}%"))
        if operation:
            query = query.where(OperationLog.operation.like(f"%{operation}%"))
        if status is not None:
            query = query.where(OperationLog.status == status)
        if start_time:
            query = query.where(OperationLog.created_at >= start_time)
        if end_time:
            query = query.where(OperationLog.created_at <= end_time)
        # 统计总数
        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()
        # 分页查询
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(OperationLog.created_at.desc())
        result = await db.execute(query)
        items = result.scalars().all()
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_page": (total + page_size - 1) // page_size if total > 0 else 0,
            "items": items
        }
system_config_service = CRUDSystemConfig(SystemConfig)
operation_log_service = CRUDOperationLog(OperationLog)
