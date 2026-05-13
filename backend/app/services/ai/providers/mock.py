import asyncio
import random
from typing import List, Dict, Any
from ..base import ASRService, TTSService, LLMService, ASRResult, TTSResult, LLMResult, LLMMessage
from ..factory import AIServiceFactory


class MockASRService(ASRService):
    """模拟ASR服务，用于开发测试"""

    def __init__(self, **kwargs):
        self.delay = kwargs.get('delay', 1.0)
        self.accuracy = kwargs.get('accuracy', 0.9)

    async def recognize(
        self,
        audio_file: str,
        language: str = "zh-CN",
        sample_rate: int = 16000,
        format: str = "wav"
    ) -> ASRResult:
        # 模拟处理延迟
        await asyncio.sleep(self.delay)

        # 模拟识别结果
        if random.random() < self.accuracy:
            return ASRResult(
                text="这是一个模拟的语音识别结果，内容可以根据需要自定义",
                confidence=random.uniform(0.8, 0.99),
                duration=random.uniform(1.0, 10.0)
            )
        else:
            return ASRResult(
                text="",
                confidence=0.0,
                success=False,
                error_msg="模拟识别失败"
            )


class MockTTSService(TTSService):
    """模拟TTS服务，用于开发测试"""

    def __init__(self, **kwargs):
        self.delay = kwargs.get('delay', 0.5)
        self.audio_url = kwargs.get('audio_url', '/static/mock_tts.wav')

    async def synthesize(
        self,
        text: str,
        voice: str = "female",
        language: str = "zh-CN",
        speed: float = 1.0,
        format: str = "wav"
    ) -> TTSResult:
        # 模拟处理延迟
        await asyncio.sleep(self.delay)

        # 模拟合成结果
        return TTSResult(
            audio_url=self.audio_url,
            duration=len(text) * 0.3  # 简单估算时长
        )


class MockLLMService(LLMService):
    """模拟大模型服务，用于开发测试"""

    def __init__(self, **kwargs):
        self.delay = kwargs.get('delay', 2.0)
        self.response_prefix = kwargs.get('response_prefix', '模拟回复：')

    async def chat_completion(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> LLMResult:
        # 模拟处理延迟
        await asyncio.sleep(self.delay)

        # 生成模拟回复
        last_message = messages[-1].content if messages else ""
        response = f"{self.response_prefix}我收到了你的消息：{last_message}。这是一个模拟的回复，实际使用时会替换为真实的大模型输出。"

        return LLMResult(
            content=response,
            usage={
                "prompt_tokens": len(last_message),
                "completion_tokens": len(response),
                "total_tokens": len(last_message) + len(response)
            }
        )

    async def intent_recognition(
        self,
        text: str,
        intents: List[str]
    ) -> Dict[str, Any]:
        # 模拟处理延迟
        await asyncio.sleep(0.5)

        # 随机选择一个意图作为识别结果
        if not intents:
            return {"intent": "unknown", "confidence": 0.0}

        selected_intent = random.choice(intents)
        return {
            "intent": selected_intent,
            "confidence": random.uniform(0.7, 0.99),
            "all_intents": [
                {"intent": intent, "confidence": random.uniform(0.0, 0.5) if intent != selected_intent else random.uniform(0.7, 0.99)}
                for intent in intents
            ]
        }


# 注册模拟服务提供商
AIServiceFactory.register_asr_provider('mock', MockASRService)
AIServiceFactory.register_tts_provider('mock', MockTTSService)
AIServiceFactory.register_llm_provider('mock', MockLLMService)
