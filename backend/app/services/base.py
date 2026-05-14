from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import BaseModel
ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD对象，包含基础的增删改查操作
        :param model: SQLAlchemy模型类
        """
        self.model = model
    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        根据ID获取单条记录
        :param db: 数据库会话
        :param id: 记录ID
        :return: 记录对象
        """
        result = await db.execute(select(self.model).where(self.model.id == id, self.model.is_deleted == False))
        return result.scalar_one_or_none()
    async def get_multi(
        self, db: AsyncSession, *, page: int = 1, page_size: int = 10, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        分页获取多条记录
        :param db: 数据库会话
        :param page: 页码
        :param page_size: 每页数量
        :param filters: 过滤条件字典
        :return: 分页结果字典，包含total和list
        """
        query = select(self.model).where(self.model.is_deleted == False)
        # 应用过滤条件
        if filters:
            for key, value in filters.items():
                if value is not None:
                    if isinstance(value, str):
                        query = query.where(getattr(self.model, key).like(f"%{value}%"))
                    else:
                        query = query.where(getattr(self.model, key) == value)
        # 查询总数
        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()
        # 分页查询
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(self.model.id.desc())
        result = await db.execute(query)
        items = result.scalars().all()
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_page": (total + page_size - 1) // page_size if total > 0 else 0,
            "items": items
        }
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        创建新记录
        :param db: 数据库会话
        :param obj_in: 创建参数
        :return: 创建后的记录对象
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        更新记录
        :param db: 数据库会话
        :param db_obj: 数据库中的记录对象
        :param obj_in: 更新参数
        :return: 更新后的记录对象
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    async def remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        """
        删除记录（软删除）
        :param db: 数据库会话
        :param id: 记录ID
        :return: 删除后的记录对象
        """
        db_obj = await self.get(db, id=id)
        if db_obj:
            db_obj.is_deleted = True
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
        return db_obj
    async def hard_remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        """
        硬删除记录（物理删除）
        :param db: 数据库会话
        :param id: 记录ID
        :return: 删除后的记录对象
        """
        db_obj = await self.get(db, id=id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj
    async def count(self, db: AsyncSession, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        统计记录数量
        :param db: 数据库会话
        :param filters: 过滤条件字典
        :return: 记录数量
        """
        query = select(func.count(self.model.id)).where(self.model.is_deleted == False)
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.where(getattr(self.model, key) == value)
        result = await db.execute(query)
        return result.scalar_one()
