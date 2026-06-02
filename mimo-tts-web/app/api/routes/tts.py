from typing import Literal

from fastapi import APIRouter, File, Form, UploadFile

from app.controllers.tts_controller import synthesize_tts_controller
from app.controllers.voice_controller import clone_voice_controller
from app.controllers.voice_design_controller import synthesize_voice_design_controller
from app.schemas.tts import TTSRequest, VoiceDesignRequest

router = APIRouter(tags=["TTS"])


@router.get("/health")
async def health_check():
    return {
        "ok": True,
        "service": "mimo-tts-web",
        "base_url": "https://api.xiaomimimo.com/v1",
        "features": ["tts", "voice_clone", "voice_design"],
    }


@router.get("/voices")
async def list_voices():
    """
    前端下拉菜单使用。
    这里使用 MiMo 接口报错信息中返回的可用音色原名，value 必须完全匹配。
    自定义复刻音色会由前端在创建成功后追加到下拉框。
    """
    return {
        "voices": [
            {"label": "冰糖 - 中文女声", "value": "冰糖"},
            {"label": "茉莉 - 中文女声", "value": "茉莉"},
            {"label": "苏打 - 中文男声", "value": "苏打"},
            {"label": "白桦 - 中文男声", "value": "白桦"},
            {"label": "Mia - English Female", "value": "Mia"},
            {"label": "Chloe - English Female", "value": "Chloe"},
            {"label": "Milo - English Male", "value": "Milo"},
            {"label": "Dean - English Male", "value": "Dean"},
        ]
    }


@router.post("/tts")
async def synthesize_tts(req: TTSRequest):
    return await synthesize_tts_controller(req)


@router.post("/voice-design")
async def synthesize_voice_design(req: VoiceDesignRequest):
    """通过文本描述自动生成音色并合成语音"""
    return await synthesize_voice_design_controller(req)


@router.post("/voices/clone")
async def clone_voice(
    api_key: str | None = Form(default=None),
    auth_type: Literal["bearer", "api-key"] | None = Form(default=None),
    name: str = Form(..., min_length=1, max_length=80),
    description: str | None = Form(default=None, max_length=300),
    consent_accepted: bool = Form(False),
    audio: UploadFile = File(...),
):
    return await clone_voice_controller(
        api_key=api_key,
        auth_type=auth_type,
        name=name,
        description=description,
        consent_accepted=consent_accepted,
        audio=audio,
    )
