import base64
import io
import json
import logging
import struct
import wave
from typing import Any, Literal

import httpx

from app.core.config import Settings
from app.schemas.tts import TTSRequest, VoiceDesignRequest

logger = logging.getLogger(__name__)


AuthType = Literal["api-key", "bearer"]


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

    def _build_headers(
        self,
        request_api_key: str | None = None,
        request_auth_type: AuthType | None = None,
        *,
        content_type: str | None = "application/json",
    ) -> dict[str, str]:
        effective_api_key = request_api_key or self.settings.MIMO_API_KEY
        effective_auth_type = request_auth_type or self.settings.MIMO_AUTH_TYPE

        if not effective_api_key:
            raise MiMoAPIError(
                message="请在网页里的 API Token 输入框填写 MiMo Token，或在后端 .env 中配置 MIMO_API_KEY。",
                status_code=400,
            )

        headers = {"Accept": "application/json, audio/mpeg, audio/wav, */*"}
        if content_type:
            headers["Content-Type"] = content_type

        if effective_auth_type == "bearer":
            headers["Authorization"] = f"Bearer {effective_api_key}"
        else:
            headers["api-key"] = effective_api_key

        return headers

    def _build_url(self, endpoint_path: str, base_url_override: str | None = None) -> str:
        if endpoint_path.startswith("http://") or endpoint_path.startswith("https://"):
            return endpoint_path
        base = base_url_override or self.settings.MIMO_BASE_URL
        return base.rstrip("/") + "/" + endpoint_path.lstrip("/")

    def _build_style_instruction(self, req: TTSRequest) -> str:
        parts = [
            "你是一个高质量语音合成引擎。",
            "请将后续文本合成为自然清晰的语音。",
            f"语速参考：{req.speed}x。",
            f"音量参考：{req.volume}/100。",
        ]

        if req.voice_audio_data_url:
            parts.append("当前使用音频样本复刻音色，请尽量保持目标说话人的音色特征。")

        if req.style_prompt:
            parts.append(f"风格要求：{req.style_prompt}。")

        if req.speed >= 1.35:
            parts.append("整体表达可以略快。")
        elif req.speed <= 0.75:
            parts.append("整体表达可以略慢。")

        return "\n".join(parts)

    def _build_voice_design_instruction(self, req: VoiceDesignRequest) -> str:
        """构建音色设计的 system prompt"""
        parts = [
            "你是一个高质量语音合成引擎。",
            "请根据以下音色描述，将后续文本合成为自然清晰的语音。",
            f"音色描述：{req.voice_description}",
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

    @staticmethod
    def _normalize_data_url(data_url: str) -> str:
        """规范 data URL 头，但不伪装真实音频格式。

        MiMo V2.5 VoiceClone 的样本只建议使用 mp3 / wav。
        这里仅把常见别名归一化：
        - audio/mp3  -> audio/mpeg
        - audio/x-wav -> audio/wav

        注意：不能把 WAV 的 MIME 头改成 audio/mpeg；那只是“换标签”，
        并不会把 WAV 真正转成 MP3，反而可能让上游接口解析失败。
        """
        if data_url.startswith("data:audio/mp3;base64,"):
            return "data:audio/mpeg;base64," + data_url[len("data:audio/mp3;base64,"):]
        if data_url.startswith("data:audio/x-wav;base64,"):
            return "data:audio/wav;base64," + data_url[len("data:audio/x-wav;base64,"):]
        return data_url

    @staticmethod
    def _compress_wav_data_url(data_url: str, max_chars: int = 500_000) -> str:
        """如果 WAV data URL 超过 max_chars，降低采样率压缩，仍保持 audio/wav。"""
        if len(data_url) <= max_chars:
            return data_url
        if not (
            data_url.startswith("data:audio/wav;base64,")
            or data_url.startswith("data:audio/x-wav;base64,")
        ):
            return data_url

        try:
            header_end = data_url.index(",") + 1
            b64_data = data_url[header_end:]
            raw_bytes = base64.b64decode(b64_data)

            buf = io.BytesIO(raw_bytes)
            with wave.open(buf, "rb") as wf:
                channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
                framerate = wf.getframerate()
                nframes = wf.getnframes()
                raw_pcm = wf.readframes(nframes)

            if sampwidth != 2:
                return data_url

            samples = struct.unpack(f"<{len(raw_pcm)//2}h", raw_pcm)
            if channels == 2:
                samples = [(samples[i] + samples[i+1]) // 2 for i in range(0, len(samples), 2)]

            # 激进降采样：降到 8kHz
            target_rate = 8000
            ratio = max(1, framerate // target_rate)
            downsampled = samples[::ratio]

            new_buf = io.BytesIO()
            with wave.open(new_buf, "wb") as out:
                out.setnchannels(1)
                out.setsampwidth(2)
                out.setframerate(target_rate)
                out.writeframes(struct.pack(f"<{len(downsampled)}h", *downsampled))
            new_bytes = new_buf.getvalue()
            new_b64 = base64.b64encode(new_bytes).decode("utf-8")
            result = f"data:audio/wav;base64,{new_b64}"
            logger.info("WAV 压缩: %d → %d chars (%d→%d Hz)", len(data_url), len(result), framerate, target_rate)
            return result
        except Exception as e:
            logger.warning("WAV 压缩失败: %s", e)
            return data_url

        return data_url

    def _build_payload(self, req: TTSRequest) -> dict[str, Any]:
        use_voice_clone = bool(req.voice_audio_data_url)
        model = self.settings.MIMO_VOICE_CLONE_MODEL if use_voice_clone else self.settings.MIMO_MODEL

        if use_voice_clone:
            voice_value = self._normalize_data_url(req.voice_audio_data_url)
            voice_value = self._compress_wav_data_url(voice_value)
            # 清理可能的换行符和空白
            voice_value = voice_value.replace("\n", "").replace("\r", "").replace(" ", "")
            # 检查 data URL 格式
            if not voice_value.startswith("data:audio/") or ";base64," not in voice_value:
                logger.error("INVALID data URL format! prefix=%s, len=%d", voice_value[:50], len(voice_value))
            else:
                prefix = voice_value[:voice_value.index(",") + 1]
                logger.warning("Data URL OK: prefix=%s, total_len=%d", prefix, len(voice_value))
        else:
            voice_value = req.voice

        audio_config: dict[str, Any] = {
            "format": req.response_format,
            "voice": voice_value,
        }

        if (not use_voice_clone) and self.settings.MIMO_SEND_EXTRA_AUDIO_PARAMS:
            audio_config["speed"] = req.speed
            audio_config["volume"] = req.volume / 100

        return {
            "model": model,
            "messages": [
                {"role": "user", "content": self._build_style_instruction(req)},
                {"role": "assistant", "content": req.text},
            ],
            "audio": audio_config,
        }

    def _build_voice_design_payload(self, req: VoiceDesignRequest) -> dict[str, Any]:
        """构建音色设计请求的 payload
        使用 mimo-v2.5-tts-voicedesign 模型，通过文本描述自动生成音色。
        音色描述放在 messages 内容中传递，audio 配置中不传 voice 字段。
        """
        audio_config: dict[str, Any] = {
            "format": req.response_format,
        }

        if self.settings.MIMO_SEND_EXTRA_AUDIO_PARAMS:
            audio_config["speed"] = req.speed
            audio_config["volume"] = req.volume / 100

        return {
            "model": self.settings.MIMO_VOICE_DESIGN_MODEL,
            "messages": [
                {"role": "user", "content": self._build_voice_design_instruction(req)},
                {"role": "assistant", "content": req.text},
            ],
            "audio": audio_config,
        }

    def _guess_media_type(self, response_format: str) -> str:
        if response_format == "wav":
            return "audio/wav"
        return "audio/mpeg"

    def _friendly_error(self, status_code: int, raw_text: str) -> str:
        if status_code == 400:
            return f"MiMo API 参数错误：{raw_text[:500]}"
        if status_code == 401:
            return "MiMo API 鉴权失败，请检查 API Token 或认证方式。"
        if status_code == 403:
            return "MiMo API 拒绝访问，请检查账户权限、模型权限、语音复刻权限或区域限制。"
        if status_code == 404:
            return "MiMo API 接口不存在，请检查 MIMO_BASE_URL、接口路径或模型名称。"
        if status_code == 413:
            return "上传音频太大，请换一段更短的音频。"
        if status_code == 429:
            return "请求过于频繁或额度不足，请稍后重试或检查 MiMo 控制台额度。"
        if 500 <= status_code < 600:
            return "MiMo 服务暂时异常，请稍后重试。"
        return f"MiMo API 请求失败：HTTP {status_code}，详情：{raw_text[:500]}"

    def _extract_audio_from_json(self, data: dict[str, Any], response_format: str) -> tuple[bytes, str]:
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
        url = self._build_url(self.settings.MIMO_ENDPOINT_PATH, req.base_url)
        payload = self._build_payload(req)
        headers = self._build_headers(req.api_key, req.auth_type)

        # 调试日志：只生成预览，不修改 payload。
        # 之前使用浅拷贝 debug_payload = {**payload} 后再截断 audio.voice，
        # 会把真实 payload 里的 base64 样本也截断，导致 VoiceClone 必然失败。
        voice_preview = payload.get("audio", {}).get("voice", "N/A")
        if isinstance(voice_preview, str) and len(voice_preview) > 100:
            voice_preview = voice_preview[:200] + f"...(total {len(voice_preview)} chars)"
        logger.warning("MiMo TTS request: model=%s, url=%s", payload.get("model"), url)
        logger.warning("Payload audio.voice preview: %s", voice_preview)

        async with httpx.AsyncClient(timeout=self.settings.HTTP_TIMEOUT_SECONDS) as client:
            try:
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                logger.warning("Request body bytes: %d", len(body))
                resp = await client.post(url, headers=headers, content=body)
            except httpx.TimeoutException as exc:
                raise MiMoAPIError(message="连接 MiMo API 超时，请稍后重试。", status_code=504) from exc
            except httpx.RequestError as exc:
                raise MiMoAPIError(message=f"无法连接 MiMo API：{str(exc)}", status_code=502) from exc

        if resp.status_code >= 400:
            raw_text = resp.text
            logger.warning("MiMo TTS error: status=%d, body=%s", resp.status_code, raw_text[:500])
            raise MiMoAPIError(
                message=self._friendly_error(resp.status_code, raw_text),
                status_code=502 if resp.status_code >= 500 else resp.status_code,
                upstream_status=resp.status_code,
                raw=raw_text,
            )

        content_type = resp.headers.get("content-type", "")
        if content_type.startswith("audio/"):
            return resp.content, content_type.split(";")[0]

        try:
            data = resp.json()
        except json.JSONDecodeError as exc:
            raise MiMoAPIError(
                message="MiMo 返回内容既不是音频，也不是合法 JSON。",
                status_code=502,
                raw=resp.text[:500],
            ) from exc

        return self._extract_audio_from_json(data, req.response_format)

    async def synthesize_voice_design(self, req: VoiceDesignRequest) -> tuple[bytes, str]:
        """通过文本描述自动生成音色并合成语音"""
        url = self._build_url(self.settings.MIMO_ENDPOINT_PATH, req.base_url)
        payload = self._build_voice_design_payload(req)
        headers = self._build_headers(req.api_key, req.auth_type)

        async with httpx.AsyncClient(timeout=self.settings.HTTP_TIMEOUT_SECONDS) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
            except httpx.TimeoutException as exc:
                raise MiMoAPIError(message="连接 MiMo API 超时，请稍后重试。", status_code=504) from exc
            except httpx.RequestError as exc:
                raise MiMoAPIError(message=f"无法连接 MiMo API：{str(exc)}", status_code=502) from exc

        if resp.status_code >= 400:
            raw_text = resp.text
            raise MiMoAPIError(
                message=self._friendly_error(resp.status_code, raw_text),
                status_code=502 if resp.status_code >= 500 else resp.status_code,
                upstream_status=resp.status_code,
                raw=raw_text,
            )

        content_type = resp.headers.get("content-type", "")
        if content_type.startswith("audio/"):
            return resp.content, content_type.split(";")[0]

        try:
            data = resp.json()
        except json.JSONDecodeError as exc:
            raise MiMoAPIError(
                message="MiMo 返回内容既不是音频，也不是合法 JSON。",
                status_code=502,
                raw=resp.text[:500],
            ) from exc

        return self._extract_audio_from_json(data, req.response_format)

    async def clone_voice(self, **kwargs) -> dict[str, Any]:
        # 保留旧方法，避免旧前端调用时报 404；但新版前端不会再调用它。
        raise MiMoAPIError(
            message="当前版本不再调用 /voices/add 创建音色。请刷新页面使用新版逻辑：上传/录音后保存为本地复刻样本，生成语音时直接使用 mimo-v2.5-tts-voiceclone。",
            status_code=400,
        )
