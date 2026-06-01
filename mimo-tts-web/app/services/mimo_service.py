import base64
import json
from typing import Any

import httpx

from app.core.config import Settings
from app.schemas.tts import TTSRequest


class MiMoAPIError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        upstream_status: int | None = None,
        raw: Any | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.upstream_status = upstream_status
        self.raw = raw
        super().__init__(message)


class MiMoTTSService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _build_headers(self, request_api_key: str | None = None) -> dict[str, str]:
        # 优先使用前端传来的 Token；如果没传，再回退到 .env 中的 MIMO_API_KEY。
        effective_api_key = request_api_key or self.settings.MIMO_API_KEY

        if not effective_api_key:
            raise MiMoAPIError(
                message="请在网页里的 API Token 输入框填写 MiMo Token，或在后端 .env 中配置 MIMO_API_KEY。",
                status_code=400,
            )

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, audio/mpeg, audio/wav, */*",
        }

        if self.settings.MIMO_AUTH_TYPE == "bearer":
            headers["Authorization"] = f"Bearer {effective_api_key}"
        else:
            headers["api-key"] = effective_api_key

        return headers

    def _build_style_instruction(self, req: TTSRequest) -> str:
        parts = [
            "你是一个高质量语音合成引擎。",
            "请将后续文本合成为自然清晰的语音。",
            f"语速参考：{req.speed}x。",
            f"音量参考：{req.volume}/100。",
        ]

        if req.style_prompt:
            parts.append(f"风格要求：{req.style_prompt}。")

        if req.speed >= 1.35:
            parts.append("整体表达可以略快。")
        elif req.speed <= 0.75:
            parts.append("整体表达可以略慢。")

        return "\n".join(parts)

    def _build_payload(self, req: TTSRequest) -> dict[str, Any]:
        audio_config: dict[str, Any] = {
            "format": req.response_format,
            "voice": req.voice,
        }

        # 有些接口版本可能不接受 speed / volume 作为 audio 字段。
        # 默认关闭，避免上游 400；如你的官方文档明确支持，可在 .env 开启。
        if self.settings.MIMO_SEND_EXTRA_AUDIO_PARAMS:
            audio_config["speed"] = req.speed
            audio_config["volume"] = req.volume / 100

        return {
            "model": self.settings.MIMO_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": self._build_style_instruction(req),
                },
                {
                    "role": "assistant",
                    "content": req.text,
                },
            ],
            "audio": audio_config,
        }

    def _guess_media_type(self, response_format: str) -> str:
        if response_format == "wav":
            return "audio/wav"
        return "audio/mpeg"

    def _friendly_error(self, status_code: int, raw_text: str) -> str:
        if status_code == 401:
            return "MiMo API 鉴权失败，请检查 MIMO_API_KEY 或认证方式 MIMO_AUTH_TYPE。"
        if status_code == 403:
            return "MiMo API 拒绝访问，请检查账户权限、模型权限或区域限制。"
        if status_code == 404:
            return "MiMo API 接口不存在，请检查 MIMO_BASE_URL、MIMO_ENDPOINT_PATH 或模型名称。"
        if status_code == 429:
            return "请求过于频繁或额度不足，请稍后重试或检查 MiMo 控制台额度。"
        if 500 <= status_code < 600:
            return "MiMo 服务暂时异常，请稍后重试。"
        return f"MiMo API 请求失败：HTTP {status_code}，详情：{raw_text[:300]}"

    def _extract_audio_from_json(
        self,
        data: dict[str, Any],
        response_format: str,
    ) -> tuple[bytes, str]:
        """
        兼容常见返回结构：
        {
          "choices": [
            {
              "message": {
                "audio": {
                  "data": "base64..."
                }
              }
            }
          ]
        }
        """
        try:
            audio_obj = data["choices"][0]["message"]["audio"]
            audio_b64 = audio_obj["data"]
        except Exception as exc:
            raise MiMoAPIError(
                message="MiMo 返回成功，但没有找到音频字段 choices[0].message.audio.data。",
                status_code=502,
                raw=data,
            ) from exc

        try:
            audio_bytes = base64.b64decode(audio_b64)
        except Exception as exc:
            raise MiMoAPIError(
                message="MiMo 返回的音频 base64 解码失败。",
                status_code=502,
                raw=data,
            ) from exc

        media_type = self._guess_media_type(response_format)
        return audio_bytes, media_type

    async def synthesize(self, req: TTSRequest) -> tuple[bytes, str]:
        url = self.settings.MIMO_BASE_URL.rstrip("/") + self.settings.MIMO_ENDPOINT_PATH

        payload = self._build_payload(req)
        headers = self._build_headers(req.api_key)

        async with httpx.AsyncClient(timeout=self.settings.HTTP_TIMEOUT_SECONDS) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
            except httpx.TimeoutException as exc:
                raise MiMoAPIError(
                    message="连接 MiMo API 超时，请稍后重试。",
                    status_code=504,
                ) from exc
            except httpx.RequestError as exc:
                raise MiMoAPIError(
                    message=f"无法连接 MiMo API：{str(exc)}",
                    status_code=502,
                ) from exc

        if resp.status_code >= 400:
            raw_text = resp.text
            raise MiMoAPIError(
                message=self._friendly_error(resp.status_code, raw_text),
                status_code=502 if resp.status_code >= 500 else resp.status_code,
                upstream_status=resp.status_code,
                raw=raw_text,
            )

        content_type = resp.headers.get("content-type", "")

        # 如果上游直接返回音频二进制，就直接透传
        if content_type.startswith("audio/"):
            return resp.content, content_type.split(";")[0]

        # 否则按 JSON + base64 音频解析
        try:
            data = resp.json()
        except json.JSONDecodeError as exc:
            raise MiMoAPIError(
                message="MiMo 返回内容既不是音频，也不是合法 JSON。",
                status_code=502,
                raw=resp.text[:500],
            ) from exc

        return self._extract_audio_from_json(data, req.response_format)
