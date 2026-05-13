from typing import Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.core.permission import PermissionChecker, get_current_active_user
from app.db.session import get_db
from app.models.system import User
from app.models.call import CallRecord
from app.models.customer import FollowRecord
from app.schemas.report import (
    CallTrendResponse,
    AgentPerformanceResponse,
    CustomerAnalysisResponse,
    HourlyDistributionResponse,
    OperationLogItem,
    OperationLogQuery,
    DashboardStats
)
from app.schemas.base import PageResponse, ResponseBase
from app.services.report import report_service
from app.services.call import call_record_service
from app.services.customer import customer_service
router = APIRouter()
# 首页看板接口
@router.get("/dashboard", response_model=ResponseBase[DashboardStats], summary="获取首页统计看板数据")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取首页统计看板数据
    """
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    # 今日通话统计
    today_calls = await call_record_service.count(
        db,
        filters={
            "created_at__ge": today_start,
            "created_at__le": today_end,
            "user_id": current_user.id if not current_user.is_superuser else None
        }
    )
    # 今日接通数
    today_answered = await call_record_service.count(
        db,
        filters={
            "created_at__ge": today_start,
            "created_at__le": today_end,
            "status": 2,
            "user_id": current_user.id if not current_user.is_superuser else None
        }
    )
    # 今日通话时长
    today_duration_result = await db.execute(
        select(func.sum(CallRecord.duration)).where(
            CallRecord.is_deleted == False,
            CallRecord.created_at >= today_start,
            CallRecord.created_at <= today_end,
            CallRecord.user_id == current_user.id if not current_user.is_superuser else True
        )
    )
    today_duration = today_duration_result.scalar() or 0
    # 今日新增客户
    today_new_customers = await customer_service.count(
        db,
        filters={
            "created_at__ge": today_start,
            "created_at__le": today_end,
            "created_by": current_user.id if not current_user.is_superuser else None
        }
    )
    # 今日跟进次数
    today_follows_result = await db.execute(
        select(func.count(FollowRecord.id)).where(
            FollowRecord.is_deleted == False,
            FollowRecord.created_at >= today_start,
            FollowRecord.created_at <= today_end,
            FollowRecord.user_id == current_user.id if not current_user.is_superuser else True
        )
    )
    today_follows = today_follows_result.scalar() or 0
    # 待跟进客户数
    pending_customers = await customer_service.count(
        db,
        filters={
            "status": 1,
            "assign_user_id": current_user.id if not current_user.is_superuser else None
        }
    )
    # 意向客户总数
    intention_customers = await customer_service.count(
        db,
        filters={
            "status": 3,
            "assign_user_id": current_user.id if not current_user.is_superuser else None
        }
    )
    # 成交客户总数
    deal_customers = await customer_service.count(
        db,
        filters={
            "status": 4,
            "assign_user_id": current_user.id if not current_user.is_superuser else None
        }
    )
    # 客户总数
    total_customers = await customer_service.count(
        db,
        filters={
            "assign_user_id": current_user.id if not current_user.is_superuser else None
        }
    )
    # 坐席总数和在线数
    total_agents = await db.scalar(
        select(func.count(User.id)).where(User.is_deleted == False, User.is_active == True)
    )
    # TODO: 实现在线坐席统计
    online_agents = 0
    # 计算接通率
    today_answer_rate = (today_answered / today_calls * 100) if today_calls > 0 else 0
    stats = DashboardStats(
        today_calls=today_calls,
        today_answered=today_answered,
        today_answer_rate=round(today_answer_rate, 2),
        today_duration=today_duration,
        today_new_customers=today_new_customers,
        today_follows=today_follows,
        pending_customers=pending_customers,
        intention_customers=intention_customers,
        deal_customers=deal_customers,
        total_customers=total_customers,
        total_agents=total_agents,
        online_agents=online_agents
    )
    return ResponseBase(data=stats)
# 通话趋势相关接口
@router.get("/call/trend", response_model=ResponseBase[CallTrendResponse], summary="获取通话趋势统计")
async def get_call_trend(
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD"),
    user_id: Optional[int] = Query(None, description="用户ID，不填则查询所有"),
    group_by: str = Query("day", description="分组粒度：day, hour, week, month"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/report/call/trend", method="GET"))
):
    """
    获取通话趋势统计，支持按日、小时、周、月分组
    """
    # 如果不是管理员，只能查看自己的数据
    if not current_user.is_superuser:
        user_id = current_user.id
    result = await report_service.get_call_trend(
        db,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        group_by=group_by
    )
    return ResponseBase(data=result)
# 坐席绩效相关接口
@router.get("/agent/performance", response_model=ResponseBase[AgentPerformanceResponse], summary="获取坐席绩效统计")
async def get_agent_performance(
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD"),
    department_id: Optional[int] = Query(None, description="部门ID，不填则查询所有"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/report/agent/performance", method="GET"))
):
    """
    获取坐席绩效统计报表
    """
    result = await report_service.get_agent_performance(
        db,
        start_date=start_date,
        end_date=end_date,
        department_id=department_id
    )
    return ResponseBase(data=result)
# 客户分析相关接口
@router.get("/customer/analysis", response_model=ResponseBase[CustomerAnalysisResponse], summary="获取客户分析统计")
async def get_customer_analysis(
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/report/customer/analysis", method="GET"))
):
    """
    获取客户分析统计报表
    """
    result = await report_service.get_customer_analysis(
        db,
        start_date=start_date,
        end_date=end_date
    )
    return ResponseBase(data=result)
# 通话时段分布接口
@router.get("/call/hourly-distribution", response_model=ResponseBase[HourlyDistributionResponse], summary="获取通话时段分布统计")
async def get_call_hourly_distribution(
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/report/call/hourly-distribution", method="GET"))
):
    """
    获取通话时段分布统计，按24小时分布
    """
    result = await report_service.get_call_hourly_distribution(
        db,
        start_date=start_date,
        end_date=end_date
    )
    return ResponseBase(data=result)
# 操作日志相关接口
@router.get("/operation/logs", response_model=ResponseBase[PageResponse[OperationLogItem]], summary="获取操作日志列表")
async def get_operation_logs(
    query: OperationLogQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/report/operation/logs", method="GET"))
):
    """
    获取操作日志列表，支持分页和条件查询
    """
    # 如果不是管理员，只能查看自己的操作日志
    if not current_user.is_superuser:
        query.user_id = current_user.id
    result = await report_service.get_operation_logs(
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
# 数据导出相关接口
@router.post("/export/call-trend", summary="导出通话趋势报表")
async def export_call_trend(
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD"),
    user_id: Optional[int] = Query(None, description="用户ID，不填则查询所有"),
    group_by: str = Query("day", description="分组粒度：day, hour, week, month"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/report/export/call-trend", method="POST"))
):
    """
    导出通话趋势报表为Excel文件
    """
    # TODO: 实现导出功能
    return ResponseBase(message="导出功能开发中")
@router.post("/export/agent-performance", summary="导出坐席绩效报表")
async def export_agent_performance(
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD"),
    department_id: Optional[int] = Query(None, description="部门ID，不填则查询所有"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/report/export/agent-performance", method="POST"))
):
    """
    导出坐席绩效报表为Excel文件
    """
    # TODO: 实现导出功能
    return ResponseBase(message="导出功能开发中")
@router.post("/export/customer-analysis", summary="导出客户分析报表")
async def export_customer_analysis(
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/report/export/customer-analysis", method="POST"))
):
    """
    导出客户分析报表为Excel文件
    """
    # TODO: 实现导出功能
    return ResponseBase(message="导出功能开发中")
