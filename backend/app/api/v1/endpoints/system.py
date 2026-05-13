from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permission import PermissionChecker, get_current_active_user
from app.db.session import get_db
from app.models.system import User
from app.schemas.system import (
    SystemConfigCreate,
    SystemConfigUpdate,
    SystemConfigResponse,
    SystemConfigQuery,
    OperationLogResponse,
    OperationLogQuery,
    SystemInfoResponse,
    SystemStatusResponse
)
from app.schemas.base import PageResponse, ResponseBase
from app.services.system import system_config_service, operation_log_service
from app.utils.logger import logger
router = APIRouter()
# 系统配置相关接口
@router.get("/config/public", response_model=ResponseBase[Dict[str, str]], summary="获取公开系统配置")
async def get_public_config(
    db: AsyncSession = Depends(get_db)
):
    """
    获取公开的系统配置，不需要登录
    """
    configs = await system_config_service.get_all(db, is_public=True)
    return ResponseBase(data=configs)
@router.get("/config/list", response_model=ResponseBase[PageResponse[SystemConfigResponse]], summary="获取系统配置列表")
async def get_system_config_list(
    query: SystemConfigQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/system/config/list", method="GET"))
):
    """
    获取系统配置列表，支持分页和条件查询
    """
    filters = {}
    if query.key:
        filters["key"] = query.key
    if query.name:
        filters["name"] = query.name
    if query.type is not None:
        filters["type"] = query.type
    if query.is_public is not None:
        filters["is_public"] = query.is_public
    result = await system_config_service.get_multi(
        db,
        page=query.page,
        page_size=query.page_size,
        filters=filters
    )
    return ResponseBase(data=result)
@router.get("/config/all", response_model=ResponseBase[Dict[str, str]], summary="获取所有系统配置")
async def get_all_system_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/system/config/all", method="GET"))
):
    """
    获取所有系统配置
    """
    configs = await system_config_service.get_all(db)
    return ResponseBase(data=configs)
@router.get("/config/{key}", response_model=ResponseBase[SystemConfigResponse], summary="获取系统配置详情")
async def get_system_config_detail(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/system/config/detail", method="GET"))
):
    """
    根据配置键获取配置详情
    """
    result = await system_config_service.get_multi(db, filters={"key": key})
    if not result["list"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    return ResponseBase(data=result["list"][0])
@router.post("/config/create", response_model=ResponseBase[SystemConfigResponse], summary="创建系统配置")
async def create_system_config(
    config_in: SystemConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/system/config/create", method="POST"))
):
    """
    创建新的系统配置
    """
    # 检查配置键是否存在
    existing_config = await system_config_service.get_by_key(db, key=config_in.key)
    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"配置键 {config_in.key} 已存在"
        )
    config = await system_config_service.create(db, obj_in=config_in)
    logger.info(f"创建系统配置成功: {config.key}")
    return ResponseBase(data=config, message="创建配置成功")
@router.put("/config/update/{config_id}", response_model=ResponseBase[SystemConfigResponse], summary="更新系统配置")
async def update_system_config(
    config_id: int,
    config_in: SystemConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/system/config/update", method="PUT"))
):
    """
    更新系统配置
    """
    config = await system_config_service.get(db, id=config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    # 检查配置键是否重复
    if config_in.key and config_in.key != config.key:
        existing_config = await system_config_service.get_by_key(db, key=config_in.key)
        if existing_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"配置键 {config_in.key} 已存在"
            )
    config = await system_config_service.update(db, db_obj=config, obj_in=config_in)
    logger.info(f"更新系统配置成功: {config.key}")
    return ResponseBase(data=config, message="更新配置成功")
@router.delete("/config/delete/{config_id}", response_model=ResponseBase, summary="删除系统配置")
async def delete_system_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/system/config/delete", method="DELETE"))
):
    """
    删除系统配置（软删除）
    """
    config = await system_config_service.get(db, id=config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    await system_config_service.remove(db, id=config_id)
    logger.info(f"删除系统配置成功: {config.key}")
    return ResponseBase(message="删除配置成功")
@router.put("/config/batch-update", response_model=ResponseBase, summary="批量更新系统配置")
async def batch_update_system_config(
    configs: Dict[str, str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/system/config/batch-update", method="PUT"))
):
    """
    批量更新系统配置
    """
    await system_config_service.batch_set(db, configs=configs)
    return ResponseBase(message="批量更新配置成功")
# 操作日志相关接口
@router.get("/operation-log/list", response_model=ResponseBase[PageResponse[OperationLogResponse]], summary="获取操作日志列表")
async def get_operation_log_list(
    query: OperationLogQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/system/operation-log/list", method="GET"))
):
    """
    获取操作日志列表，支持分页和条件查询
    """
    result = await operation_log_service.get_list(
        db,
        page=query.page,
        page_size=query.page_size,
        user_id=query.user_id,
        module=query.module,
        operation=query.operation,
        status=query.status,
        start_time=query.start_time,
        end_time=query.end_time
    )
    return ResponseBase(data=result)
# 系统信息相关接口
@router.get("/info", response_model=ResponseBase[SystemInfoResponse], summary="获取系统信息")
async def get_system_info(
    current_user: User = Depends(PermissionChecker(path="/system/info", method="GET"))
):
    """
    获取系统基本信息
    """
    import sys
    import platform
    import multiprocessing
    import psutil
    from datetime import datetime
    # 获取进程启动时间
    process = psutil.Process()
    start_time = datetime.fromtimestamp(process.create_time())
    run_time = str(datetime.now() - start_time).split(".")[0]
    info = SystemInfoResponse(
        version="1.0.0",
        python_version=sys.version.split(" ")[0],
        fastapi_version=platform.python_version(),  # 这里应该获取FastAPI版本，暂时用Python版本代替
        os=platform.platform(),
        cpu_count=multiprocessing.cpu_count(),
        memory_total=int(psutil.virtual_memory().total / 1024 / 1024),
        disk_total=int(psutil.disk_usage("/").total / 1024 / 1024 / 1024),
        run_time=run_time
    )
    return ResponseBase(data=info)
@router.get("/status", response_model=ResponseBase[SystemStatusResponse], summary="获取系统实时状态")
async def get_system_status(
    current_user: User = Depends(PermissionChecker(path="/system/status", method="GET"))
):
    """
    获取系统实时运行状态
    """
    import psutil
    # 获取CPU使用率
    cpu_usage = psutil.cpu_percent(interval=0.1)
    # 获取内存使用率
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    # 获取磁盘使用率
    disk = psutil.disk_usage("/")
    disk_usage = disk.percent
    # 获取网络速度
    net_io = psutil.net_io_counters()
    import time
    time.sleep(1)
    net_io2 = psutil.net_io_counters()
    network_rx = int((net_io2.bytes_recv - net_io.bytes_recv) / 1024)
    network_tx = int((net_io2.bytes_sent - net_io.bytes_sent) / 1024)
    # 获取进程和线程数
    process_count = len(psutil.pids())
    thread_count = sum(p.num_threads() for p in psutil.process_iter())
    status = SystemStatusResponse(
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        disk_usage=disk_usage,
        network_rx=network_rx,
        network_tx=network_tx,
        process_count=process_count,
        thread_count=thread_count
    )
    return ResponseBase(data=status)
