from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
class ASRTask(BaseModel):
    __tablename__ = "ai_asr_task"
    task_id = Column(String(50), unique=True, index=True, comment="任务ID")
    call_id = Column(String(50), index=True, comment="通话ID")
    audio_url = Column(String(255), comment="音频文件URL")
    audio_path = Column(String(255), comment="音频文件路径")
    audio_duration = Column(Integer, comment="音频时长(秒)")
    language = Column(String(10), default="zh-CN", comment="语言")
    status = Column(Integer, default=1, comment="状态：1-待处理 2-处理中 3-成功 4-失败")
    result = Column(Text, comment="识别结果")
    word_result = Column(JSON, comment="词级识别结果")
    confidence = Column(Integer, comment="置信度(%)")
    error_msg = Column(String(255), comment="错误信息")
    cost_time = Column(Integer, comment="处理耗时(ms)")
    provider = Column(String(50), comment="服务提供商")
    callback_url = Column(String(255), comment="回调URL")
class TTSTask(BaseModel):
    __tablename__ = "ai_tts_task"
    task_id = Column(String(50), unique=True, index=True, comment="任务ID")
    text = Column(Text, nullable=False, comment="待合成文本")
    voice = Column(String(50), default="female", comment="音色")
    language = Column(String(10), default="zh-CN", comment="语言")
    speed = Column(Integer, default=100, comment="语速(%)")
    pitch = Column(Integer, default=100, comment="音调(%)")
    volume = Column(Integer, default=100, comment="音量(%)")
    format = Column(String(10), default="wav", comment="音频格式")
    status = Column(Integer, default=1, comment="状态：1-待处理 2-处理中 3-成功 4-失败")
    audio_url = Column(String(255), comment="合成音频URL")
    audio_duration = Column(Integer, comment="音频时长(秒)")
    error_msg = Column(String(255), comment="错误信息")
    cost_time = Column(Integer, comment="处理耗时(ms)")
    provider = Column(String(50), comment="服务提供商")
class LLMRequest(BaseModel):
    __tablename__ = "ai_llm_request"
    request_id = Column(String(50), unique=True, index=True, comment="请求ID")
    user_id = Column(Integer, ForeignKey("system_user.id"), comment="用户ID")
    model = Column(String(50), comment="模型名称")
    prompt = Column(Text, comment="输入提示")
    messages = Column(JSON, comment="对话历史")
    temperature = Column(Integer, default=70, comment="温度(%)")
    max_tokens = Column(Integer, default=2000, comment="最大生成长度")
    stream = Column(Boolean, default=False, comment="是否流式返回")
    status = Column(Integer, default=1, comment="状态：1-待处理 2-处理中 3-成功 4-失败")
    response = Column(Text, comment="响应内容")
    usage = Column(JSON, comment="Token使用情况")
    error_msg = Column(String(255), comment="错误信息")
    cost_time = Column(Integer, comment="处理耗时(ms)")
    provider = Column(String(50), comment="服务提供商")
    # 关联
    user = relationship("User")
class QualityCheckTask(BaseModel):
    __tablename__ = "ai_quality_check_task"
    task_id = Column(String(50), unique=True, index=True, comment="任务ID")
    call_id = Column(String(50), index=True, comment="通话ID")
    asr_text = Column(Text, comment="ASR识别文本")
    rules = Column(JSON, comment="质检规则")
    status = Column(Integer, default=1, comment="状态：1-待处理 2-处理中 3-成功 4-失败")
    score = Column(Integer, comment="质检分数")
    result = Column(JSON, comment="质检结果")
    hit_rules = Column(JSON, comment="命中的规则")
    suggestion = Column(Text, comment="改进建议")
    error_msg = Column(String(255), comment="错误信息")
    cost_time = Column(Integer, comment="处理耗时(ms)")
    created_by = Column(Integer, ForeignKey("system_user.id"), comment="创建人ID")
    # 关联
    created_user = relationship("User", foreign_keys=[created_by])
class QualityCheckRule(BaseModel):
    __tablename__ = "ai_quality_check_rule"
    name = Column(String(100), nullable=False, comment="规则名称")
    description = Column(String(255), comment="规则描述")
    type = Column(Integer, default=1, comment="规则类型：1-关键词检测 2-话术规范 3-情绪检测 4-敏感词检测")
    content = Column(JSON, nullable=False, comment="规则内容")
    score = Column(Integer, default=10, comment="扣分值")
    level = Column(Integer, default=2, comment="严重等级：1-一般 2-警告 3-严重")
    category_id = Column(Integer, ForeignKey("ai_quality_check_category.id"), comment="分类ID")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(Boolean, default=True, comment="状态")
    hit_count = Column(Integer, default=0, comment="命中次数")
    # 关联
    category = relationship("QualityCheckCategory")
class QualityCheckCategory(BaseModel):
    __tablename__ = "ai_quality_check_category"
    name = Column(String(50), nullable=False, comment="分类名称")
    description = Column(String(255), comment="分类描述")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(Boolean, default=True, comment="状态")
class AIServiceConfig(BaseModel):
    __tablename__ = "ai_service_config"
    service_type = Column(String(20), nullable=False, comment="服务类型：asr, tts, llm")
    provider = Column(String(50), nullable=False, comment="服务提供商")
    name = Column(String(50), nullable=False, comment="配置名称")
    config = Column(JSON, nullable=False, comment="配置内容")
    is_default = Column(Boolean, default=False, comment="是否默认配置")
    status = Column(Boolean, default=True, comment="状态")
    priority = Column(Integer, default=0, comment="优先级")
    remark = Column(String(255), comment="备注")
