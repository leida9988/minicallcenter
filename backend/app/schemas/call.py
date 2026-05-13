from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema, PageRequest
# 通话记录相关Schema
class CallRecordBase(BaseSchema):
    call_id: str = Field(description="通话唯一ID")
    caller: Optional[str] = Field(None, description="主叫号码")
    called: Optional[str] = Field(None, description="被叫号码")
    user_id: Optional[int] = Field(None, description="坐席ID")
    customer_id: Optional[int] = Field(None, description="客户ID")
    direction: Optional[int] = Field(1, description="通话方向：1-外呼 2-呼入")
    status: Optional[int] = Field(1, description="通话状态：1-呼叫中 2-已接通 3-已挂断 4-未接通 5-占线 6-无人接听 7-号码错误")
    start_time: Optional[datetime] = Field(None, description="通话开始时间")
    answer_time: Optional[datetime] = Field(None, description="接听时间")
    end_time: Optional[datetime] = Field(None, description="通话结束时间")
    duration: Optional[int] = Field(0, description="通话时长(秒)")
    ring_duration: Optional[int] = Field(0, description="振铃时长(秒)")
    wait_duration: Optional[int] = Field(0, description="等待时长(秒)")
    recording_url: Optional[str] = Field(None, description="录音文件URL")
    recording_path: Optional[str] = Field(None, description="录音文件路径")
    recording_duration: Optional[int] = Field(0, description="录音时长(秒)")
    sip_code: Optional[str] = Field(None, description="SIP响应码")
    sip_reason: Optional[str] = Field(None, description="SIP响应原因")
    hangup_cause: Optional[str] = Field(None, description="挂断原因")
    hangup_side: Optional[int] = Field(0, description="挂断方：0-未知 1-主叫 2-被叫 3-系统")
    transferred_from: Optional[str] = Field(None, description="转移来源号码")
    transferred_to: Optional[str] = Field(None, description="转移目标号码")
    ivr_path: Optional[List[str]] = Field(None, description="IVR路径")
    skill_group_id: Optional[int] = Field(None, description="技能组ID")
    tags: Optional[List[str]] = Field(None, description="通话标签")
    remark: Optional[str] = Field(None, description="备注")
    asr_text: Optional[str] = Field(None, description="ASR识别文本")
    quality_score: Optional[int] = Field(None, description="质检分数")
    quality_result: Optional[Dict[str, Any]] = Field(None, description="质检结果")
class CallRecordCreate(CallRecordBase):
    pass
class CallRecordResponse(CallRecordBase):
    id: int = Field(description="记录ID")
    user_name: Optional[str] = Field(None, description="坐席姓名")
    customer_name: Optional[str] = Field(None, description="客户姓名")
    customer_phone: Optional[str] = Field(None, description="客户手机号")
    skill_group_name: Optional[str] = Field(None, description="技能组名称")
    created_at: datetime = Field(description="创建时间")
class CallRecordQuery(PageRequest):
    caller: Optional[str] = Field(None, description="主叫号码")
    called: Optional[str] = Field(None, description="被叫号码")
    user_id: Optional[int] = Field(None, description="坐席ID")
    customer_id: Optional[int] = Field(None, description="客户ID")
    direction: Optional[int] = Field(None, description="通话方向")
    status: Optional[int] = Field(None, description="通话状态")
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    min_duration: Optional[int] = Field(None, description="最小通话时长(秒)")
    max_duration: Optional[int] = Field(None, description="最大通话时长(秒)")
# 呼叫任务相关Schema
class CallTaskBase(BaseSchema):
    name: str = Field(description="任务名称")
    description: Optional[str] = Field(None, description="任务描述")
    type: Optional[int] = Field(1, description="任务类型：1-手动外呼 2-自动外呼 3-预测外呼")
    status: Optional[int] = Field(1, description="任务状态：1-待执行 2-执行中 3-已暂停 4-已完成 5-已取消")
    caller_ids: Optional[List[int]] = Field(None, description="主叫号码ID列表")
    user_ids: Optional[List[int]] = Field(None, description="坐席ID列表")
    customer_ids: Optional[List[int]] = Field(None, description="客户ID列表")
    total_count: Optional[int] = Field(0, description="总客户数")
    completed_count: Optional[int] = Field(0, description="已完成数")
    success_count: Optional[int] = Field(0, description="成功接通数")
    failed_count: Optional[int] = Field(0, description="失败数")
    concurrent_count: Optional[int] = Field(5, description="并发数")
    retry_count: Optional[int] = Field(0, description="重试次数")
    retry_interval: Optional[int] = Field(60, description="重试间隔(秒)")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    allow_time_start: Optional[str] = Field(None, description="允许拨打开始时间")
    allow_time_end: Optional[str] = Field(None, description="允许拨打结束时间")
    script_id: Optional[int] = Field(None, description="话术ID")
