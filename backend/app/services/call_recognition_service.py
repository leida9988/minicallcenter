from typing import Optional
import os
from fastapi import HTTPException
from .ai.factory import AIServiceFactory
from .ai.base import LLMMessage
from ..models.call import CallRecord
from ..core.config import settings


class CallRecognitionService:
    """通话录音识别服务"""

    @classmethod
    async def recognize_call_audio(cls, call_record: CallRecord) -> str:
        """
        识别通话录音内容

        Args:
            call_record: 通话记录对象

        Returns:
            识别的文本内容
        """
        if not call_record.recording_url:
            raise HTTPException(status_code=400, detail="该通话没有录音文件")

        # 构建录音文件路径
        if settings.FS_RECORDING_PATH:
            audio_path = os.path.join(settings.FS_RECORDING_PATH, call_record.recording_url)
        else:
            audio_path = call_record.recording_url

        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="录音文件不存在")

        try:
            # 获取ASR服务实例
            asr_service = AIServiceFactory.get_asr_service()
            result = await asr_service.recognize(audio_path)
            if not result.success:
                raise HTTPException(status_code=500, detail=f"语音识别失败: {result.error_msg}")

            # 保存识别结果到数据库
            call_record.recognition_text = result.text
            await call_record.save()

            return result.text

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"通话识别失败: {str(e)}")

    @classmethod
    async def analyze_call_content(cls, call_record: CallRecord) -> dict:
        """
        分析通话内容，提取关键信息

        Args:
            call_record: 通话记录对象

        Returns:
            分析结果，包含意图、情绪、关键信息等
        """
        if not call_record.recognition_text:
            # 如果还没有识别结果，先进行识别
            await cls.recognize_call_audio(call_record)

        try:
            llm_service = AIServiceFactory.get_llm_service()

            # 构建提示词
            system_prompt = """
            你是一个专业的通话内容分析助手，请分析以下通话内容，提取关键信息：
            1. 客户意图：客户的主要需求是什么
            2. 情绪分析：客户的情绪是积极、中性还是消极
            3. 关键信息：提取通话中的重要信息，如产品需求、时间、地点、联系方式等
            4. 后续建议：针对这次通话，坐席后续应该做什么

            请以JSON格式返回结果，包含以下字段：
            {
                "intent": "客户意图",
                "sentiment": "positive/neutral/negative",
                "key_points": ["关键信息1", "关键信息2"],
                "suggestion": "后续建议"
            }
            """

            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=f"通话内容：{call_record.recognition_text}")
            ]

            result = await llm_service.chat_completion(messages, temperature=0.3)
            if not result.success:
                raise HTTPException(status_code=500, detail=f"内容分析失败: {result.error_msg}")

            # 解析返回的JSON
            import json
            try:
                analysis_result = json.loads(result.content)
                return analysis_result
            except json.JSONDecodeError:
                # 如果解析失败，返回原始内容
                return {"raw_result": result.content}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"通话内容分析失败: {str(e)}")
