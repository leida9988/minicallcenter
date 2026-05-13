from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.base import BaseModel
class CallRecord(BaseModel):
    __tablename__ = "call_record"
    call_id = Column(String(50), unique=True, index=True, nullable=False, comment="通话唯一ID")
    caller = Column(String(20), comment="主叫号码")
    called = Column(String(20), comment="被叫号码")
    user_id = Column(Integer, ForeignKey("system_user.id"), comment="坐席ID")
    customer_id = Column(Integer, ForeignKey("customer.id"), comment="客户ID")
    direction = Column(Integer, default=1, comment="通话方向：1-外呼 2-呼入")
    status = Column(Integer, default=1, comment="通话状态：1-呼叫中 2-已接通 3-已挂断 4-未接通 5-占线 6-无人接听 7-号码错误")
    start_time = Column(DateTime, comment="通话开始时间")
    answer_time = Column(DateTime, comment="接听时间")
    end_time = Column(DateTime, comment="通话结束时间")
    duration = Column(Integer, default=0, comment="通话时长(秒)")
    ring_duration = Column(Integer, default=0, comment="振铃时长(秒)")
    wait_duration = Column(Integer, default=0, comment="等待时长(秒)")
    recording_url = Column(String(255), comment="录音文件URL")
    recording_path = Column(String(255), comment="录音文件路径")
    recording_duration = Column(Integer, default=0, comment="录音时长(秒)")
    sip_code = Column(String(10), comment="SIP响应码")
    sip_reason = Column(String(100), comment="SIP响应原因")
    hangup_cause = Column(String(50), comment="挂断原因")
    hangup_side = Column(Integer, default=0, comment="挂断方：0-未知 1-主叫 2-被叫 3-系统")
    transferred_from = Column(String(20), comment="转移来源号码")
    transferred_to = Column(String(20), comment="转移目标号码")
    ivr_path = Column(JSON, comment="IVR路径")
    skill_group_id = Column(Integer, ForeignKey("skill_group.id"), comment="技能组ID")
    tags = Column(JSON, comment="通话标签")
    remark = Column(Text, comment="备注")
    asr_text = Column(Text, comment="ASR识别文本")
    quality_score = Column(Integer, comment="质检分数")
    quality_result = Column(JSON, comment="质检结果")
    # 关联
    user = relationship("User")
    customer = relationship("Customer", back_populates="call_records")
    skill_group = relationship("SkillGroup")
    @classmethod
    async def get_by_call_id(cls, db: AsyncSession, call_id: str):
        result = await db.execute(select(cls).where(cls.call_id == call_id))
        return result.scalar_one_or_none()
class CallTask(BaseModel):
    __tablename__ = "call_task"
    name = Column(String(100), nullable=False, comment="任务名称")
    description = Column(String(255), comment="任务描述")
    type = Column(Integer, default=1, comment="任务类型：1-手动外呼 2-自动外呼 3-预测外呼")
    status = Column(Integer, default=1, comment="任务状态：1-待执行 2-执行中 3-已暂停 4-已完成 5-已取消")
    caller_ids = Column(JSON, comment="主叫号码ID列表")
    user_ids = Column(JSON, comment="坐席ID列表")
    customer_ids = Column(JSON, comment="客户ID列表")
    total_count = Column(Integer, default=0, comment="总客户数")
    completed_count = Column(Integer, default=0, comment="已完成数")
    success_count = Column(Integer, default=0, comment="成功接通数")
    failed_count = Column(Integer, default=0, comment="失败数")
    concurrent_count = Column(Integer, default=5, comment="并发数")
    retry_count = Column(Integer, default=0, comment="重试次数")
    retry_interval = Column(Integer, default=60, comment="重试间隔(秒)")
    start_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    allow_time_start = Column(String(10), comment="允许拨打开始时间")
    allow_time_end = Column(String(10), comment="允许拨打结束时间")
    script_id = Column(Integer, ForeignKey("call_script.id"), comment="话术ID")
    created_by = Column(Integer, ForeignKey("system_user.id"), comment="创建人ID")
    # 关联
    script = relationship("CallScript")
    created_user = relationship("User", foreign_keys=[created_by])
