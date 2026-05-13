from typing import Any, Dict, Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models.customer import Customer, FollowRecord, Tag, PublicSeaPool, PublicSeaConfig
from app.schemas.customer import CustomerCreate, CustomerUpdate, FollowRecordCreate, TagCreate
from app.services.base import CRUDBase
from app.utils.logger import logger
class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    async def get_by_phone(self, db: AsyncSession, phone: str) -> Optional[Customer]:
        """
        根据手机号获取客户
        """
        result = await db.execute(select(Customer).where(Customer.phone == phone, Customer.is_deleted == False))
        return result.scalar_one_or_none()
    async def get_with_follow_records(self, db: AsyncSession, customer_id: int) -> Optional[Customer]:
        """
        获取客户及其跟进记录
        """
        result = await db.execute(
            select(Customer)
            .options(joinedload(Customer.follow_records).joinedload(FollowRecord.user))
            .where(Customer.id == customer_id, Customer.is_deleted == False)
        )
        return result.scalar_one_or_none()
    async def get_list(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
        level: Optional[int] = None,
        tags: Optional[List[str]] = None,
        assign_user_id: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取客户列表
        """
        query = select(Customer).where(Customer.is_deleted == False)
        if keyword:
            query = query.where(
                (Customer.name.like(f"%{keyword}%")) |
                (Customer.phone.like(f"%{keyword}%")) |
                (Customer.company.like(f"%{keyword}%"))
            )
        if status is not None:
            query = query.where(Customer.status == status)
        if level is not None:
            query = query.where(Customer.level == level)
        if tags:
            # JSON数组包含查询，这里需要根据数据库类型调整
            for tag in tags:
                query = query.where(Customer.tags.contains([tag]))
        if assign_user_id is not None:
            query = query.where(Customer.assign_user_id == assign_user_id)
        if start_time:
            query = query.where(Customer.created_at >= start_time)
        if end_time:
            query = query.where(Customer.created_at <= end_time)
        # 统计总数
        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()
        # 分页查询
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Customer.created_at.desc())
        result = await db.execute(query)
        items = result.scalars().all()
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_page": (total + page_size - 1) // page_size if total > 0 else 0,
            "list": items
        }
    async def assign_customer(
        self,
        db: AsyncSession,
        *,
        customer_id: int,
        user_id: int,
        assign_by: int
    ) -> Optional[Customer]:
        """
        分配客户给坐席
        """
        customer = await self.get(db, id=customer_id)
        if not customer:
            return None
        customer.assign_user_id = user_id
        customer.assign_time = func.now()
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        logger.info(f"分配客户 {customer.name} 给用户 {user_id}")
        return customer
    async def batch_assign(
        self,
        db: AsyncSession,
        *,
        customer_ids: List[int],
        user_id: int,
        assign_by: int
    ) -> int:
        """
        批量分配客户
        """
        count = 0
        for customer_id in customer_ids:
            customer = await self.assign_customer(db, customer_id=customer_id, user_id=user_id, assign_by=assign_by)
            if customer:
                count += 1
        return count
    async def recycle_to_public_sea(self, db: AsyncSession, customer_id: int) -> Optional[Customer]:
        """
        回收客户到公海池
        """
        customer = await self.get(db, id=customer_id)
        if not customer:
            return None
        customer.assign_user_id = None
        customer.assign_time = None
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        logger.info(f"回收客户 {customer.name} 到公海池")
        return customer
    async def update_follow_info(self, db: AsyncSession, customer_id: int, follow_duration: int = 0) -> Optional[Customer]:
        """
        更新客户跟进信息
        """
        customer = await self.get(db, id=customer_id)
        if not customer:
            return None
        customer.follow_count += 1
        customer.total_call_duration += follow_duration
        customer.last_follow_time = func.now()
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return customer
class CRUDFollowRecord(CRUDBase[FollowRecord, FollowRecordCreate, Any]):
    async def get_by_customer_id(
        self,
        db: AsyncSession,
        customer_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取客户的跟进记录
        """
        query = select(FollowRecord).where(
            FollowRecord.customer_id == customer_id,
            FollowRecord.is_deleted == False
        ).order_by(FollowRecord.follow_time.desc())
        # 统计总数
        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()
        # 分页查询
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_page": (total + page_size - 1) // page_size if total > 0 else 0,
            "list": items
        }
    async def create_record(
        self,
        db: AsyncSession,
        *,
        obj_in: FollowRecordCreate,
        user_id: int
    ) -> FollowRecord:
        """
        创建跟进记录
        """
        db_obj = FollowRecord(**obj_in.model_dump(), user_id=user_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        # 更新客户的跟进信息
        await customer_service.update_follow_info(db, customer_id=obj_in.customer_id, follow_duration=obj_in.duration or 0)
        logger.info(f"创建跟进记录: 客户ID {obj_in.customer_id}")
        return db_obj
class CRUDTag(CRUDBase[Tag, TagCreate, TagCreate]):
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Tag]:
        """
        根据标签名称获取标签
        """
        result = await db.execute(select(Tag).where(Tag.name == name, Tag.is_deleted == False))
        return result.scalar_one_or_none()
    async def get_all(self, db: AsyncSession, type: int = 1) -> List[Tag]:
        """
        获取所有标签
        """
        result = await db.execute(
            select(Tag)
            .where(Tag.type == type, Tag.is_deleted == False)
            .order_by(Tag.sort.asc())
        )
        return result.scalars().all()
    async def create_tag(self, db: AsyncSession, obj_in: TagCreate) -> Tag:
        """
        创建标签
        """
        existing_tag = await self.get_by_name(db, name=obj_in.name)
        if existing_tag:
            raise ValueError(f"标签 {obj_in.name} 已存在")
        tag = await self.create(db, obj_in=obj_in)
        logger.info(f"创建标签: {tag.name}")
        return tag
    async def increment_count(self, db: AsyncSession, tag_id: int) -> None:
        """
        增加标签使用次数
        """
        tag = await self.get(db, id=tag_id)
        if tag:
            tag.count += 1
            db.add(tag)
            await db.commit()
customer_service = CRUDCustomer(Customer)
follow_record_service = CRUDFollowRecord(FollowRecord)
tag_service = CRUDTag(Tag)
