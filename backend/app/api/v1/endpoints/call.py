from typing import Any, List, Dict
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import asyncio
from app.core.permission import PermissionChecker, get_current_active_user
from app.db.session import get_db
from app.models.system import User
from app.models.customer import Customer
from app.schemas.call import (
    CallRecordResponse,
    CallRecordQuery,
    CallTaskCreate,
    CallTaskResponse,
    CallTaskQuery,
    CallTaskControl,
    CallControlRequest,
    CallOutboundRequest,
    CallStatusResponse,
    CallScriptCreate,
    CallScriptResponse,
    CallScriptQuery,
    CallScriptCategoryCreate,
    CallScriptCategoryResponse,
    CallerNumberCreate,
    CallerNumberResponse,
    SkillGroupCreate,
    SkillGroupResponse,
    BlackListCreate,
    BlackListResponse,
    BlackListQuery,
    IVRConfigCreate,
    IVRConfigResponse,
    CallStatistics
)
from app.schemas.base import PageResponse, ResponseBase
from app.services.call import (
    freeswitch_service,
    call_record_service,
    call_task_service,
    call_script_service,
    call_script_category_service,
    caller_number_service,
    skill_group_service,
    black_list_service,
    ivr_config_service
)
from app.services.customer import customer_service
from app.utils.logger import logger
router = APIRouter()
# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    async def send_personal_message(self, message: Dict[str, Any], user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)
    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections.values():
            await connection.send_json(message)
manager = ConnectionManager()
# WebSocket接口
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """
    实时通话事件通知WebSocket接口
    """
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # 处理客户端发送的消息
            logger.debug(f"收到WebSocket消息: user_id={user_id}, data={data}")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        logger.info(f"WebSocket连接断开: user_id={user_id}")
# 通话控制相关接口
@router.post("/outbound", response_model=ResponseBase[CallStatusResponse], summary="发起外呼")
async def make_outbound_call(
    request: CallOutboundRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    发起对外呼叫
    """
    # 检查客户是否存在
    customer = await customer_service.get(db, id=request.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户不存在"
        )
    # 检查号码是否在黑名单
    if await black_list_service.exists_by_phone(db, phone=customer.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该号码在黑名单中，无法呼叫"
        )
    # 分配主叫号码
    if request.caller_number:
        # 检查指定的主叫号码是否可用
        caller_numbers = await caller_number_service.get_available(db)
        caller_number = next((n for n in caller_numbers if n.number == request.caller_number), None)
        if not caller_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定的主叫号码不可用"
            )
    else:
        # 随机分配可用的主叫号码
        caller_number = await caller_number_service.get_random_available(db)
        if not caller_number:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="暂无可用的主叫号码"
            )
    # 生成唯一通话ID
    call_id = str(uuid.uuid4())
    # 创建通话记录
    record_in = {
        "call_id": call_id,
        "caller": caller_number.number,
        "called": customer.phone,
        "user_id": current_user.id,
        "customer_id": customer.id,
        "direction": 1,  # 外呼
        "status": 1,  # 呼叫中
        "start_time": datetime.now()
    }
    await call_record_service.create_record(db, obj_in=record_in)
    # 发起呼叫
    if not freeswitch_service:
        # 更新通话状态为失败
        await call_record_service.update_call_status(db, call_id=call_id, status=4)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="呼叫功能不可用：FreeSWITCH服务未配置"
        )
    success = await freeswitch_service.originate_call(
        caller_number=caller_number.number,
        called_number=customer.phone,
        user_id=current_user.id,
        customer_id=customer.id,
        call_id=call_id
    )
    if not success:
        # 更新通话状态为失败
        await call_record_service.update_call_status(db, call_id=call_id, status=4)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="呼叫发起失败"
        )
    response = CallStatusResponse(
        call_id=call_id,
        status="calling",
        caller=caller_number.number,
        called=customer.phone,
        user_id=current_user.id,
        customer_id=customer.id
    )
    # 通知坐席客户端
    await manager.send_personal_message(
        {
            "type": "call_outbound",
            "data": response.model_dump()
        },
        user_id=current_user.id
    )
    return ResponseBase(data=response, message="呼叫已发起")
@router.post("/control", response_model=ResponseBase, summary="通话控制")
async def control_call(
    request: CallControlRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    通话控制：挂断、保持、取消保持、转接、静音、取消静音等
    """
    # 检查通话是否存在
    call_record = await call_record_service.get_by_call_id(db, call_id=request.call_id)
    if not call_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通话记录不存在"
        )
    # 检查是否有权限操作该通话
    if call_record.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作该通话"
        )
    success = False
    message = ""
    if not freeswitch_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="呼叫功能不可用：FreeSWITCH服务未配置"
        )
    if request.action == "hangup":
        success = await freeswitch_service.hangup_call(request.call_id)
        message = "挂断成功" if success else "挂断失败"
    elif request.action == "transfer":
        if not request.target_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="转接目标号码不能为空"
            )
        success = await freeswitch_service.transfer_call(request.call_id, request.target_number)
        message = "转接成功" if success else "转接失败"
    elif request.action in ["hold", "unhold", "mute", "unmute"]:
        # TODO: 实现保持、静音等功能
        success = True
        message = f"{request.action}成功"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的操作类型"
        )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    return ResponseBase(message=message)
