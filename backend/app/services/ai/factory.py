from typing import Type, Dict, Any
from functools import lru_cache
from .base import ASRService, TTSService, LLMService
from ...core.config import settings


class AIServiceFactory:
    """AI服务工厂类"""

    _asr_providers: Dict[str, Type[ASRService]] = {}
    _tts_providers: Dict[str, Type[TTSService]] = {}
    _llm_providers: Dict[str, Type[LLMService]] = {}

    @classmethod
    def register_asr_provider(cls, name: str, provider: Type[ASRService]):
        """注册ASR服务提供商"""
        cls._asr_providers[name.lower()] = provider

    @classmethod
    def register_tts_provider(cls, name: str, provider: Type[TTSService]):
        """注册TTS服务提供商"""
        cls._tts_providers[name.lower()] = provider

    @classmethod
    def register_llm_provider(cls, name: str, provider: Type[LLMService]):
        """注册LLM服务提供商"""
        cls._llm_providers[name.lower()] = provider

    @classmethod
    @lru_cache(maxsize=None)
    def get_asr_service(cls, provider_name: Optional[str] = None) -> ASRService:
        """
        获取ASR服务实例

        Args:
            provider_name: 提供商名称，默认使用配置中的ASR_PROVIDER

        Returns:
            ASR服务实例
        """
        provider_name = provider_name or settings.ASR_PROVIDER
        provider_class = cls._asr_providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"不支持的ASR提供商: {provider_name}")

        # 根据提供商名称获取对应的配置
        config = getattr(settings, f"ASR_{provider_name.upper()}_CONFIG", {})
        return provider_class(**config)

    @classmethod
    @lru_cache(maxsize=None)
    def get_tts_service(cls, provider_name: Optional[str] = None) -> TTSService:
        """
        获取TTS服务实例

        Args:
            provider_name: 提供商名称，默认使用配置中的TTS_PROVIDER

        Returns:
            TTS服务实例
        """
        provider_name = provider_name or settings.TTS_PROVIDER
        provider_class = cls._tts_providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"不支持的TTS提供商: {provider_name}")

        # 根据提供商名称获取对应的配置
        config = getattr(settings, f"TTS_{provider_name.upper()}_CONFIG", {})
        return provider_class(**config)

    @classmethod
    @lru_cache(maxsize=None)
    def get_llm_service(cls, provider_name: Optional[str] = None) -> LLMService:
        """
        获取LLM服务实例

        Args:
            provider_name: 提供商名称，默认使用配置中的LLM_PROVIDER

        Returns:
            LLM服务实例
        """
        provider_name = provider_name or settings.LLM_PROVIDER
        provider_class = cls._llm_providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"不支持的LLM提供商: {provider_name}")

        # 根据提供商名称获取对应的配置
        config = getattr(settings, f"LLM_{provider_name.upper()}_CONFIG", {})
        return provider_class(**config)


# 注册内置的服务提供商
def register_builtin_providers():
    """注册内置的AI服务提供商"""
    # 这里会在各个provider实现文件中调用注册
    pass