class CallTaskCreate(CallTaskBase):
    name: str = Field(description="任务名称")
    customer_ids: List[int] = Field(description="客户ID列表")
class CallTaskResponse(CallTaskBase):
    id: int = Field(description="任务ID")
    created_by: int = Field(description="创建人ID")
    created_by_name: Optional[str] = Field(None, description="创建人姓名")
    script_name: Optional[str] = Field(None, description="话术名称")
    created_at: datetime = Field(description="创建时间")
class CallTaskQuery(PageRequest):
    name: Optional[str] = Field(None, description="任务名称")
    type: Optional[int] = Field(None, description="任务类型")
    status: Optional[int] = Field(None, description="任务状态")
    created_by: Optional[int] = Field(None, description="创建人ID")
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
class CallTaskControl(BaseModel):
    task_id: int = Field(description="任务ID")
    action: str = Field(description="操作：start-启动 pause-暂停 stop-停止 resume-恢复")
# 通话控制相关Schema
class CallControlRequest(BaseModel):
    call_id: str = Field(description="通话ID")
    action: str = Field(description="操作：hangup-挂断 hold-保持 unhold-取消保持 transfer-转接 mute-静音 unmute-取消静音")
    target_number: Optional[str] = Field(None, description="转接目标号码")
class CallOutboundRequest(BaseModel):
    customer_id: int = Field(description="客户ID")
    caller_number: Optional[str] = Field(None, description="主叫号码，不指定则系统自动分配")
class CallStatusResponse(BaseModel):
    call_id: str = Field(description="通话ID")
    status: str = Field(description="通话状态")
    caller: str = Field(description="主叫号码")
    called: str = Field(description="被叫号码")
    duration: int = Field(0, description="通话时长(秒)")
    user_id: Optional[int] = Field(None, description="坐席ID")
    customer_id: Optional[int] = Field(None, description="客户ID")
    extra: Optional[Dict[str, Any]] = Field(None, description="额外信息")
# 话术相关Schema
class CallScriptBase(BaseSchema):
    name: str = Field(description="话术名称")
    description: Optional[str] = Field(None, description="话术描述")
    type: Optional[int] = Field(1, description="话术类型：1-开场话术 2-产品介绍 3-异议处理 4-成交话术 5-结束语")
    content: str = Field(description="话术内容")
    variables: Optional[List[str]] = Field(None, description="可用变量列表")
    category_id: Optional[int] = Field(None, description="分类ID")
    sort: Optional[int] = Field(0, description="排序")
    status: Optional[bool] = Field(True, description="状态")
class CallScriptCreate(CallScriptBase):
    name: str = Field(description="话术名称")
    content: str = Field(description="话术内容")
class CallScriptResponse(CallScriptBase):
    id: int = Field(description="话术ID")
    category_name: Optional[str] = Field(None, description="分类名称")
    usage_count: int = Field(0, description="使用次数")
    success_rate: int = Field(0, description="成功率(%)")
    created_by: int = Field(description="创建人ID")
    created_by_name: Optional[str] = Field(None, description="创建人姓名")
    created_at: datetime = Field(description="创建时间")
class CallScriptQuery(PageRequest):
    name: Optional[str] = Field(None, description="话术名称")
    type: Optional[int] = Field(None, description="话术类型")
    category_id: Optional[int] = Field(None, description="分类ID")
    status: Optional[bool] = Field(None, description="状态")
class CallScriptCategoryBase(BaseSchema):
    name: str = Field(description="分类名称")
    parent_id: Optional[int] = Field(0, description="父分类ID")
    sort: Optional[int] = Field(0, description="排序")
    status: Optional[bool] = Field(True, description="状态")
class CallScriptCategoryCreate(CallScriptCategoryBase):
    name: str = Field(description="分类名称")
class CallScriptCategoryResponse(CallScriptCategoryBase):
    id: int = Field(description="分类ID")
    children: Optional[List["CallScriptCategoryResponse"]] = Field(None, description="子分类")