@router.get("/status/{call_id}", response_model=ResponseBase[CallStatusResponse], summary="获取通话状态")
async def get_call_status(
    call_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定通话的实时状态
    """
    call_record = await call_record_service.get_by_call_id(db, call_id=call_id)
    if not call_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通话记录不存在"
        )
    # 检查权限
    if call_record.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看该通话"
        )
    # 从FreeSWITCH获取实时状态
    fs_status = None
    if freeswitch_service:
        fs_status = await freeswitch_service.get_call_status(call_id)
    if not fs_status:
        # 如果FreeSWITCH中没有该通话，返回数据库中的状态
        status_map = {
            1: "calling",
            2: "connected",
            3: "ended",
            4: "failed"
        }
        response = CallStatusResponse(
            call_id=call_id,
            status=status_map.get(call_record.status, "unknown"),
            caller=call_record.caller,
            called=call_record.called,
            duration=call_record.duration,
            user_id=call_record.user_id,
            customer_id=call_record.customer_id
        )
    else:
        response = CallStatusResponse(
            call_id=call_id,
            status=fs_status.get("Channel-Call-State", "unknown").lower(),
            caller=fs_status.get("Caller-Caller-ID-Number", call_record.caller),
            called=fs_status.get("Caller-Destination-Number", call_record.called),
            duration=int(fs_status.get("Caller-Duration", call_record.duration)),
            user_id=call_record.user_id,
            customer_id=call_record.customer_id,
            extra=fs_status
        )
    return ResponseBase(data=response)
# 通话记录相关接口
@router.get("/record/list", response_model=ResponseBase[PageResponse[CallRecordResponse]], summary="获取通话记录列表")
async def get_call_record_list(
    query: CallRecordQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/record/list", method="GET"))
):
    """
    获取通话记录列表，支持分页和条件查询
    """
    # 如果不是管理员，只能查看自己的通话记录
    if not current_user.is_superuser:
        query.user_id = current_user.id
    result = await call_record_service.get_list(
        db,
        page=query.page,
        page_size=query.page_size,
        caller=query.caller,
        called=query.called,
        user_id=query.user_id,
        customer_id=query.customer_id,
        direction=query.direction,
        status=query.status,
        start_time=query.start_time,
        end_time=query.end_time,
        min_duration=query.min_duration,
        max_duration=query.max_duration
    )
    return ResponseBase(data=result)
@router.get("/record/my-list", response_model=ResponseBase[PageResponse[CallRecordResponse]], summary="获取我的通话记录")
async def get_my_call_record_list(
    query: CallRecordQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户的通话记录
    """
    result = await call_record_service.get_list(
        db,
        page=query.page,
        page_size=query.page_size,
        caller=query.caller,
        called=query.called,
        user_id=current_user.id,
        customer_id=query.customer_id,
        direction=query.direction,
        status=query.status,
        start_time=query.start_time,
        end_time=query.end_time,
        min_duration=query.min_duration,
        max_duration=query.max_duration
    )
    return ResponseBase(data=result)
@router.get("/record/{record_id}", response_model=ResponseBase[CallRecordResponse], summary="获取通话记录详情")
async def get_call_record_detail(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/record/detail", method="GET"))
):
    """
    根据记录ID获取通话记录详情
    """
    record = await call_record_service.get(db, id=record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通话记录不存在"
        )
    # 检查权限
    if record.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看该通话记录"
        )
    return ResponseBase(data=record)
