from typing import Literal

from fastapi import File, Form, HTTPException, UploadFile

from app.core.config import get_settings
from app.services.mimo_service import MiMoAPIError, MiMoTTSService


async def clone_voice_controller(
    api_key: str | None = Form(default=None),
    auth_type: Literal["bearer", "api-key"] | None = Form(default=None),
    name: str = Form(..., min_length=1, max_length=80),
    description: str | None = Form(default=None, max_length=300),
    consent_accepted: bool = Form(False),
    audio: UploadFile = File(...),
):
    if not consent_accepted:
        raise HTTPException(
            status_code=400,
            detail={"message": "请先确认：你拥有该声音的使用授权。"},
        )

    settings = get_settings()
    max_bytes = settings.MIMO_MAX_CLONE_AUDIO_MB * 1024 * 1024

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=400,
            detail={"message": "请上传或录制一段音频。"},
        )

    if len(audio_bytes) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail={
                "message": f"音频文件过大，当前限制为 {settings.MIMO_MAX_CLONE_AUDIO_MB}MB。请换一段更短的音频。"
            },
        )

    safe_name = name.strip()
    if not safe_name:
        raise HTTPException(
            status_code=400,
            detail={"message": "音色名称不能为空。"},
        )

    service = MiMoTTSService(settings)

    try:
        return await service.clone_voice(
            api_key=api_key.strip() if api_key else None,
            auth_type=auth_type,
            name=safe_name,
            description=description.strip() if description else None,
            audio_bytes=audio_bytes,
            filename=audio.filename or "voice-sample.webm",
            content_type=audio.content_type,
        )
    except MiMoAPIError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "message": exc.message,
                "upstream_status": exc.upstream_status,
                "raw": exc.raw,
            },
        ) from exc
