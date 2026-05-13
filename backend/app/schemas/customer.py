from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema, PageRequest
# 客户相关Schema
class CustomerBase(BaseSchema):
    name: Optional[str] = Field(None, description="客户姓名")
    phone: Optional[str] = Field(None, description="手机号码")
    gender: Optional[int] = Field(0, description="性别：0-未知 1-男 2-女")
    age: Optional[int] = Field(None, description="年龄")
    email: Optional[str] = Field(None, description="邮箱")
    company: Optional[str] = Field(None, description="公司名称")
    position: Optional[str] = Field(None, description="职位")
    address: Optional[str] = Field(None, description="联系地址")
    source: Optional[str] = Field(None, description="客户来源")
    level: Optional[int] = Field(1, description="客户等级：1-普通 2-VIP 3-重要客户")
    status: Optional[int] = Field(1, description="客户状态：1-待联系 2-联系中 3-有意向 4-已成交 5-已拒绝 6-无效客户")
    tags: Optional[List[str]] = Field(None, description="客户标签")
    description: Optional[str] = Field(None, description="客户描述")
    remark: Optional[str] = Field(None, description="备注")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="自定义字段")
class CustomerCreate(CustomerBase):
    phone: str = Field(description="手机号码", min_length=11, max_length=11)
class CustomerUpdate(CustomerBase):
    pass
class CustomerResponse(CustomerBase):
    id: int = Field(description="客户ID")
    assign_user_id: Optional[int] = Field(None, description="分配坐席ID")
    assign_user_name: Optional[str] = Field(None, description="分配坐席姓名")
    assign_time: Optional[datetime] = Field(None, description="分配时间")
    last_follow_time: Optional[datetime] = Field(None, description="最后跟进时间")
    next_follow_time: Optional[datetime] = Field(None, description="下次跟进时间")
    follow_count: int = Field(0, description="跟进次数")
    call_count: int = Field(0, description="通话次数")
    total_call_duration: int = Field(0, description="总通话时长(秒)")
    created_at: datetime = Field(description="创建时间")
class CustomerQuery(PageRequest):
    keyword: Optional[str] = Field(None, description="搜索关键词（姓名、手机号、公司）")
    status: Optional[int] = Field(None, description="客户状态")
    level: Optional[int] = Field(None, description="客户等级")
    tags: Optional[List[str]] = Field(None, description="客户标签")
    assign_user_id: Optional[int] = Field(None, description="分配坐席ID")
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    source: Optional[str] = Field(None, description="客户来源")
class CustomerAssign(BaseModel):
    customer_ids: List[int] = Field(description="客户ID列表")
    user_id: int = Field(description="分配给的用户ID")
class CustomerImportResult(BaseModel):
    total: int = Field(description="总条数")
    success: int = Field(description="成功条数")
    failed: int = Field(description="失败条数")
    errors: List[str] = Field(description="错误信息列表")
# 跟进记录相关Schema
class FollowRecordBase(BaseSchema):
    customer_id: int = Field(description="客户ID")
    type: Optional[int] = Field(1, description="跟进类型：1-电话 2-微信 3-线下 4-短信 5-邮件")
    content: str = Field(description="跟进内容")
    result: Optional[str] = Field(None, description="跟进结果")
    next_follow_time: Optional[datetime] = Field(None, description="下次跟进时间")
    follow_time: datetime = Field(description="跟进时间")
    duration: Optional[int] = Field(0, description="时长(秒)")
    attachment: Optional[List[str]] = Field(None, description="附件")
class FollowRecordCreate(FollowRecordBase):
    pass
class FollowRecordResponse(FollowRecordBase):
    id: int = Field(description="记录ID")
    user_id: int = Field(description="跟进人ID")
    user_name: Optional[str] = Field(None, description="跟进人姓名")
    created_at: datetime = Field(description="创建时间")
class FollowRecordQuery(PageRequest):
    customer_id: Optional[int] = Field(None, description="客户ID")
    user_id: Optional[int] = Field(None, description="跟进人ID")
    type: Optional[int] = Field(None, description="跟进类型")
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
# 标签相关Schema
class TagBase(BaseSchema):
    name: str = Field(description="标签名称")
    color: Optional[str] = Field("#1890ff", description="标签颜色")
    type: Optional[int] = Field(1, description="标签类型：1-客户标签 2-其他")
    sort: Optional[int] = Field(0, description="排序")
class TagCreate(TagBase):
    pass
class TagResponse(TagBase):
    id: int = Field(description="标签ID")
    count: int = Field(0, description="使用次数")
    created_at: datetime = Field(description="创建时间")
class TagQuery(PageRequest):
    name: Optional[str] = Field(None, description="标签名称")
    type: Optional[int] = Field(None, description="标签类型")
class CustomerStatistics(BaseModel):
    total_count: int = Field(description="总客户数")
    today_new: int = Field(description="今日新增")
    week_new: int = Field(description="本周新增")
    month_new: int = Field(description="本月新增")
    follow_count: int = Field(description="待跟进数")
    intention_count: int = Field(description="有意向数")
    deal_count: int = Field(description="已成交数")
    invalid_count: int = Field(description="无效客户数")
    conversion_rate: float = Field(description="转化率(%)")
