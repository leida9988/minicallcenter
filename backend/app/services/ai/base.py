from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ASRResult(BaseModel):
    """ASR识别结果"""
    text: str
    confidence: float
    word_timestamps: Optional[List[Dict[str, Any]]] = None
    duration: Optional[float] = None
    success: bool = True
    error_msg: Optional[str] = None


class TTSResult(BaseModel):
    """TTS合成结果"""
    audio_url: str
    duration: Optional[float] = None
    success: bool = True
    error_msg: Optional[str] = None


class LLMMessage(BaseModel):
    """大模型消息"""
    role: str
    content: str


class LLMResult(BaseModel):
    """大模型返回结果"""
    content: str
    usage: Optional[Dict[str, int]] = None
    success: bool = True
    error_msg: Optional[str] = None


class ASRService(ABC):
    """ASR服务抽象基类"""

    @abstractmethod
    async def recognize(
        self,
        audio_file: str,
        language: str = "zh-CN",
        sample_rate: int = 16000,
        format: str = "wav"
    ) -> ASRResult:
        """
        识别音频文件中的语音内容

        Args:
            audio_file: 音频文件路径
            language: 语言代码，默认zh-CN
            sample_rate: 采样率，默认16000
            format: 音频格式，默认wav

        Returns:
            ASR识别结果
        """
        pass


class TTSService(ABC):
    """TTS服务抽象基类"""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: str = "female",
        language: str = "zh-CN",
        speed: float = 1.0,
        format: str = "wav"
    ) -> TTSResult:
        """
        将文本合成为语音

        Args:
            text: 要合成的文本
            voice: 音色选择，默认female
            language: 语言代码，默认zh-CN
            speed: 语速，默认1.0
            format: 输出音频格式，默认wav

        Returns:
            TTS合成结果
        """
        pass


class LLMService(ABC):
    """大模型服务抽象基类"""

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> LLMResult:
        """
        聊天补全接口

        Args:
            messages: 消息列表
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            stream: 是否流式输出

        Returns:
            大模型返回结果
        """
        pass

    @abstractmethod
    async def intent_recognition(
        self,
        text: str,
        intents: List[str]
    ) -> Dict[str, Any]:
        """
        意图识别接口

        Args:
            text: 要识别的文本
            intents: 意图列表

        Returns:
            识别结果，包含最可能的意图和置信度
        """
        pass