# 主叫号码相关Schema
class CallerNumberBase(BaseSchema):
    number: str = Field(description="主叫号码")
    name: Optional[str] = Field(None, description="号码名称")
    provider: Optional[str] = Field(None, description="运营商")
    area: Optional[str] = Field(None, description="归属地")
    max_concurrent: Optional[int] = Field(10, description="最大并发数")
    current_concurrent: Optional[int] = Field(0, description="当前并发数")
    total_calls: Optional[int] = Field(0, description="总呼叫数")
    success_calls: Optional[int] = Field(0, description="成功呼叫数")
    status: Optional[bool] = Field(True, description="状态")
    remark: Optional[str] = Field(None, description="备注")
class CallerNumberCreate(CallerNumberBase):
    number: str = Field(description="主叫号码")
class CallerNumberResponse(CallerNumberBase):
    id: int = Field(description="号码ID")
    success_rate: float = Field(0, description="成功率(%)")
    created_at: datetime = Field(description="创建时间")
# 技能组相关Schema
class SkillGroupBase(BaseSchema):
    name: str = Field(description="技能组名称")
    description: Optional[str] = Field(None, description="描述")
    type: Optional[int] = Field(1, description="技能组类型：1-呼入 2-外呼 3-通用")
    strategy: Optional[int] = Field(1, description="分配策略：1-轮询 2-随机 3-最少接听 4-最长空闲 5-技能优先级")
    user_ids: Optional[List[int]] = Field(None, description="坐席ID列表")
    max_waiting: Optional[int] = Field(20, description="最大等待人数")
    wait_timeout: Optional[int] = Field(30, description="等待超时时间(秒)")
    no_answer_forward: Optional[str] = Field(None, description="无应答转接号码")
    overflow_forward: Optional[str] = Field(None, description="溢出转接号码")
    sort: Optional[int] = Field(0, description="排序")
    status: Optional[bool] = Field(True, description="状态")
class SkillGroupCreate(SkillGroupBase):
    name: str = Field(description="技能组名称")
class SkillGroupResponse(SkillGroupBase):
    id: int = Field(description="技能组ID")
    user_names: Optional[List[str]] = Field(None, description="坐席姓名列表")
    created_at: datetime = Field(description="创建时间")
# 黑名单相关Schema
class BlackListBase(BaseSchema):
    phone: str = Field(description="电话号码")
    type: Optional[int] = Field(1, description="类型：1-投诉 2-骚扰 3-无效号码 4-其他")
    reason: Optional[str] = Field(None, description="拉黑原因")
    source: Optional[str] = Field(None, description="来源")
    expired_at: Optional[datetime] = Field(None, description="过期时间")
class BlackListCreate(BlackListBase):
    phone: str = Field(description="电话号码")
class BlackListResponse(BlackListBase):
    id: int = Field(description="记录ID")
    created_by: int = Field(description="创建人ID")
    created_by_name: Optional[str] = Field(None, description="创建人姓名")
    created_at: datetime = Field(description="创建时间")
class BlackListQuery(PageRequest):
    phone: Optional[str] = Field(None, description="电话号码")
    type: Optional[int] = Field(None, description="类型")
    source: Optional[str] = Field(None, description="来源")
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
# IVR配置相关Schema
class IVRConfigBase(BaseSchema):
    name: str = Field(description="IVR名称")
    description: Optional[str] = Field(None, description="描述")
    number: Optional[str] = Field(None, description="接入号码")
    config: Dict[str, Any] = Field(description="IVR配置")
    status: Optional[bool] = Field(True, description="状态")
class IVRConfigCreate(IVRConfigBase):
    name: str = Field(description="IVR名称")
    config: Dict[str, Any] = Field(description="IVR配置")
class IVRConfigResponse(IVRConfigBase):
    id: int = Field(description="配置ID")
    created_at: datetime = Field(description="创建时间")
# 通话统计相关Schema
class CallStatistics(BaseModel):
    total_calls: int = Field(description="总呼叫数")
    answered_calls: int = Field(description="接通数")
    answer_rate: float = Field(description="接通率(%)")
    total_duration: int = Field(description="总通话时长(秒)")
    avg_duration: float = Field(description="平均通话时长(秒)")
    success_calls: int = Field(description="成功呼叫数")
    failed_calls: int = Field(description="失败呼叫数")
    busy_calls: int = Field(description="占线数")
    no_answer_calls: int = Field(description="无人接听数")
    customer_reject_calls: int = Field(description="客户拒接数")
# 解决循环引用
CallScriptCategoryResponse.model_rebuild()
