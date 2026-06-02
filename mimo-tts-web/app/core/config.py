from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 可选：后端环境变量里的 MiMo API Key。前端传入 Token 时会优先使用前端 Token。
    MIMO_API_KEY: str = ""

    # MiMo API 请求地址，注意这里已经包含 /v1
    MIMO_BASE_URL: str = "https://api.xiaomimimo.com/v1"

    # 最终会拼成：https://api.xiaomimimo.com/v1/chat/completions
    MIMO_ENDPOINT_PATH: str = "/chat/completions"

    # MiMo V2.5 TTS 预置音色模型
    MIMO_MODEL: str = "mimo-v2.5-tts"

    # MiMo V2.5 TTS 音色设计模型：通过文本描述自动生成音色，无需预置或音频样本
    # 不支持唱歌模式、预置音色与音色复刻
    MIMO_VOICE_DESIGN_MODEL: str = "mimo-v2.5-tts-voicedesign"

    # 语音复刻不再走独立 /voices/add 接口。
    # 官方开源 skill 使用 chat/completions + model=mimo-v2.5-tts-voiceclone，
    # 并把音频样本 Data URL 放入 audio.voice。
    MIMO_VOICE_CLONE_MODEL: str = "mimo-v2.5-tts-voiceclone"

    # 默认用 Bearer；如果你的文档要求 api-key，可在前端或 .env 中改成 api-key
    MIMO_AUTH_TYPE: Literal["api-key", "bearer"] = "bearer"

    # 默认关闭，避免上游不支持 speed/volume 字段导致 400。
    # 前端的 speed/volume 会通过文本指令方式传给模型。
    MIMO_SEND_EXTRA_AUDIO_PARAMS: bool = False

    # 上传用于复刻的音频大小限制，单位 MB。官方 skill 建议 Base64 后不超过 10MB。
    MIMO_MAX_CLONE_AUDIO_MB: int = 8

    HTTP_TIMEOUT_SECONDS: float = 90.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
