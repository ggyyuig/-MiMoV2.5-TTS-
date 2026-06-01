from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 必填：MiMo MiMo API Key / Token
    MIMO_API_KEY: str = ""

    # 你提供的 MiMo API 请求地址，注意这里已经包含 /v1
    MIMO_BASE_URL: str = "https://api.xiaomimimo.com/v1"

    # 最终会拼成：https://api.xiaomimimo.com/v1/chat/completions
    MIMO_ENDPOINT_PATH: str = "/chat/completions"

    # MiMo V2.5 TTS 模型名
    MIMO_MODEL: str = "mimo-v2.5-tts"

    # 默认用 Bearer；如果你的文档要求 api-key，可在 .env 中改成 api-key
    MIMO_AUTH_TYPE: Literal["api-key", "bearer"] = "bearer"

    # 默认关闭，避免上游不支持 speed/volume 字段导致 400。
    # 前端的 speed/volume 会通过文本指令方式传给模型。
    MIMO_SEND_EXTRA_AUDIO_PARAMS: bool = False

    HTTP_TIMEOUT_SECONDS: float = 90.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
