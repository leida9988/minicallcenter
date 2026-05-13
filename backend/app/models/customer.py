from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.base import BaseModel
class Customer(BaseModel):
    __tablename__ = "customer"
    name = Column(String(100), comment="客户姓名")
    phone = Column(String(20), index=True, comment="手机号码")
    gender = Column(Integer, default=0, comment="性别：0-未知 1-男 2-女")
    age = Column(Integer, comment="年龄")
    email = Column(String(100), comment="邮箱")
    company = Column(String(255), comment="公司名称")
    position = Column(String(100), comment="职位")
    address = Column(String(255), comment="联系地址")
    source = Column(String(50), comment="客户来源")
    level = Column(Integer, default=1, comment="客户等级：1-普通 2-VIP 3-重要客户")
    status = Column(Integer, default=1, comment="客户状态：1-待联系 2-联系中 3-有意向 4-已成交 5-已拒绝 6-无效客户")
    tags = Column(JSON, comment="客户标签")
    description = Column(Text, comment="客户描述")
    remark = Column(Text, comment="备注")
    assign_user_id = Column(Integer, ForeignKey("system_user.id"), comment="分配坐席ID")
    assign_time = Column(DateTime, comment="分配时间")
    last_follow_time = Column(DateTime, comment="最后跟进时间")
    next_follow_time = Column(DateTime, comment="下次跟进时间")
    follow_count = Column(Integer, default=0, comment="跟进次数")
    call_count = Column(Integer, default=0, comment="通话次数")
    total_call_duration = Column(Integer, default=0, comment="总通话时长(秒)")
    custom_fields = Column(JSON, comment="自定义字段")
    # 关联
    assign_user = relationship("User", foreign_keys=[assign_user_id])
    follow_records = relationship("FollowRecord", back_populates="customer")
    call_records = relationship("CallRecord", back_populates="customer")
    @classmethod
    async def get_by_phone(cls, db: AsyncSession, phone: str):
        result = await db.execute(select(cls).where(cls.phone == phone, cls.is_deleted == False))
        return result.scalar_one_or_none()
class FollowRecord(BaseModel):
    __tablename__ = "follow_record"
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False, comment="客户ID")
    user_id = Column(Integer, ForeignKey("system_user.id"), nullable=False, comment="跟进人ID")
    type = Column(Integer, default=1, comment="跟进类型：1-电话 2-微信 3-线下 4-短信 5-邮件")
    content = Column(Text, comment="跟进内容")
    result = Column(String(255), comment="跟进结果")
    next_follow_time = Column(DateTime, comment="下次跟进时间")
    follow_time = Column(DateTime, nullable=False, comment="跟进时间")
    duration = Column(Integer, comment="时长(秒)")
    attachment = Column(JSON, comment="附件")
    # 关联
    customer = relationship("Customer", back_populates="follow_records")
    user = relationship("User")
class Tag(BaseModel):
    __tablename__ = "tag"
    name = Column(String(50), nullable=False, comment="标签名称")
    color = Column(String(20), default="#1890ff", comment="标签颜色")
    type = Column(Integer, default=1, comment="标签类型：1-客户标签 2-其他")
    sort = Column(Integer, default=0, comment="排序")
    count = Column(Integer, default=0, comment="使用次数")
class PublicSeaPool(BaseModel):
    __tablename__ = "public_sea_pool"
    name = Column(String(50), nullable=False, comment="公海池名称")
    description = Column(String(255), comment="描述")
    department_ids = Column(JSON, comment="可见部门ID列表")
    auto_recycle_days = Column(Integer, default=7, comment="自动回收天数")
    max_receive_count = Column(Integer, default=10, comment="每人最大领取数")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(Boolean, default=True, comment="状态")
class PublicSeaConfig(BaseModel):
    __tablename__ = "public_sea_config"
    pool_id = Column(Integer, ForeignKey("public_sea_pool.id"), nullable=False, comment="公海池ID")
    key = Column(String(100), nullable=False, comment="配置键")
    value = Column(String(255), comment="配置值")
    description = Column(String(255), comment="配置描述")
    # 关联
    pool = relationship("PublicSeaPool")
