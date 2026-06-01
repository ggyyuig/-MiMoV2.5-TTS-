from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TTSRequest(BaseModel):
    # 可选：允许前端传入 Token。
    # 这样用户无需修改 .env；如果不传，则回退使用后端环境变量 MIMO_API_KEY。
    api_key: str | None = Field(default=None, max_length=4096)

    text: str = Field(..., min_length=1, max_length=4096)
    voice: str = Field(default="茉莉")
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    volume: int = Field(default=80, ge=0, le=100)
    response_format: Literal["mp3", "wav"] = "mp3"
    style_prompt: str | None = Field(
        default=None,
        max_length=300,
        description="可选风格提示，比如：温柔、开心、新闻播报感、慢一点等",
    )

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("文本不能为空")
        return value

    @field_validator("api_key")
    @classmethod
    def normalize_api_key(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None