@router.delete("/record/delete/{record_id}", response_model=ResponseBase, summary="删除通话记录")
async def delete_call_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/record/delete", method="DELETE"))
):
    """
    删除通话记录（软删除）
    """
    record = await call_record_service.get(db, id=record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通话记录不存在"
        )
    await call_record_service.remove(db, id=record_id)
    return ResponseBase(message="删除通话记录成功")
@router.get("/record/download/{record_id}", summary="下载通话录音")
async def download_call_recording(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    下载通话录音文件
    """
    record = await call_record_service.get(db, id=record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通话记录不存在"
        )
    if not record.recording_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="录音文件不存在"
        )
    # TODO: 实现文件下载逻辑
    return ResponseBase(data={"url": record.recording_url}, message="下载链接已生成")
# 呼叫任务相关接口
@router.get("/task/list", response_model=ResponseBase[PageResponse[CallTaskResponse]], summary="获取呼叫任务列表")
async def get_call_task_list(
    query: CallTaskQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/task/list", method="GET"))
):
    """
    获取呼叫任务列表
    """
    filters = {}
    if query.name:
        filters["name"] = query.name
    if query.type is not None:
        filters["type"] = query.type
    if query.status is not None:
        filters["status"] = query.status
    if query.created_by is not None:
        filters["created_by"] = query.created_by
    # 如果不是管理员，只能查看自己创建的任务
    if not current_user.is_superuser:
        filters["created_by"] = current_user.id
    result = await call_task_service.get_multi(
        db,
        page=query.page,
        page_size=query.page_size,
        filters=filters
    )
    return ResponseBase(data=result)
@router.get("/task/my-list", response_model=ResponseBase[List[CallTaskResponse]], summary="获取我的呼叫任务")
async def get_my_call_task_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户参与的呼叫任务
    """
    tasks = await call_task_service.get_by_user_id(db, user_id=current_user.id)
    return ResponseBase(data=tasks)
@router.post("/task/create", response_model=ResponseBase[CallTaskResponse], summary="创建呼叫任务")
async def create_call_task(
    task_in: CallTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/task/create", method="POST"))
):
    """
    创建新的呼叫任务
    """
    task_data = task_in.model_dump()
    task_data["created_by"] = current_user.id
    task_data["total_count"] = len(task_in.customer_ids)
    task = await call_task_service.create(db, obj_in=task_data)
    logger.info(f"创建呼叫任务成功: {task.name}")
    return ResponseBase(data=task, message="创建呼叫任务成功")
@router.post("/task/control", response_model=ResponseBase, summary="控制呼叫任务")
async def control_call_task(
    control_in: CallTaskControl,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/task/control", method="POST"))
):
    """
    控制呼叫任务：启动、暂停、停止、恢复
    """
    task = await call_task_service.get(db, id=control_in.task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    # 检查权限
    if task.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作该任务"
        )
    status_map = {
        "start": 2,
        "pause": 3,
        "stop": 5,
        "resume": 2
    }
    if control_in.action not in status_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的操作类型"
        )
    task.status = status_map[control_in.action]
    await db.commit()
    await db.refresh(task)
    # 如果是启动任务，异步执行任务
    if control_in.action == "start":
        asyncio.create_task(execute_call_task(task.id, db))
    message = {
        "start": "任务已启动",
        "pause": "任务已暂停",
        "stop": "任务已停止",
        "resume": "任务已恢复"
    }[control_in.action]
    return ResponseBase(message=message)
async def execute_call_task(task_id: int, db: AsyncSession):
    """
    异步执行呼叫任务
    """
    try:
        task = await call_task_service.get(db, id=task_id)
        if not task or task.status != 2:  # 不是执行中状态
            return
        # TODO: 实现呼叫任务执行逻辑
        logger.info(f"开始执行呼叫任务: {task.name}")
    except Exception as e:
        logger.error(f"执行呼叫任务异常: {str(e)}", exc_info=True)
