from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Any
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_active_user, get_current_superuser
from app.models.system import User
from app.core.config_engine import (
    config_engine,
    FieldConfig,
    FormConfig,
    FlowConfig,
    ScriptConfig
)

router = APIRouter(prefix="/config", tags=["配置管理"])


class ConfigItem(BaseModel):
    """配置项"""
    key: str
    value: Any
    description: Optional[str] = None


class FieldsConfigUpdate(BaseModel):
    """字段配置更新"""
    module: str
    fields: List[FieldConfig]


class ScriptQuery(BaseModel):
    """话术查询"""
    category: Optional[str] = None
    keyword: Optional[str] = None


@router.get("/system", summary="获取所有系统配置", dependencies=[Depends(get_current_superuser)])
async def get_system_configs(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有系统配置，需要超级管理员权限
    """
    from app.models.system import SystemConfig
    configs = await SystemConfig.get_all(db)
    return {
        "configs": [
            {
                "key": c.key,
                "value": c.value,
                "name": c.name,
                "description": c.description,
                "type": c.type,
                "sort": c.sort,
                "is_public": c.is_public,
                "created_at": c.created_at,
                "updated_at": c.updated_at
            }
            for c in configs
        ]
    }


@router.post("/system", summary="更新系统配置", dependencies=[Depends(get_current_superuser)])
async def update_system_config(
    config: ConfigItem,
    db: AsyncSession = Depends(get_db)
):
    """
    更新系统配置，需要超级管理员权限
    """
    await config_engine.set_config(db, config.key, config.value, config.description)
    return {"message": "配置更新成功"}


@router.get("/fields/{module}", summary="获取模块字段配置")
async def get_fields_config(
    module: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定模块的字段配置
    """
    fields = await config_engine.get_fields_config(db, module)
    return {"fields": [field.model_dump() for field in fields]}


@router.post("/fields", summary="保存模块字段配置", dependencies=[Depends(get_current_superuser)])
async def save_fields_config(
    request: FieldsConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    保存模块的字段配置，需要超级管理员权限
    """
    await config_engine.save_fields_config(db, request.module, request.fields)
    return {"message": "字段配置保存成功"}


@router.get("/form/{form_name}", summary="获取表单配置")
async def get_form_config(
    form_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定表单的配置
    """
    form = await config_engine.get_form_config(db, form_name)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="表单配置不存在"
        )
    return form.model_dump()


@router.post("/form", summary="保存表单配置", dependencies=[Depends(get_current_superuser)])
async def save_form_config(
    form_config: FormConfig,
    db: AsyncSession = Depends(get_db)
):
    """
    保存表单配置，需要超级管理员权限
    """
    await config_engine.save_form_config(db, form_config)
    return {"message": "表单配置保存成功"}


@router.get("/flow/{flow_name}", summary="获取流程配置")
async def get_flow_config(
    flow_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定流程的配置
    """
    flow = await config_engine.get_flow_config(db, flow_name)
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="流程配置不存在"
        )
    return flow.model_dump()


@router.post("/flow", summary="保存流程配置", dependencies=[Depends(get_current_superuser)])
async def save_flow_config(
    flow_config: FlowConfig,
    db: AsyncSession = Depends(get_db)
):
    """
    保存流程配置，需要超级管理员权限
    """
    await config_engine.save_flow_config(db, flow_config)
    return {"message": "流程配置保存成功"}


@router.get("/scripts", summary="获取话术列表")
async def get_script_list(
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取话术列表，可按分类和关键词筛选
    """
    scripts = await config_engine.get_script_list(db, category)

    if keyword:
        keyword = keyword.lower()
        scripts = [
            s for s in scripts
            if keyword in s.name.lower() or keyword in s.content.lower()
            or (s.keywords and any(keyword in kw.lower() for kw in s.keywords))
        ]

    return {"scripts": [s.model_dump() for s in scripts]}


@router.post("/scripts", summary="保存话术配置")
async def save_script(
    script: ScriptConfig,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    保存话术配置
    """
    await config_engine.save_script(db, script)
    return {"message": "话术保存成功"}


@router.delete("/scripts/{script_id}", summary="删除话术")
async def delete_script(
    script_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    删除话术，需要超级管理员权限
    """
    await config_engine.delete_script(db, script_id)
    return {"message": "话术删除成功"}


@router.post("/scripts/recommend", summary="智能推荐话术")
async def recommend_scripts(
    keywords: List[str],
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    根据关键词智能推荐相关话术
    """
    scripts = await config_engine.recommend_scripts(db, keywords, limit)
    return {"scripts": [s.model_dump() for s in scripts]}
