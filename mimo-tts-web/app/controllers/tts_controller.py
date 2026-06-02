from io import BytesIO
from time import time

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.core.config import get_settings
from app.schemas.tts import TTSRequest
from app.services.mimo_service import MiMoAPIError, MiMoTTSService


async def synthesize_tts_controller(req: TTSRequest) -> StreamingResponse:
    service = MiMoTTSService(get_settings())

    try:
        audio_bytes, media_type = await service.synthesize(req)
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
    filename = f"mimo_tts_{int(time())}.{ext}"

    return StreamingResponse(
        BytesIO(audio_bytes),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )
