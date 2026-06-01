from fastapi import APIRouter

from app.controllers.tts_controller import synthesize_tts_controller
from app.schemas.tts import TTSRequest

router = APIRouter(tags=["TTS"])


@router.get("/health")
async def health_check():
    return {
        "ok": True,
        "service": "mimo-tts-web",
        "base_url": "https://api.xiaomimimo.com/v1",
    }


@router.get("/voices")
async def list_voices():
    """
    前端下拉菜单使用。
    这里使用 MiMo 接口报错信息中返回的可用音色原名，value 必须完全匹配。
    """
    return {
        "voices": [
            {"label": "MiMo 默认音色", "value": "mimo_default"},
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