@router.delete("/task/delete/{task_id}", response_model=ResponseBase, summary="删除呼叫任务")
async def delete_call_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/task/delete", method="DELETE"))
):
    """
    删除呼叫任务
    """
    task = await call_task_service.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    if task.status == 2:  # 执行中状态不能删除
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="执行中的任务不能删除"
        )
    await call_task_service.remove(db, id=task_id)
    return ResponseBase(message="删除呼叫任务成功")
# 话术相关接口
@router.get("/script/category/list", response_model=ResponseBase[List[CallScriptCategoryResponse]], summary="获取话术分类列表")
async def get_script_category_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有话术分类
    """
    categories = await call_script_category_service.get_all(db)
    # 构建树形结构
    def build_tree(parent_id: int = 0):
        tree = []
        for category in categories:
            if category.parent_id == parent_id:
                children = build_tree(category.id)
                if children:
                    category.children = children
                tree.append(category)
        return tree
    tree = build_tree()
    return ResponseBase(data=tree)
@router.post("/script/category/create", response_model=ResponseBase[CallScriptCategoryResponse], summary="创建话术分类")
async def create_script_category(
    category_in: CallScriptCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/script/category/create", method="POST"))
):
    """
    创建新的话术分类
    """
    category = await call_script_category_service.create(db, obj_in=category_in)
    return ResponseBase(data=category, message="创建分类成功")
@router.get("/script/list", response_model=ResponseBase[PageResponse[CallScriptResponse]], summary="获取话术列表")
async def get_script_list(
    query: CallScriptQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取话术列表
    """
    filters = {}
    if query.name:
        filters["name"] = query.name
    if query.type is not None:
        filters["type"] = query.type
    if query.category_id is not None:
        filters["category_id"] = query.category_id
    if query.status is not None:
        filters["status"] = query.status
    result = await call_script_service.get_multi(
        db,
        page=query.page,
        page_size=query.page_size,
        filters=filters
    )
    return ResponseBase(data=result)
@router.get("/script/category/{category_id}", response_model=ResponseBase[List[CallScriptResponse]], summary="获取分类下的话术")
async def get_scripts_by_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定分类下的所有话术
    """
    scripts = await call_script_service.get_by_category_id(db, category_id=category_id)
    return ResponseBase(data=scripts)
@router.post("/script/create", response_model=ResponseBase[CallScriptResponse], summary="创建话术")
async def create_script(
    script_in: CallScriptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/script/create", method="POST"))
):
    """
    创建新的话术
    """
    script_data = script_in.model_dump()
    script_data["created_by"] = current_user.id
    script = await call_script_service.create(db, obj_in=script_data)
    logger.info(f"创建话术成功: {script.name}")
    return ResponseBase(data=script, message="创建话术成功")
@router.put("/script/update/{script_id}", response_model=ResponseBase[CallScriptResponse], summary="更新话术")
async def update_script(
    script_id: int,
    script_in: CallScriptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/script/update", method="PUT"))
):
    """
    更新话术信息
    """
    script = await call_script_service.get(db, id=script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="话术不存在"
        )
    script = await call_script_service.update(db, db_obj=script, obj_in=script_in)
    return ResponseBase(data=script, message="更新话术成功")
@router.delete("/script/delete/{script_id}", response_model=ResponseBase, summary="删除话术")
async def delete_script(
    script_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/script/delete", method="DELETE"))
):
    """
    删除话术
    """
    script = await call_script_service.get(db, id=script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="话术不存在"
        )
    await call_script_service.remove(db, id=script_id)
    return ResponseBase(message="删除话术成功")
# 主叫号码相关接口
@router.get("/caller-number/list", response_model=ResponseBase[List[CallerNumberResponse]], summary="获取主叫号码列表")
async def get_caller_number_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/caller-number/list", method="GET"))
):
    """
    获取所有可用的主叫号码
    """
    numbers = await caller_number_service.get_available(db)
    return ResponseBase(data=numbers)
@router.post("/caller-number/create", response_model=ResponseBase[CallerNumberResponse], summary="创建主叫号码")
async def create_caller_number(
    number_in: CallerNumberCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/caller-number/create", method="POST"))
):
    """
    添加新的主叫号码
    """
    # 检查号码是否已存在
    existing = await caller_number_service.get_multi(db, filters={"number": number_in.number})
    if existing["list"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该号码已存在"
        )
    number = await caller_number_service.create(db, obj_in=number_in)
    return ResponseBase(data=number, message="添加主叫号码成功")
@router.delete("/caller-number/delete/{number_id}", response_model=ResponseBase, summary="删除主叫号码")
async def delete_caller_number(
    number_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/caller-number/delete", method="DELETE"))
):
    """
    删除主叫号码
    """
    number = await caller_number_service.get(db, id=number_id)
    if not number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="号码不存在"
        )
    await caller_number_service.remove(db, id=number_id)
    return ResponseBase(message="删除主叫号码成功")
# 技能组相关接口
@router.get("/skill-group/list", response_model=ResponseBase[List[SkillGroupResponse]], summary="获取技能组列表")
async def get_skill_group_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有技能组
    """
    groups = await skill_group_service.get_all(db)
    return ResponseBase(data=groups)
