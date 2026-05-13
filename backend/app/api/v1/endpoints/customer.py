from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
import io
from app.core.permission import PermissionChecker, get_current_active_user
from app.db.session import get_db
from app.models.system import User
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerQuery,
    CustomerAssign,
    CustomerImportResult,
    FollowRecordCreate,
    FollowRecordResponse,
    FollowRecordQuery,
    TagCreate,
    TagResponse,
    TagQuery,
    CustomerStatistics
)
from app.schemas.base import PageResponse, ResponseBase
from app.services.customer import customer_service, follow_record_service, tag_service
from app.utils.logger import logger
router = APIRouter()
# 客户管理相关接口
@router.get("/list", response_model=ResponseBase[PageResponse[CustomerResponse]], summary="获取客户列表")
async def get_customer_list(
    query: CustomerQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/list", method="GET"))
):
    """
    获取客户列表，支持分页和条件查询
    """
    result = await customer_service.get_list(
        db,
        page=query.page,
        page_size=query.page_size,
        keyword=query.keyword,
        status=query.status,
        level=query.level,
        tags=query.tags,
        assign_user_id=query.assign_user_id,
        start_time=query.start_time,
        end_time=query.end_time
    )
    return ResponseBase(data=result)
@router.get("/my-list", response_model=ResponseBase[PageResponse[CustomerResponse]], summary="获取我的客户列表")
async def get_my_customer_list(
    query: CustomerQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户负责的客户列表
    """
    result = await customer_service.get_list(
        db,
        page=query.page,
        page_size=query.page_size,
        keyword=query.keyword,
        status=query.status,
        level=query.level,
        tags=query.tags,
        assign_user_id=current_user.id,
        start_time=query.start_time,
        end_time=query.end_time
    )
    return ResponseBase(data=result)
@router.get("/{customer_id}", response_model=ResponseBase[CustomerResponse], summary="获取客户详情")
async def get_customer_detail(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/detail", method="GET"))
):
    """
    根据客户ID获取客户详情
    """
    customer = await customer_service.get_with_follow_records(db, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户不存在"
        )
    return ResponseBase(data=customer)
@router.post("/create", response_model=ResponseBase[CustomerResponse], summary="创建客户")
async def create_customer(
    customer_in: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/create", method="POST"))
):
    """
    创建新客户
    """
    # 检查手机号是否存在
    existing_customer = await customer_service.get_by_phone(db, phone=customer_in.phone)
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"手机号 {customer_in.phone} 已存在"
        )
    customer = await customer_service.create(db, obj_in=customer_in)
    logger.info(f"创建客户成功: {customer.name} - {customer.phone}")
    return ResponseBase(data=customer, message="创建客户成功")
@router.put("/update/{customer_id}", response_model=ResponseBase[CustomerResponse], summary="更新客户")
async def update_customer(
    customer_id: int,
    customer_in: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/update", method="PUT"))
):
    """
    更新客户信息
    """
    customer = await customer_service.get(db, id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户不存在"
        )
    # 检查手机号是否重复
    if customer_in.phone and customer_in.phone != customer.phone:
        existing_customer = await customer_service.get_by_phone(db, phone=customer_in.phone)
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"手机号 {customer_in.phone} 已存在"
            )
    customer = await customer_service.update(db, db_obj=customer, obj_in=customer_in)
    logger.info(f"更新客户成功: {customer.name} - {customer.phone}")
    return ResponseBase(data=customer, message="更新客户成功")
@router.delete("/delete/{customer_id}", response_model=ResponseBase, summary="删除客户")
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/delete", method="DELETE"))
):
    """
    删除客户（软删除）
    """
    customer = await customer_service.get(db, id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户不存在"
        )
    await customer_service.remove(db, id=customer_id)
    logger.info(f"删除客户成功: {customer.name} - {customer.phone}")
    return ResponseBase(message="删除客户成功")
@router.post("/assign", response_model=ResponseBase, summary="分配客户")
async def assign_customer(
    assign_in: CustomerAssign,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/assign", method="POST"))
):
    """
    批量分配客户给坐席
    """
    count = await customer_service.batch_assign(
        db,
        customer_ids=assign_in.customer_ids,
        user_id=assign_in.user_id,
        assign_by=current_user.id
    )
    return ResponseBase(message=f"成功分配 {count} 个客户")
@router.post("/recycle/{customer_id}", response_model=ResponseBase, summary="回收客户到公海")
async def recycle_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/recycle", method="POST"))
):
    """
    回收单个客户到公海池
    """
    customer = await customer_service.recycle_to_public_sea(db, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户不存在"
        )
    return ResponseBase(message="回收客户成功")
@router.post("/batch-recycle", response_model=ResponseBase, summary="批量回收客户到公海")
async def batch_recycle_customer(
    customer_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/batch-recycle", method="POST"))
):
    """
    批量回收客户到公海池
    """
    count = 0
    for customer_id in customer_ids:
        customer = await customer_service.recycle_to_public_sea(db, customer_id=customer_id)
        if customer:
            count += 1
    return ResponseBase(message=f"成功回收 {count} 个客户")
@router.post("/import", response_model=ResponseBase[CustomerImportResult], summary="批量导入客户")
async def import_customers(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/import", method="POST"))
):
    """
    批量导入客户，支持Excel文件
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请上传Excel文件"
        )
    try:
        content = await file.read()
        df = pd.read_excel(io.BytesIO(content))
        total = len(df)
        success = 0
        failed = 0
        errors = []
        for index, row in df.iterrows():
            try:
                phone = str(row.get('手机号', '')).strip()
                if not phone or len(phone) != 11:
                    raise ValueError("手机号格式错误")
                # 检查手机号是否存在
                existing = await customer_service.get_by_phone(db, phone=phone)
                if existing:
                    raise ValueError("手机号已存在")
                customer_in = CustomerCreate(
                    name=str(row.get('姓名', '')).strip(),
                    phone=phone,
                    gender=int(row.get('性别', 0)) if pd.notna(row.get('性别')) else 0,
                    age=int(row.get('年龄')) if pd.notna(row.get('年龄')) else None,
                    email=str(row.get('邮箱', '')).strip() if pd.notna(row.get('邮箱')) else None,
                    company=str(row.get('公司', '')).strip() if pd.notna(row.get('公司')) else None,
                    position=str(row.get('职位', '')).strip() if pd.notna(row.get('职位')) else None,
                    address=str(row.get('地址', '')).strip() if pd.notna(row.get('地址')) else None,
                    source=str(row.get('来源', '')).strip() if pd.notna(row.get('来源')) else None,
                    level=int(row.get('等级', 1)) if pd.notna(row.get('等级')) else 1,
                    description=str(row.get('备注', '')).strip() if pd.notna(row.get('备注')) else None
                )
                await customer_service.create(db, obj_in=customer_in)
                success += 1
            except Exception as e:
                failed += 1
                errors.append(f"第 {index + 2} 行：{str(e)}")
        result = CustomerImportResult(
            total=total,
            success=success,
            failed=failed,
            errors=errors
        )
        logger.info(f"导入客户完成: 总 {total} 条，成功 {success} 条，失败 {failed} 条")
        return ResponseBase(data=result, message="导入完成")
    except Exception as e:
        logger.error(f"导入客户失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入失败: {str(e)}"
        )
