from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TTSRequest(BaseModel):
    # 可选：允许前端传入 Token。
    # 这样用户无需修改 .env；如果不传，则回退使用后端环境变量 MIMO_API_KEY。
    api_key: str | None = Field(default=None, max_length=4096)
    auth_type: Literal["bearer", "api-key"] | None = Field(default=None)

    # 可选：允许前端传入自定义 API 接口地址。
    # 如果不传，则使用后端 .env 中的 MIMO_BASE_URL。
    base_url: str | None = Field(default=None, max_length=2048)

    text: str = Field(..., min_length=1, max_length=4096)

    # 预置音色时使用 MiMo 官方音色名，例如：茉莉、冰糖、苏打等。
    # 音色复刻时，前端仍会传一个展示名，但真正的声音样本走 voice_audio_data_url。
    voice: str = Field(default="茉莉")

    # 音色复刻：官方示例不是先创建一个永久 voice_id，而是把音频样本转成
    # data:audio/...;base64,... 作为 audio.voice 直接传给 mimo-v2.5-tts-voiceclone。
    voice_audio_data_url: str | None = Field(default=None, max_length=14_000_000)

    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    volume: int = Field(default=80, ge=0, le=100)
    response_format: Literal["mp3", "wav"] = "wav"
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

    @field_validator("base_url")
    @classmethod
    def normalize_base_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip().rstrip("/")
        return value or None

    @field_validator("voice_audio_data_url")
    @classmethod
    def validate_voice_audio_data_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        if not value.startswith("data:audio/") or ";base64," not in value:
            raise ValueError("复刻音频必须是 data:audio/...;base64,... 格式")
        # 官方 skill 说明：音色样本 Base64 编码不超过 10 MB，仅支持 mp3 和 wav。
        if not (value.startswith("data:audio/mpeg;base64,") or value.startswith("data:audio/mp3;base64,") or value.startswith("data:audio/wav;base64,") or value.startswith("data:audio/x-wav;base64,")):
            raise ValueError("复刻音频仅建议使用 mp3 或 wav。")
        return value


class VoiceDesignRequest(BaseModel):
    """
    音色设计请求：通过文本描述自动生成音色。
    使用 mimo-v2.5-tts-voicedesign 模型，无需预置音色或上传音频样本。
    不支持唱歌模式、预置音色与音色复刻。
    """
    api_key: str | None = Field(default=None, max_length=4096)
    auth_type: Literal["bearer", "api-key"] | None = Field(default=None)

    # 可选：允许前端传入自定义 API 接口地址。
    # 如果不传，则使用后端 .env 中的 MIMO_BASE_URL。
    base_url: str | None = Field(default=None, max_length=2048)

    text: str = Field(..., min_length=1, max_length=4096, description="要合成的文本")

    voice_description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="用文字描述你想要的音色，例如：温柔甜美的年轻女声、低沉浑厚的中年男声、活泼可爱的童声",
    )

    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    volume: int = Field(default=80, ge=0, le=100)
    response_format: Literal["mp3", "wav"] = "wav"
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

    @field_validator("voice_description")
    @classmethod
    def normalize_voice_description(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("音色描述不能为空")
        return value

    @field_validator("api_key")
    @classmethod
    def normalize_api_key(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("base_url")
    @classmethod
    def normalize_base_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip().rstrip("/")
        return value or None