@router.post("/skill-group/create", response_model=ResponseBase[SkillGroupResponse], summary="创建技能组")
async def create_skill_group(
    group_in: SkillGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/skill-group/create", method="POST"))
):
    """
    创建新的技能组
    """
    group = await skill_group_service.create(db, obj_in=group_in)
    return ResponseBase(data=group, message="创建技能组成功")
@router.put("/skill-group/update/{group_id}", response_model=ResponseBase[SkillGroupResponse], summary="更新技能组")
async def update_skill_group(
    group_id: int,
    group_in: SkillGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/skill-group/update", method="PUT"))
):
    """
    更新技能组信息
    """
    group = await skill_group_service.get(db, id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="技能组不存在"
        )
    group = await skill_group_service.update(db, db_obj=group, obj_in=group_in)
    return ResponseBase(data=group, message="更新技能组成功")
@router.delete("/skill-group/delete/{group_id}", response_model=ResponseBase, summary="删除技能组")
async def delete_skill_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/skill-group/delete", method="DELETE"))
):
    """
    删除技能组
    """
    group = await skill_group_service.get(db, id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="技能组不存在"
        )
    await skill_group_service.remove(db, id=group_id)
    return ResponseBase(message="删除技能组成功")
# 黑名单相关接口
@router.get("/black-list/list", response_model=ResponseBase[PageResponse[BlackListResponse]], summary="获取黑名单列表")
async def get_black_list(
    query: BlackListQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/black-list/list", method="GET"))
):
    """
    获取黑名单列表
    """
    filters = {}
    if query.phone:
        filters["phone"] = query.phone
    if query.type is not None:
        filters["type"] = query.type
    if query.source:
        filters["source"] = query.source
    result = await black_list_service.get_multi(
        db,
        page=query.page,
        page_size=query.page_size,
        filters=filters
    )
    return ResponseBase(data=result)
@router.post("/black-list/create", response_model=ResponseBase[BlackListResponse], summary="添加黑名单")
async def create_black_list(
    black_in: BlackListCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/black-list/create", method="POST"))
):
    """
    添加号码到黑名单
    """
    # 检查号码是否已在黑名单
    if await black_list_service.exists_by_phone(db, phone=black_in.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该号码已在黑名单中"
        )
    black_data = black_in.model_dump()
    black_data["created_by"] = current_user.id
    black = await black_list_service.create(db, obj_in=black_data)
    logger.info(f"添加黑名单成功: {black.phone}")
    return ResponseBase(data=black, message="添加黑名单成功")
@router.delete("/black-list/delete/{black_id}", response_model=ResponseBase, summary="移除黑名单")
async def delete_black_list(
    black_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/black-list/delete", method="DELETE"))
):
    """
    从黑名单中移除号码
    """
    black = await black_list_service.get(db, id=black_id)
    if not black:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    await black_list_service.remove(db, id=black_id)
    logger.info(f"移除黑名单成功: {black.phone}")
    return ResponseBase(message="移除黑名单成功")