@router.get("/export", summary="导出客户数据")
async def export_customers(
    query: CustomerQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/export", method="GET"))
):
    """
    导出客户数据为Excel文件
    """
    # TODO: 实现导出功能
    return ResponseBase(message="导出功能开发中")
# 跟进记录相关接口
@router.get("/follow-record/list", response_model=ResponseBase[PageResponse[FollowRecordResponse]], summary="获取跟进记录列表")
async def get_follow_record_list(
    query: FollowRecordQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/follow-record/list", method="GET"))
):
    """
    获取跟进记录列表
    """
    if query.customer_id:
        result = await follow_record_service.get_by_customer_id(
            db,
            customer_id=query.customer_id,
            page=query.page,
            page_size=query.page_size
        )
    else:
        filters = {}
        if query.user_id:
            filters["user_id"] = query.user_id
        if query.type:
            filters["type"] = query.type
        result = await follow_record_service.get_multi(
            db,
            page=query.page,
            page_size=query.page_size,
            filters=filters
        )
    return ResponseBase(data=result)
@router.post("/follow-record/create", response_model=ResponseBase[FollowRecordResponse], summary="创建跟进记录")
async def create_follow_record(
    record_in: FollowRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新的跟进记录
    """
    # 检查客户是否存在
    customer = await customer_service.get(db, id=record_in.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="客户不存在"
        )
    record = await follow_record_service.create_record(db, obj_in=record_in, user_id=current_user.id)
    return ResponseBase(data=record, message="创建跟进记录成功")
@router.delete("/follow-record/delete/{record_id}", response_model=ResponseBase, summary="删除跟进记录")
async def delete_follow_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/follow-record/delete", method="DELETE"))
):
    """
    删除跟进记录
    """
    record = await follow_record_service.get(db, id=record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="跟进记录不存在"
        )
    await follow_record_service.remove(db, id=record_id)
    return ResponseBase(message="删除跟进记录成功")
# 标签相关接口
@router.get("/tag/list", response_model=ResponseBase[List[TagResponse]], summary="获取标签列表")
async def get_tag_list(
    type: int = 1,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有标签列表
    """
    tags = await tag_service.get_all(db, type=type)
    return ResponseBase(data=tags)
@router.post("/tag/create", response_model=ResponseBase[TagResponse], summary="创建标签")
async def create_tag(
    tag_in: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/tag/create", method="POST"))
):
    """
    创建新标签
    """
    try:
        tag = await tag_service.create_tag(db, obj_in=tag_in)
        return ResponseBase(data=tag, message="创建标签成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
@router.put("/tag/update/{tag_id}", response_model=ResponseBase[TagResponse], summary="更新标签")
async def update_tag(
    tag_id: int,
    tag_in: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/tag/update", method="PUT"))
):
    """
    更新标签信息
    """
    tag = await tag_service.get(db, id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    # 检查标签名称是否重复
    if tag_in.name and tag_in.name != tag.name:
        existing_tag = await tag_service.get_by_name(db, name=tag_in.name)
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"标签 {tag_in.name} 已存在"
            )
    tag = await tag_service.update(db, db_obj=tag, obj_in=tag_in)
    return ResponseBase(data=tag, message="更新标签成功")
@router.delete("/tag/delete/{tag_id}", response_model=ResponseBase, summary="删除标签")
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(path="/customer/tag/delete", method="DELETE"))
):
    """
    删除标签
    """
    tag = await tag_service.get(db, id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    await tag_service.remove(db, id=tag_id)
    return ResponseBase(message="删除标签成功")
# 统计相关接口
@router.get("/statistics", response_model=ResponseBase[CustomerStatistics], summary="获取客户统计数据")
async def get_customer_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取客户统计数据
    """
    # 总客户数
    total_count = await customer_service.count(db)
    # 今日新增
    from datetime import datetime, timedelta
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_new = await customer_service.count(db, filters={"created_at__ge": today_start})
    # 本周新增
    week_start = today - timedelta(days=today.weekday())
    week_new = await customer_service.count(db, filters={"created_at__ge": week_start})
    # 本月新增
    month_start = today.replace(day=1)
    month_new = await customer_service.count(db, filters={"created_at__ge": month_start})
    # 待跟进数
    follow_count = await customer_service.count(db, filters={"next_follow_time__lte": datetime.now()})
    # 有意向数
    intention_count = await customer_service.count(db, filters={"status": 3})
    # 已成交数
    deal_count = await customer_service.count(db, filters={"status": 4})
    # 无效客户数
    invalid_count = await customer_service.count(db, filters={"status": 6})
    # 转化率
    conversion_rate = (deal_count / total_count * 100) if total_count > 0 else 0
    statistics = CustomerStatistics(
        total_count=total_count,
        today_new=today_new,
        week_new=week_new,
        month_new=month_new,
        follow_count=follow_count,
        intention_count=intention_count,
        deal_count=deal_count,
        invalid_count=invalid_count,
        conversion_rate=round(conversion_rate, 2)
    )
    return ResponseBase(data=statistics)
