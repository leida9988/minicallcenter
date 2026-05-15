from typing import Any, Dict, List, Optional, Type, Union
from pydantic import BaseModel, Field
from datetime import datetime
import json
from enum import Enum
from functools import lru_cache
from ..models.system import SystemConfig
from ..db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession


class FieldType(str, Enum):
    """字段类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    SELECT = "select"
    MULTISELECT = "multiselect"
    PHONE = "phone"
    EMAIL = "email"
    TEXTAREA = "textarea"
    RICH_TEXT = "rich_text"
    FILE = "file"
    IMAGE = "image"


class FieldConfig(BaseModel):
    """字段配置"""
    key: str = Field(..., description="字段唯一标识")
    label: str = Field(..., description="字段显示名称")
    type: FieldType = Field(..., description="字段类型")
    required: bool = Field(False, description="是否必填")
    default: Any = Field(None, description="默认值")
    placeholder: Optional[str] = Field(None, description="占位提示文本")
    options: Optional[List[Dict[str, Any]]] = Field(None, description="选择类型的选项")
    validation_rules: Optional[List[Dict[str, Any]]] = Field(None, description="验证规则")
    show_in_list: bool = Field(True, description="是否在列表页显示")
    show_in_detail: bool = Field(True, description="是否在详情页显示")
    show_in_form: bool = Field(True, description="是否在表单页显示")
    sortable: bool = Field(False, description="是否可排序")
    searchable: bool = Field(False, description="是否可搜索")
    group: Optional[str] = Field(None, description="字段分组")
    order: int = Field(0, description="显示顺序")
    permissions: Optional[List[str]] = Field(None, description="访问权限，需要的角色标识")


class FormConfig(BaseModel):
    """表单配置"""
    name: str = Field(..., description="表单名称")
    description: Optional[str] = Field(None, description="表单描述")
    fields: List[FieldConfig] = Field(..., description="字段列表")
    layout: Optional[Dict[str, Any]] = Field(None, description="表单布局配置")
    submit_button_text: str = Field("提交", description="提交按钮文本")
    reset_button_text: str = Field("重置", description="重置按钮文本")
    success_message: str = Field("提交成功", description="提交成功提示")
    submit_url: Optional[str] = Field(None, description="提交接口地址")


class FlowConfig(BaseModel):
    """流程配置"""
    name: str = Field(..., description="流程名称")
    description: Optional[str] = Field(None, description="流程描述")
    stages: List[Dict[str, Any]] = Field(..., description="流程阶段列表")
    transitions: List[Dict[str, Any]] = Field(..., description="状态转换规则")
    permissions: Optional[Dict[str, List[str]]] = Field(None, description="各阶段权限配置")
    auto_actions: Optional[List[Dict[str, Any]]] = Field(None, description="自动执行的动作配置")


class ScriptConfig(BaseModel):
    """话术配置"""
    id: str = Field(..., description="话术唯一标识")
    name: str = Field(..., description="话术名称")
    category: str = Field(..., description="话术分类")
    content: str = Field(..., description="话术内容，支持变量插值")
    variables: Optional[List[Dict[str, Any]]] = Field(None, description="支持的变量列表")
    conditions: Optional[List[Dict[str, Any]]] = Field(None, description="触发条件")
    keywords: Optional[List[str]] = Field(None, description="关键词，用于智能推荐")
    priority: int = Field(0, description="优先级，越高越先推荐")
    enabled: bool = Field(True, description="是否启用")


class ConfigEngine:
    """配置引擎"""

    @staticmethod
    async def get_config(db: AsyncSession, config_key: str, default: Any = None) -> Any:
        """
        获取系统配置

        Args:
            db: 数据库会话
            config_key: 配置键名
            default: 默认值

        Returns:
            配置值
        """
        config = await SystemConfig.get_by_key(db, config_key)
        if not config:
            return default

        try:
            return json.loads(config.config_value)
        except json.JSONDecodeError:
            return config.config_value

    @staticmethod
    async def set_config(db: AsyncSession, config_key: str, config_value: Any, description: Optional[str] = None):
        """
        设置系统配置

        Args:
            db: 数据库会话
            config_key: 配置键名
            config_value: 配置值
            description: 配置描述
        """
        if isinstance(config_value, (dict, list)):
            config_value = json.dumps(config_value, ensure_ascii=False)
        else:
            config_value = str(config_value)

        existing = await SystemConfig.get_by_key(db, config_key)
        if existing:
            existing.config_value = config_value
            if description is not None:
                existing.description = description
            existing.updated_at = datetime.now()
            await existing.save(db)
        else:
            config = SystemConfig(
                config_key=config_key,
                config_value=config_value,
                description=description
            )
            await config.save(db)

        # 清除缓存
        ConfigEngine.get_config.cache_clear()

    @staticmethod
    async def get_fields_config(db: AsyncSession, module: str) -> List[FieldConfig]:
        """
        获取指定模块的字段配置

        Args:
            db: 数据库会话
            module: 模块名称，如customer、call等

        Returns:
            字段配置列表
        """
        config_key = f"fields_{module}"
        fields_data = await ConfigEngine.get_config(db, config_key, [])
        return [FieldConfig(**field) for field in fields_data]

    @staticmethod
    async def save_fields_config(db: AsyncSession, module: str, fields: List[FieldConfig]):
        """
        保存模块的字段配置

        Args:
            db: 数据库会话
            module: 模块名称
            fields: 字段配置列表
        """
        config_key = f"fields_{module}"
        fields_data = [field.model_dump() for field in fields]
        await ConfigEngine.set_config(db, config_key, fields_data, f"{module}模块字段配置")

    @staticmethod
    async def get_form_config(db: AsyncSession, form_name: str) -> Optional[FormConfig]:
        """
        获取表单配置

        Args:
            db: 数据库会话
            form_name: 表单名称

        Returns:
            表单配置
        """
        config_key = f"form_{form_name}"
        form_data = await ConfigEngine.get_config(db, config_key)
        if not form_data:
            return None
        return FormConfig(**form_data)

    @staticmethod
    async def save_form_config(db: AsyncSession, form_config: FormConfig):
        """
        保存表单配置

        Args:
            db: 数据库会话
            form_config: 表单配置
        """
        config_key = f"form_{form_config.name}"
        await ConfigEngine.set_config(db, config_key, form_config.model_dump(), f"表单【{form_config.name}】配置")

    @staticmethod
    async def get_flow_config(db: AsyncSession, flow_name: str) -> Optional[FlowConfig]:
        """
        获取流程配置

        Args:
            db: 数据库会话
            flow_name: 流程名称

        Returns:
            流程配置
        """
        config_key = f"flow_{flow_name}"
        flow_data = await ConfigEngine.get_config(db, config_key)
        if not flow_data:
            return None
        return FlowConfig(**flow_data)

    @staticmethod
    async def save_flow_config(db: AsyncSession, flow_config: FlowConfig):
        """
        保存流程配置

        Args:
            db: 数据库会话
            flow_config: 流程配置
        """
        config_key = f"flow_{flow_config.name}"
        await ConfigEngine.set_config(db, config_key, flow_config.model_dump(), f"流程【{flow_config.name}】配置")

    @staticmethod
    async def get_script_list(db: AsyncSession, category: Optional[str] = None) -> List[ScriptConfig]:
        """
        获取话术列表

        Args:
            db: 数据库会话
            category: 可选分类，不指定返回所有

        Returns:
            话术配置列表
        """
        config_key = "scripts"
        scripts_data = await ConfigEngine.get_config(db, config_key, [])
        scripts = [ScriptConfig(**script) for script in scripts_data]

        if category:
            scripts = [s for s in scripts if s.category == category and s.enabled]

        # 按优先级排序
        scripts.sort(key=lambda x: (-x.priority, x.name))
        return scripts

    @staticmethod
    async def save_script(db: AsyncSession, script: ScriptConfig):
        """
        保存话术配置

        Args:
            db: 数据库会话
            script: 话术配置
        """
        scripts = await ConfigEngine.get_script_list(db)

        # 查找是否已存在
        exists = False
        for i, s in enumerate(scripts):
            if s.id == script.id:
                scripts[i] = script
                exists = True
                break

        if not exists:
            scripts.append(script)

        # 保存
        scripts_data = [s.model_dump() for s in scripts]
        await ConfigEngine.set_config(db, "scripts", scripts_data, "话术配置列表")

    @staticmethod
    async def delete_script(db: AsyncSession, script_id: str):
        """
        删除话术

        Args:
            db: 数据库会话
            script_id: 话术ID
        """
        scripts = await ConfigEngine.get_script_list(db)
        scripts = [s for s in scripts if s.id != script_id]

        # 保存
        scripts_data = [s.model_dump() for s in scripts]
        await ConfigEngine.set_config(db, "scripts", scripts_data, "话术配置列表")

    @staticmethod
    async def recommend_scripts(db: AsyncSession, keywords: List[str], limit: int = 5) -> List[ScriptConfig]:
        """
        根据关键词推荐相关话术

        Args:
            db: 数据库会话
            keywords: 关键词列表
            limit: 返回数量

        Returns:
            推荐的话术列表
        """
        scripts = await ConfigEngine.get_script_list(db)
        keywords = [k.lower() for k in keywords]

        # 计算匹配度
        matched_scripts = []
        for script in scripts:
            if not script.enabled:
                continue

            score = 0
            # 关键词匹配
            if script.keywords:
                for kw in script.keywords:
                    if kw.lower() in keywords:
                        score += 2
            # 内容匹配
            for kw in keywords:
                if kw in script.content.lower():
                    score += 1

            if score > 0:
                # 加上优先级权重
                score += script.priority
                matched_scripts.append((score, script))

        # 按匹配度排序
        matched_scripts.sort(key=lambda x: -x[0])
        return [s for _, s in matched_scripts[:limit]]


# 全局配置引擎实例
config_engine = ConfigEngine()
