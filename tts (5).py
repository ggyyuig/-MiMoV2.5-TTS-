from io import BytesIO
from time import time

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.core.config import get_settings
from app.schemas.tts import VoiceDesignRequest
from app.services.mimo_service import MiMoAPIError, MiMoTTSService


async def synthesize_voice_design_controller(req: VoiceDesignRequest) -> StreamingResponse:
    """通过文本描述自动生成音色并合成语音"""
    service = MiMoTTSService(get_settings())

    try:
        audio_bytes, media_type = await service.synthesize_voice_design(req)
    except MiMoAPIError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "message": exc.message,
                "upstream_status": exc.upstream_status,
                "raw": exc.raw,
            },
        ) from exc

    ext = "wav" if media_type == "audio/wav" else "mp3"
    filename = f"mimo_voice_design_{int(time())}.{ext}"

    return StreamingResponse(
        BytesIO(audio_bytes),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )
