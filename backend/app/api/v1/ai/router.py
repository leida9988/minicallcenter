from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from ....services.ai.factory import AIServiceFactory
from ....services.ai.base import LLMMessage
from ....core.dependencies import get_current_user
from ....models.user import User

router = APIRouter(prefix="/ai", tags=["AI服务"])


class TTSRequest(BaseModel):
    """TTS合成请求"""
    text: str
    voice: Optional[str] = "female"
    language: Optional[str] = "zh-CN"
    speed: Optional[float] = 1.0
    provider: Optional[str] = None


class LLMChatRequest(BaseModel):
    """大模型聊天请求"""
    messages: List[LLMMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000
    provider: Optional[str] = None


class IntentRecognitionRequest(BaseModel):
    """意图识别请求"""
    text: str
    intents: List[str]
    provider: Optional[str] = None


@router.post("/asr/recognize", summary="语音识别")
async def asr_recognize(
    audio: UploadFile = File(...),
    language: str = Form("zh-CN"),
    provider: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    上传音频文件进行语音识别

    - **audio**: 音频文件，支持wav、mp3等格式
    - **language**: 语言代码，默认zh-CN
    - **provider**: 服务提供商，默认使用系统配置
    """
    try:
        asr_service = AIServiceFactory.get_asr_service(provider)

        # 保存上传的文件到临时目录
        import tempfile
        import os
        suffix = os.path.splitext(audio.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            result = await asr_service.recognize(tmp_path, language=language)
            return result
        finally:
            # 删除临时文件
            os.unlink(tmp_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音识别失败: {str(e)}")


@router.post("/tts/synthesize", summary="语音合成")
async def tts_synthesize(
    request: TTSRequest,
    current_user: User = Depends(get_current_user)
):
    """
    将文本合成为语音

    - **text**: 要合成的文本内容
    - **voice**: 音色选择，默认female
    - **language**: 语言代码，默认zh-CN
    - **speed**: 语速，默认1.0
    - **provider**: 服务提供商，默认使用系统配置
    """
    try:
        tts_service = AIServiceFactory.get_tts_service(request.provider)
        result = await tts_service.synthesize(
            text=request.text,
            voice=request.voice,
            language=request.language,
            speed=request.speed
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")


@router.post("/llm/chat", summary="大模型聊天")
async def llm_chat(
    request: LLMChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    调用大模型进行对话

    - **messages**: 消息历史列表
    - **temperature**: 温度参数，控制随机性，默认0.7
    - **max_tokens**: 最大生成token数，默认2000
    - **provider**: 服务提供商，默认使用系统配置
    """
    try:
        llm_service = AIServiceFactory.get_llm_service(request.provider)
        result = await llm_service.chat_completion(
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"大模型调用失败: {str(e)}")


@router.post("/llm/intent-recognition", summary="意图识别")
async def intent_recognition(
    request: IntentRecognitionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    识别文本的意图

    - **text**: 要识别的文本内容
    - **intents**: 可选的意图列表
    - **provider**: 服务提供商，默认使用系统配置
    """
    try:
        llm_service = AIServiceFactory.get_llm_service(request.provider)
        result = await llm_service.intent_recognition(
            text=request.text,
            intents=request.intents
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"意图识别失败: {str(e)}")
