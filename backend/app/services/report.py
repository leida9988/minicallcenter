from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.call import CallRecord
from app.models.customer import Customer, FollowRecord
from app.models.system import User, OperationLog
from app.utils.logger import logger
class ReportService:
    """
    统计报表服务
    """
    async def get_call_trend(
        self,
        db: AsyncSession,
        start_date: str,
        end_date: str,
        user_id: Optional[int] = None,
        group_by: str = "day"  # day, hour, week, month
    ) -> Dict[str, Any]:
        """
        获取通话趋势统计
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        # 构建查询
        query = select(
            func.date(CallRecord.start_time).label("date"),
            func.count(CallRecord.id).label("total_calls"),
            func.sum(func.if_(CallRecord.status == 2, 1, 0)).label("answered_calls"),
            func.sum(func.if_(CallRecord.status == 2, CallRecord.duration, 0)).label("total_duration"),
            func.count(func.distinct(CallRecord.customer_id)).label("contacted_customers")
        ).where(
            CallRecord.is_deleted == False,
            CallRecord.start_time >= start,
            CallRecord.start_time <= end
        )
        if user_id:
            query = query.where(CallRecord.user_id == user_id)
        # 按不同粒度分组
        if group_by == "hour":
            query = query.group_by(
                func.date(CallRecord.start_time),
                func.hour(CallRecord.start_time)
            ).order_by(
                func.date(CallRecord.start_time),
                func.hour(CallRecord.start_time)
            )
        elif group_by == "week":
            query = query.group_by(
                func.year(CallRecord.start_time),
                func.week(CallRecord.start_time)
            ).order_by(
                func.year(CallRecord.start_time),
                func.week(CallRecord.start_time)
            )
        elif group_by == "month":
            query = query.group_by(
                func.year(CallRecord.start_time),
                func.month(CallRecord.start_time)
            ).order_by(
                func.year(CallRecord.start_time),
                func.month(CallRecord.start_time)
            )
        else:  # day
            query = query.group_by(
                func.date(CallRecord.start_time)
            ).order_by(
                func.date(CallRecord.start_time)
            )
        result = await db.execute(query)
        rows = result.all()
        # 处理结果
        data = []
        total = {
            "total_calls": 0,
            "answered_calls": 0,
            "total_duration": 0,
            "contacted_customers": 0
        }
        for row in rows:
            if group_by == "hour":
                date_str = f"{row.date} {row.hour}:00"
            elif group_by == "week":
                date_str = f"{row.year}年第{row.week}周"
            elif group_by == "month":
                date_str = f"{row.year}年{row.month}月"
            else:
                date_str = row.date.strftime("%Y-%m-%d")
            answer_rate = (row.answered_calls / row.total_calls * 100) if row.total_calls > 0 else 0
            avg_duration = (row.total_duration / row.answered_calls) if row.answered_calls > 0 else 0
            item = {
                "date": date_str,
                "total_calls": row.total_calls,
                "answered_calls": row.answered_calls,
                "answer_rate": round(answer_rate, 2),
                "total_duration": row.total_duration,
                "avg_duration": round(avg_duration, 2),
                "contacted_customers": row.contacted_customers
            }
            data.append(item)
            # 累计总计
            total["total_calls"] += row.total_calls
            total["answered_calls"] += row.answered_calls
            total["total_duration"] += row.total_duration
            total["contacted_customers"] += row.contacted_customers
        # 计算总计的平均值
        total["answer_rate"] = round((total["answered_calls"] / total["total_calls"] * 100) if total["total_calls"] > 0 else 0, 2)
        total["avg_duration"] = round((total["total_duration"] / total["answered_calls"]) if total["answered_calls"] > 0 else 0, 2)
        return {
            "group_by": group_by,
            "start_date": start_date,
            "end_date": end_date,
            "total": total,
            "list": data
        }
    async def get_agent_performance(
        self,
        db: AsyncSession,
        start_date: str,
        end_date: str,
        department_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取坐席绩效统计
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        # 查询坐席通话数据
        query = select(
            CallRecord.user_id,
            User.username,
            User.nickname,
            func.count(CallRecord.id).label("total_calls"),
            func.sum(func.if_(CallRecord.status == 2, 1, 0)).label("answered_calls"),
            func.sum(func.if_(CallRecord.status == 2, CallRecord.duration, 0)).label("total_duration"),
            func.count(func.distinct(CallRecord.customer_id)).label("contacted_customers"),
            func.sum(func.if_(Customer.status == 3, 1, 0)).label("intention_customers"),
            func.sum(func.if_(Customer.status == 4, 1, 0)).label("deal_customers")
        ).outerjoin(
            Customer, CallRecord.customer_id == Customer.id
        ).outerjoin(
            User, CallRecord.user_id == User.id
        ).where(
            CallRecord.is_deleted == False,
            CallRecord.start_time >= start,
            CallRecord.start_time <= end,
            User.is_deleted == False
        )
        if department_id:
            query = query.where(User.department_id == department_id)
        query = query.group_by(CallRecord.user_id, User.username, User.nickname).order_by(func.count(CallRecord.id).desc())
        result = await db.execute(query)
        rows = result.all()
        # 查询跟进记录数据
        follow_query = select(
            FollowRecord.user_id,
            func.count(FollowRecord.id).label("total_follows"),
            func.count(func.distinct(FollowRecord.customer_id)).label("followed_customers")
        ).where(
            FollowRecord.is_deleted == False,
            FollowRecord.created_at >= start,
            FollowRecord.created_at <= end
        ).group_by(FollowRecord.user_id)
        follow_result = await db.execute(follow_query)
        follow_rows = {row.user_id: row for row in follow_result.all()}
        # 处理结果
        data = []
        total = {
            "total_calls": 0,
            "answered_calls": 0,
            "total_duration": 0,
            "contacted_customers": 0,
            "intention_customers": 0,
            "deal_customers": 0,
            "total_follows": 0,
            "followed_customers": 0
        }
        for row in rows:
            # 获取跟进数据
            follow_data = follow_rows.get(row.user_id, None)
            total_follows = follow_data.total_follows if follow_data else 0
            followed_customers = follow_data.followed_customers if follow_data else 0
            # 计算各项指标
            answer_rate = (row.answered_calls / row.total_calls * 100) if row.total_calls > 0 else 0
            avg_duration = (row.total_duration / row.answered_calls) if row.answered_calls > 0 else 0
            conversion_rate = (row.deal_customers / row.contacted_customers * 100) if row.contacted_customers > 0 else 0
            intention_rate = (row.intention_customers / row.contacted_customers * 100) if row.contacted_customers > 0 else 0
            item = {
                "user_id": row.user_id,
                "username": row.username,
                "nickname": row.nickname,
                "total_calls": row.total_calls,
                "answered_calls": row.answered_calls,
                "answer_rate": round(answer_rate, 2),
                "total_duration": row.total_duration,
                "avg_duration": round(avg_duration, 2),
                "contacted_customers": row.contacted_customers,
                "intention_customers": row.intention_customers,
                "intention_rate": round(intention_rate, 2),
                "deal_customers": row.deal_customers,
                "conversion_rate": round(conversion_rate, 2),
                "total_follows": total_follows,
                "followed_customers": followed_customers
            }
            data.append(item)
            # 累计总计
            total["total_calls"] += row.total_calls
            total["answered_calls"] += row.answered_calls
            total["total_duration"] += row.total_duration
            total["contacted_customers"] += row.contacted_customers
            total["intention_customers"] += row.intention_customers
            total["deal_customers"] += row.deal_customers
            total["total_follows"] += total_follows
            total["followed_customers"] += followed_customers
        # 计算总计的平均值
        total["answer_rate"] = round((total["answered_calls"] / total["total_calls"] * 100) if total["total_calls"] > 0 else 0, 2)
        total["avg_duration"] = round((total["total_duration"] / total["answered_calls"]) if total["answered_calls"] > 0 else 0, 2)
        total["conversion_rate"] = round((total["deal_customers"] / total["contacted_customers"] * 100) if total["contacted_customers"] > 0 else 0, 2)
        total["intention_rate"] = round((total["intention_customers"] / total["contacted_customers"] * 100) if total["contacted_customers"] > 0 else 0, 2)
        return {
            "start_date": start_date,
            "end_date": end_date,
            "department_id": department_id,
            "total": total,
            "list": data
        }
    async def get_customer_analysis(
        self,
        db: AsyncSession,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        获取客户分析统计
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        # 统计客户总量和新增量
        total_customers = await db.scalar(
            select(func.count(Customer.id)).where(Customer.is_deleted == False)
        )
        new_customers = await db.scalar(
            select(func.count(Customer.id)).where(
                Customer.is_deleted == False,
                Customer.created_at >= start,
                Customer.created_at <= end
            )
        )
        # 按客户状态统计
        status_query = select(
            Customer.status,
            func.count(Customer.id).label("count")
        ).where(
            Customer.is_deleted == False
        ).group_by(Customer.status)
        status_result = await db.execute(status_query)
        status_stats = {row.status: row.count for row in status_result.all()}
        # 按客户等级统计
        level_query = select(
            Customer.level,
            func.count(Customer.id).label("count")
        ).where(
            Customer.is_deleted == False
        ).group_by(Customer.level)
        level_result = await db.execute(level_query)
        level_stats = {row.level: row.count for row in level_result.all()}
        # 按来源统计
        source_query = select(
            Customer.source,
            func.count(Customer.id).label("count")
        ).where(
            Customer.is_deleted == False,
            Customer.source.isnot(None)
        ).group_by(Customer.source).order_by(func.count(Customer.id).desc())
        source_result = await db.execute(source_query)
        source_stats = [{"source": row.source, "count": row.count} for row in source_result.all()]
        # 按跟进情况统计
        follow_query = select(
            func.count(Customer.id).label("count"),
            func.if_(Customer.last_follow_time.isnot(None), 1, 0).label("has_follow")
        ).where(
            Customer.is_deleted == False
        ).group_by(func.if_(Customer.last_follow_time.isnot(None), 1, 0))
        follow_result = await db.execute(follow_query)
        follow_stats = {row.has_follow: row.count for row in follow_result.all()}
        # 计算跟进率
        followed = follow_stats.get(1, 0)
        not_followed = follow_stats.get(0, 0)
        follow_rate = (followed / (followed + not_followed) * 100) if (followed + not_followed) > 0 else 0
        # 客户转化漏斗
        total_leads = total_customers
        contacted = await db.scalar(
            select(func.count(func.distinct(CallRecord.customer_id))).where(
                CallRecord.is_deleted == False,
                CallRecord.status == 2,
                CallRecord.start_time >= start,
                CallRecord.start_time <= end
            )
        ) or 0
        intention = status_stats.get(3, 0)
        deal = status_stats.get(4, 0)
        funnel = [
            {"name": "线索总数", "value": total_leads},
            {"name": "已联系", "value": contacted},
            {"name": "有意向", "value": intention},
            {"name": "已成交", "value": deal}
        ]
        return {
            "start_date": start_date,
            "end_date": end_date,
            "overview": {
                "total_customers": total_customers,
                "new_customers": new_customers,
                "followed_customers": followed,
                "follow_rate": round(follow_rate, 2),
                "deal_customers": deal
            },
            "status_stats": [
                {"status": 1, "name": "待联系", "count": status_stats.get(1, 0)},
                {"status": 2, "name": "联系中", "count": status_stats.get(2, 0)},
                {"status": 3, "name": "有意向", "count": status_stats.get(3, 0)},
                {"status": 4, "name": "已成交", "count": status_stats.get(4, 0)},
                {"status": 5, "name": "已拒绝", "count": status_stats.get(5, 0)},
                {"status": 6, "name": "无效客户", "count": status_stats.get(6, 0)}
            ],
            "level_stats": [
                {"level": 1, "name": "普通客户", "count": level_stats.get(1, 0)},
                {"level": 2, "name": "VIP客户", "count": level_stats.get(2, 0)},
                {"level": 3, "name": "重要客户", "count": level_stats.get(3, 0)}
            ],
            "source_stats": source_stats,
            "conversion_funnel": funnel
        }
    async def get_call_hourly_distribution(
        self,
        db: AsyncSession,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        获取通话时段分布统计
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        # 按小时统计通话量和接通率
        query = select(
            extract('hour', CallRecord.start_time).label("hour"),
            func.count(CallRecord.id).label("total_calls"),
            func.sum(func.if_(CallRecord.status == 2, 1, 0)).label("answered_calls")
        ).where(
            CallRecord.is_deleted == False,
            CallRecord.start_time >= start,
            CallRecord.start_time <= end
        ).group_by(extract('hour', CallRecord.start_time)).order_by(extract('hour', CallRecord.start_time))
        result = await db.execute(query)
        rows = result.all()
        # 初始化24小时的数据
        hourly_data = [{"hour": i, "total_calls": 0, "answered_calls": 0, "answer_rate": 0} for i in range(24)]
        for row in rows:
            hour = int(row.hour)
            hourly_data[hour]["total_calls"] = row.total_calls
            hourly_data[hour]["answered_calls"] = row.answered_calls
            hourly_data[hour]["answer_rate"] = round((row.answered_calls / row.total_calls * 100) if row.total_calls > 0 else 0, 2)
        return {
            "start_date": start_date,
            "end_date": end_date,
            "data": hourly_data
        }
    async def get_operation_logs(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None,
        module: Optional[str] = None,
        operation: Optional[str] = None,
        status: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取操作日志列表
        """
        query = select(OperationLog).where(OperationLog.is_deleted == False)
        if user_id:
            query = query.where(OperationLog.user_id == user_id)
        if module:
            query = query.where(OperationLog.module.like(f"%{module}%"))
        if operation:
            query = query.where(OperationLog.operation.like(f"%{operation}%"))
        if status is not None:
            query = query.where(OperationLog.status == status)
        if start_time:
            query = query.where(OperationLog.created_at >= start_time)
        if end_time:
            query = query.where(OperationLog.created_at <= end_time)
        # 统计总数
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        # 分页查询
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(OperationLog.created_at.desc())
        result = await db.execute(query)
        logs = result.scalars().all()
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_page": (total + page_size - 1) // page_size if total > 0 else 0,
            "list": logs
        }
# 初始化服务
report_service = ReportService()