@router.post("/black-list/check", response_model=ResponseBase[Dict[str, bool]], summary="检查号码是否在黑名单")
async def check_black_list(
    phone: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    检查指定号码是否在黑名单中
    """
    exists = await black_list_service.exists_by_phone(db, phone=phone)
    return ResponseBase(data={"exists": exists})
# IVR配置相关接口
@router.get("/ivr/list", response_model=ResponseBase[List[IVRConfigResponse]], summary="获取IVR配置列表")
async def get_ivr_config_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/ivr/list", method="GET"))
):
    """
    获取所有IVR配置
    """
    configs = await ivr_config_service.get_multi(db, filters={"status": True})
    return ResponseBase(data=configs["list"])
@router.post("/ivr/create", response_model=ResponseBase[IVRConfigResponse], summary="创建IVR配置")
async def create_ivr_config(
    ivr_in: IVRConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/ivr/create", method="POST"))
):
    """
    创建新的IVR配置
    """
    # 检查接入号码是否已配置
    if ivr_in.number:
        existing = await ivr_config_service.get_by_number(db, number=ivr_in.number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该接入号码已配置IVR"
            )
    ivr = await ivr_config_service.create(db, obj_in=ivr_in)
    return ResponseBase(data=ivr, message="创建IVR配置成功")
@router.put("/ivr/update/{ivr_id}", response_model=ResponseBase[IVRConfigResponse], summary="更新IVR配置")
async def update_ivr_config(
    ivr_id: int,
    ivr_in: IVRConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/ivr/update", method="PUT"))
):
    """
    更新IVR配置
    """
    ivr = await ivr_config_service.get(db, id=ivr_id)
    if not ivr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IVR配置不存在"
        )
    # 检查接入号码冲突
    if ivr_in.number and ivr_in.number != ivr.number:
        existing = await ivr_config_service.get_by_number(db, number=ivr_in.number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该接入号码已配置IVR"
            )
    ivr = await ivr_config_service.update(db, db_obj=ivr, obj_in=ivr_in)
    return ResponseBase(data=ivr, message="更新IVR配置成功")
@router.delete("/ivr/delete/{ivr_id}", response_model=ResponseBase, summary="删除IVR配置")
async def delete_ivr_config(
    ivr_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/call/ivr/delete", method="DELETE"))
):
    """
    删除IVR配置
    """
    ivr = await ivr_config_service.get(db, id=ivr_id)
    if not ivr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IVR配置不存在"
        )
    await ivr_config_service.remove(db, id=ivr_id)
    return ResponseBase(message="删除IVR配置成功")
# 统计相关接口
@router.get("/statistics", response_model=ResponseBase[CallStatistics], summary="获取通话统计数据")
async def get_call_statistics(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取通话统计数据
    """
    # 如果不是管理员，只能查看自己的统计
    if not current_user.is_superuser:
        user_id = current_user.id
    # TODO: 实现统计逻辑
    statistics = CallStatistics(
        total_calls=0,
        answered_calls=0,
        answer_rate=0.0,
        total_duration=0,
        avg_duration=0.0,
        success_calls=0,
        failed_calls=0,
        busy_calls=0,
        no_answer_calls=0,
        customer_reject_calls=0
    )
    return ResponseBase(data=statistics)


@router.post("/record/{call_id}/recognize", response_model=ResponseBase, summary="识别通话录音")
async def recognize_call_record(
    call_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    识别通话录音内容，将录音转为文本
    """
    call_record = await call_record_service.get_by_call_id(db, call_id=call_id)
    if not call_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通话记录不存在"
        )

    # 检查权限
    if call_record.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作该通话"
        )

    try:
        from app.services.call_recognition_service import CallRecognitionService
        text = await CallRecognitionService.recognize_call_audio(call_record)
        return ResponseBase(data={"text": text}, message="录音识别成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")


@router.post("/record/{call_id}/analyze", response_model=ResponseBase, summary="分析通话内容")
async def analyze_call_record(
    call_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    分析通话内容，提取意图、情绪、关键信息等
    """
    call_record = await call_record_service.get_by_call_id(db, call_id=call_id)
    if not call_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通话记录不存在"
        )

    # 检查权限
    if call_record.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作该通话"
        )

    try:
        from app.services.call_recognition_service import CallRecognitionService
        result = await CallRecognitionService.analyze_call_content(call_record)
        return ResponseBase(data=result, message="内容分析成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

