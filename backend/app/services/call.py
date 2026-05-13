from typing import Any, Dict, Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.call import (
    CallRecord, CallTask, CallScript, CallScriptCategory,
    CallerNumber, SkillGroup, BlackList, IVRConfig
)
from app.schemas.call import (
    CallRecordCreate, CallTaskCreate, CallScriptCreate,
    CallScriptCategoryCreate, CallerNumberCreate, SkillGroupCreate,
    BlackListCreate, IVRConfigCreate
)
from app.services.base import CRUDBase
from app.utils.logger import logger
import ESL
import asyncio
class FreeSWITCHService:
    """
    FreeSWITCH对接服务
    """
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password
        self.connection: Optional[ESL.ESLconnection] = None
    async def connect(self) -> bool:
        """
        连接FreeSWITCH
        """
        try:
            loop = asyncio.get_event_loop()
            self.connection = await loop.run_in_executor(
                None,
                ESL.ESLconnection,
                self.host,
                str(self.port),
                self.password
            )
            if self.connection.connected():
                logger.info(f"成功连接到FreeSWITCH: {self.host}:{self.port}")
                return True
            logger.error(f"连接FreeSWITCH失败: {self.host}:{self.port}")
            return False
        except Exception as e:
            logger.error(f"连接FreeSWITCH异常: {str(e)}", exc_info=True)
            return False
    def disconnect(self):
        """
        断开连接
        """
        if self.connection and self.connection.connected():
            self.connection.disconnect()
            logger.info("已断开FreeSWITCH连接")
    async def originate_call(
        self,
        caller_number: str,
        called_number: str,
        user_id: int,
        customer_id: int,
        call_id: str
    ) -> bool:
        """
        发起呼叫
        :param caller_number: 主叫号码
        :param called_number: 被叫号码
        :param user_id: 坐席用户ID
        :param customer_id: 客户ID
        :param call_id: 通话唯一ID
        :return: 是否成功发起
        """
        if not self.connection or not self.connection.connected():
            if not await self.connect():
                return False
        try:
            # 构建originate命令
            # 先呼叫坐席，坐席接听后再呼叫客户
            command = (
                f"originate {{origination_caller_id_number={caller_number},call_id={call_id},"
                f"user_id={user_id},customer_id={customer_id}}}"
                f"user/{user_id} &bridge({called_number})"
            )
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.connection.api,
                "originate",
                command
            )
            if result.getHeader("Content-Type") == "api/response" and result.getBody() == "+OK":
                logger.info(f"发起呼叫成功: {caller_number} -> {called_number}, call_id: {call_id}")
                return True
            else:
                logger.error(f"发起呼叫失败: {result.getBody()}, call_id: {call_id}")
                return False
        except Exception as e:
            logger.error(f"发起呼叫异常: {str(e)}", exc_info=True)
            return False
    async def hangup_call(self, call_id: str) -> bool:
        """
        挂断通话
        """
        if not self.connection or not self.connection.connected():
            if not await self.connect():
                return False
        try:
            command = f"uuid_kill {call_id}"
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.connection.api,
                "uuid_kill",
                call_id
            )
            return result.getBody() == "+OK"
        except Exception as e:
            logger.error(f"挂断通话异常: {str(e)}", exc_info=True)
            return False
    async def transfer_call(self, call_id: str, target_number: str) -> bool:
        """
        转接通话
        """
        if not self.connection or not self.connection.connected():
            if not await self.connect():
                return False
        try:
            command = f"uuid_transfer {call_id} {target_number} XML default"
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.connection.api,
                "uuid_transfer",
                command
            )
            return result.getBody() == "+OK"
        except Exception as e:
            logger.error(f"转接通话异常: {str(e)}", exc_info=True)
            return False
    async def get_call_status(self, call_id: str) -> Optional[Dict[str, Any]]:
        """
        获取通话状态
        """
        if not self.connection or not self.connection.connected():
            if not await self.connect():
                return None
        try:
            command = f"uuid_dump {call_id}"
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.connection.api,
                "uuid_dump",
                call_id
            )
            if result.getBody().startswith("-ERR"):
                return None
            # 解析返回结果
            status = {}
            for line in result.getBody().split("\n"):
                if ": " in line:
                    key, value = line.split(": ", 1)
                    status[key.strip()] = value.strip()
            return status
        except Exception as e:
            logger.error(f"获取通话状态异常: {str(e)}", exc_info=True)
            return None
