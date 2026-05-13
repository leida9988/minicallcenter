from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema, PageRequest
class SystemConfigBase(BaseSchema):
    key: str = Field(description="配置键")
    value: str = Field(description="配置值")
    name: Optional[str] = Field(None, description="配置名称")
    description: Optional[str] = Field(None, description="配置描述")
    type: Optional[int] = Field(1, description="配置类型：1-系统配置 2-业务配置")
    sort: Optional[int] = Field(0, description="排序")
    is_public: Optional[bool] = Field(False, description="是否公开")
class SystemConfigCreate(SystemConfigBase):
    pass
class SystemConfigUpdate(SystemConfigBase):
    pass
class SystemConfigResponse(SystemConfigBase):
    pass
class SystemConfigQuery(PageRequest):
    key: Optional[str] = Field(None, description="配置键")
    name: Optional[str] = Field(None, description="配置名称")
    type: Optional[int] = Field(None, description="配置类型")
    is_public: Optional[bool] = Field(None, description="是否公开")
class OperationLogBase(BaseSchema):
    user_id: Optional[int] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    module: Optional[str] = Field(None, description="模块名称")
    operation: Optional[str] = Field(None, description="操作类型")
    method: Optional[str] = Field(None, description="请求方法")
    path: Optional[str] = Field(None, description="请求路径")
    ip: Optional[str] = Field(None, description="IP地址")
    location: Optional[str] = Field(None, description="操作地点")
    user_agent: Optional[str] = Field(None, description="User Agent")
    request_params: Optional[Dict[str, Any]] = Field(None, description="请求参数")
    response_result: Optional[Dict[str, Any]] = Field(None, description="响应结果")
    status: Optional[int] = Field(1, description="操作状态：1-成功 2-失败")
    error_msg: Optional[str] = Field(None, description="错误信息")
    cost_time: Optional[int] = Field(None, description="耗时(ms)")
class OperationLogResponse(OperationLogBase):
    pass
class OperationLogQuery(PageRequest):
    user_id: Optional[int] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    module: Optional[str] = Field(None, description="模块名称")
    operation: Optional[str] = Field(None, description="操作类型")
    status: Optional[int] = Field(None, description="操作状态")
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
class SystemInfoResponse(BaseModel):
    version: str = Field(description="系统版本")
    python_version: str = Field(description="Python版本")
    fastapi_version: str = Field(description="FastAPI版本")
    os: str = Field(description="操作系统")
    cpu_count: int = Field(description="CPU核心数")
    memory_total: int = Field(description="总内存(MB)")
    disk_total: int = Field(description="总磁盘(GB)")
    run_time: str = Field(description="运行时间")
class SystemStatusResponse(BaseModel):
    cpu_usage: float = Field(description="CPU使用率(%)")
    memory_usage: float = Field(description="内存使用率(%)")
    disk_usage: float = Field(description="磁盘使用率(%)")
    network_rx: int = Field(description="网络接收速度(KB/s)")
    network_tx: int = Field(description="网络发送速度(KB/s)")
    process_count: int = Field(description="进程数")
    thread_count: int = Field(description="线程数")