class CallScript(BaseModel):
    __tablename__ = "call_script"
    name = Column(String(100), nullable=False, comment="话术名称")
    description = Column(String(255), comment="话术描述")
    type = Column(Integer, default=1, comment="话术类型：1-开场话术 2-产品介绍 3-异议处理 4-成交话术 5-结束语")
    content = Column(Text, nullable=False, comment="话术内容")
    variables = Column(JSON, comment="可用变量列表")
    category_id = Column(Integer, ForeignKey("call_script_category.id"), comment="分类ID")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(Boolean, default=True, comment="状态")
    usage_count = Column(Integer, default=0, comment="使用次数")
    success_rate = Column(Integer, default=0, comment="成功率(%)")
    created_by = Column(Integer, ForeignKey("system_user.id"), comment="创建人ID")
    # 关联
    category = relationship("CallScriptCategory")
    created_user = relationship("User", foreign_keys=[created_by])
class CallScriptCategory(BaseModel):
    __tablename__ = "call_script_category"
    name = Column(String(50), nullable=False, comment="分类名称")
    parent_id = Column(Integer, default=0, comment="父分类ID")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(Boolean, default=True, comment="状态")
class CallerNumber(BaseModel):
    __tablename__ = "caller_number"
    number = Column(String(20), unique=True, nullable=False, comment="主叫号码")
    name = Column(String(50), comment="号码名称")
    provider = Column(String(50), comment="运营商")
    area = Column(String(50), comment="归属地")
    max_concurrent = Column(Integer, default=10, comment="最大并发数")
    current_concurrent = Column(Integer, default=0, comment="当前并发数")
    total_calls = Column(Integer, default=0, comment="总呼叫数")
    success_calls = Column(Integer, default=0, comment="成功呼叫数")
    status = Column(Boolean, default=True, comment="状态")
    remark = Column(String(255), comment="备注")
class SkillGroup(BaseModel):
    __tablename__ = "skill_group"
    name = Column(String(50), nullable=False, comment="技能组名称")
    description = Column(String(255), comment="描述")
    type = Column(Integer, default=1, comment="技能组类型：1-呼入 2-外呼 3-通用")
    strategy = Column(Integer, default=1, comment="分配策略：1-轮询 2-随机 3-最少接听 4-最长空闲 5-技能优先级")
    user_ids = Column(JSON, comment="坐席ID列表")
    max_waiting = Column(Integer, default=20, comment="最大等待人数")
    wait_timeout = Column(Integer, default=30, comment="等待超时时间(秒)")
    no_answer_forward = Column(String(20), comment="无应答转接号码")
    overflow_forward = Column(String(20), comment="溢出转接号码")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(Boolean, default=True, comment="状态")
class BlackList(BaseModel):
    __tablename__ = "black_list"
    phone = Column(String(20), unique=True, index=True, nullable=False, comment="电话号码")
    type = Column(Integer, default=1, comment="类型：1-投诉 2-骚扰 3-无效号码 4-其他")
    reason = Column(String(255), comment="拉黑原因")
    source = Column(String(50), comment="来源")
    expired_at = Column(DateTime, comment="过期时间")
    created_by = Column(Integer, ForeignKey("system_user.id"), comment="创建人ID")
    # 关联
    created_user = relationship("User", foreign_keys=[created_by])
    @classmethod
    async def exists_by_phone(cls, db: AsyncSession, phone: str):
        result = await db.execute(select(cls).where(cls.phone == phone, cls.is_deleted == False))
        return result.scalar_one_or_none() is not None
class IVRConfig(BaseModel):
    __tablename__ = "ivr_config"
    name = Column(String(50), nullable=False, comment="IVR名称")
    description = Column(String(255), comment="描述")
    number = Column(String(20), comment="接入号码")
    config = Column(JSON, nullable=False, comment="IVR配置")
    status = Column(Boolean, default=True, comment="状态")