class CRUDCallRecord(CRUDBase[CallRecord, CallRecordCreate, Any]):
    async def get_by_call_id(self, db: AsyncSession, call_id: str) -> Optional[CallRecord]:
        """
        根据通话ID获取通话记录
        """
        result = await db.execute(select(CallRecord).where(CallRecord.call_id == call_id, CallRecord.is_deleted == False))
        return result.scalar_one_or_none()
    async def get_list(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 10,
        caller: Optional[str] = None,
        called: Optional[str] = None,
        user_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        direction: Optional[int] = None,
        status: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取通话记录列表
        """
        query = select(CallRecord).where(CallRecord.is_deleted == False)
        if caller:
            query = query.where(CallRecord.caller.like(f"%{caller}%"))
        if called:
            query = query.where(CallRecord.called.like(f"%{called}%"))
        if user_id is not None:
            query = query.where(CallRecord.user_id == user_id)
        if customer_id is not None:
            query = query.where(CallRecord.customer_id == customer_id)
        if direction is not None:
            query = query.where(CallRecord.direction == direction)
        if status is not None:
            query = query.where(CallRecord.status == status)
        if start_time:
            query = query.where(CallRecord.start_time >= start_time)
        if end_time:
            query = query.where(CallRecord.start_time <= end_time)
        if min_duration is not None:
            query = query.where(CallRecord.duration >= min_duration)
        if max_duration is not None:
            query = query.where(CallRecord.duration <= max_duration)
        # 统计总数
        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()
        # 分页查询
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(CallRecord.start_time.desc())
        result = await db.execute(query)
        items = result.scalars().all()
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_page": (total + page_size - 1) // page_size if total > 0 else 0,
            "list": items
        }
    async def create_record(self, db: AsyncSession, obj_in: CallRecordCreate) -> CallRecord:
        """
        创建通话记录
        """
        db_obj = CallRecord(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    async def update_call_status(
        self,
        db: AsyncSession,
        call_id: str,
        status: int,
        **kwargs
    ) -> Optional[CallRecord]:
        """
        更新通话状态
        """
        record = await self.get_by_call_id(db, call_id=call_id)
        if not record:
            return None
        record.status = status
        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record
class CRUDCallTask(CRUDBase[CallTask, CallTaskCreate, Any]):
    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> List[CallTask]:
        """
        获取用户的呼叫任务
        """
        result = await db.execute(
            select(CallTask)
            .where(CallTask.user_id == user_id, CallTask.is_deleted == False)
            .order_by(CallTask.created_at.desc())
        )
        return result.scalars().all()
    async def update_task_progress(
        self,
        db: AsyncSession,
        task_id: int,
        completed: int = 0,
        success: int = 0,
        failed: int = 0
    ) -> Optional[CallTask]:
        """
        更新任务进度
        """
        task = await self.get(db, id=task_id)
        if not task:
            return None
        task.completed_count += completed
        task.success_count += success
        task.failed_count += failed
        # 检查是否完成
        if task.completed_count >= task.total_count:
            task.status = 4  # 已完成
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
class CRUDCallScript(CRUDBase[CallScript, CallScriptCreate, Any]):
    async def get_by_category_id(self, db: AsyncSession, category_id: int) -> List[CallScript]:
        """
        获取分类下的话术
        """
        result = await db.execute(
            select(CallScript)
            .where(
                CallScript.category_id == category_id,
                CallScript.status == True,
                CallScript.is_deleted == False
            )
            .order_by(CallScript.sort.asc())
        )
        return result.scalars().all()
    async def increment_usage(self, db: AsyncSession, script_id: int, success: bool = True):
        """
        增加使用次数
        """
        script = await self.get(db, id=script_id)
        if script:
            script.usage_count += 1
            if success:
                script.success_rate = int((script.success_rate * (script.usage_count - 1) + 100) / script.usage_count)
            else:
                script.success_rate = int((script.success_rate * (script.usage_count - 1)) / script.usage_count)
            db.add(script)
            await db.commit()
class CRUDCallScriptCategory(CRUDBase[CallScriptCategory, CallScriptCategoryCreate, Any]):
    async def get_all(self, db: AsyncSession) -> List[CallScriptCategory]:
        """
        获取所有话术分类
        """
        result = await db.execute(
            select(CallScriptCategory)
            .where(CallScriptCategory.status == True, CallScriptCategory.is_deleted == False)
            .order_by(CallScriptCategory.sort.asc())
        )
        return result.scalars().all()
class CRUDCallerNumber(CRUDBase[CallerNumber, CallerNumberCreate, Any]):
    async def get_available(self, db: AsyncSession) -> List[CallerNumber]:
        """
        获取可用的主叫号码
        """
        result = await db.execute(
            select(CallerNumber)
            .where(CallerNumber.status == True, CallerNumber.is_deleted == False)
            .order_by(CallerNumber.sort.asc())
        )
        return result.scalars().all()
    async def get_random_available(self, db: AsyncSession) -> Optional[CallerNumber]:
        """
        随机获取一个可用的主叫号码
        """
        result = await db.execute(
            select(CallerNumber)
            .where(
                CallerNumber.status == True,
                CallerNumber.is_deleted == False,
                CallerNumber.current_concurrent < CallerNumber.max_concurrent
            )
            .order_by(func.rand())
            .limit(1)
        )
        return result.scalar_one_or_none()
class CRUDSkillGroup(CRUDBase[SkillGroup, SkillGroupCreate, Any]):
    async def get_all(self, db: AsyncSession) -> List[SkillGroup]:
        """
        获取所有技能组
        """
        result = await db.execute(
            select(SkillGroup)
            .where(SkillGroup.status == True, SkillGroup.is_deleted == False)
            .order_by(SkillGroup.sort.asc())
        )
        return result.scalars().all()
class CRUDBlackList(CRUDBase[BlackList, BlackListCreate, Any]):
    async def exists_by_phone(self, db: AsyncSession, phone: str) -> bool:
        """
        检查号码是否在黑名单中
        """
        result = await db.execute(select(BlackList).where(BlackList.phone == phone, BlackList.is_deleted == False))
        return result.scalar_one_or_none() is not None
class CRUDIVRConfig(CRUDBase[IVRConfig, IVRConfigCreate, Any]):
    async def get_by_number(self, db: AsyncSession, number: str) -> Optional[IVRConfig]:
        """
        根据接入号码获取IVR配置
        """
        result = await db.execute(select(IVRConfig).where(IVRConfig.number == number, IVRConfig.status == True, IVRConfig.is_deleted == False))
        return result.scalar_one_or_none()
# 初始化FreeSWITCH服务
from app.core.config import settings
freeswitch_service = FreeSWITCHService(
    host=settings.FS_HOST,
    port=settings.FS_PORT,
    password=settings.FS_PASSWORD
)
call_record_service = CRUDCallRecord(CallRecord)
call_task_service = CRUDCallTask(CallTask)
call_script_service = CRUDCallScript(CallScript)
call_script_category_service = CRUDCallScriptCategory(CallScriptCategory)
caller_number_service = CRUDCallerNumber(CallerNumber)
skill_group_service = CRUDSkillGroup(SkillGroup)
black_list_service = CRUDBlackList(BlackList)
ivr_config_service = CRUDIVRConfig(IVRConfig)
