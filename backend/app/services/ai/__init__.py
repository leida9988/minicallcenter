"""
AI服务模块
提供ASR、TTS、大模型等AI能力的抽象接口和多种提供商实现
"""
from .base import ASRService, TTSService, LLMService, ASRResult, TTSResult, LLMResult, LLMMessage
from .factory import AIServiceFactory
from .providers import mock, aliyun

# 注册所有内置提供商
mock.register_builtin_providers()
aliyun.register_builtin_providers()

__all__ = [
    "ASRService",
    "TTSService",
    "LLMService",
    "ASRResult",
    "TTSResult",
    "LLMResult",
    "LLMMessage",
    "AIServiceFactory",
]
