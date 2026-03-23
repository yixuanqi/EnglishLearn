"""Text-to-Speech service using Azure Cognitive Services."""

import hashlib
import json
from typing import Optional

import httpx

from app.ai.config import ai_settings
from app.ai.exceptions import TTSServiceError
from app.ai.retry import CircuitBreaker, RetryConfig, retry_with_backoff


VOICE_MAPPING = {
    "business": "en-GB-SoniaNeural",
    "technical": "en-IN-NeerjaNeural",
    "exhibition": "en-US-JennyNeural",
    "daily_life": "en-US-GuyNeural",
}

AVAILABLE_VOICES = {
    "en-US-JennyNeural": {"gender": "female", "accent": "US", "language": "en-US"},
    "en-US-GuyNeural": {"gender": "male", "accent": "US", "language": "en-US"},
    "en-GB-SoniaNeural": {"gender": "female", "accent": "UK", "language": "en-GB"},
    "en-IN-NeerjaNeural": {"gender": "female", "accent": "Indian", "language": "en-IN"},
    "en-AU-NatashaNeural": {"gender": "female", "accent": "Australian", "language": "en-AU"},
}


class TTSRequest:
    """TTS request parameters."""

    def __init__(
        self,
        text: str,
        voice: str = "en-US-JennyNeural",
        rate: str = "0",
        pitch: str = "0",
        volume: str = "0",
    ) -> None:
        self.text = text
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.volume = volume


class TTSResponse:
    """TTS response data."""

    def __init__(
        self,
        audio_data: bytes,
        duration_seconds: float,
        format: str = "wav",
        sample_rate: int = 16000,
    ) -> None:
        self.audio_data = audio_data
        self.duration_seconds = duration_seconds
        self.format = format
        self.sample_rate = sample_rate

    @property
    def file_size_bytes(self) -> int:
        return len(self.audio_data)


class TTSService:
    """Text-to-Speech service using Azure Cognitive Services."""

    def __init__(
        self,
        subscription_key: Optional[str] = None,
        region: Optional[str] = None,
    ) -> None:
        self.subscription_key = subscription_key or ai_settings.azure_speech_key
        self.region = region or ai_settings.azure_speech_region
        self.cache_ttl = ai_settings.tts_cache_ttl
        self.circuit_breaker = CircuitBreaker()

    def select_voice(
        self,
        scenario_category: str,
        difficulty: Optional[str] = None,
        user_preference: Optional[str] = None,
    ) -> str:
        """Select appropriate voice based on scenario."""
        if user_preference and user_preference in AVAILABLE_VOICES:
            return user_preference

        return VOICE_MAPPING.get(scenario_category, ai_settings.tts_default_voice)

    async def synthesize(
        self,
        request: TTSRequest,
    ) -> TTSResponse:
        """Synthesize speech from text."""
        self._validate_text(request.text)

        return await self._synthesize_azure(request)

    async def synthesize_with_cache(
        self,
        request: TTSRequest,
        cache_client: Optional[any] = None,
    ) -> TTSResponse:
        """Synthesize speech with caching support."""
        if cache_client:
            cache_key = self._generate_cache_key(request)
            cached = await cache_client.get(cache_key)
            if cached:
                data = json.loads(cached)
                return TTSResponse(
                    audio_data=bytes.fromhex(data["audio_hex"]),
                    duration_seconds=data["duration_seconds"],
                    format=data.get("format", "wav"),
                    sample_rate=data.get("sample_rate", 16000),
                )

        response = await self.synthesize(request)

        if cache_client:
            cache_key = self._generate_cache_key(request)
            await cache_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps({
                    "audio_hex": response.audio_data.hex(),
                    "duration_seconds": response.duration_seconds,
                    "format": response.format,
                    "sample_rate": response.sample_rate,
                }),
            )

        return response

    async def _synthesize_azure(self, request: TTSRequest) -> TTSResponse:
        """Call Azure TTS API."""
        endpoint = f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1"

        ssml = self._build_ssml(request)

        async def _request() -> TTSResponse:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    endpoint,
                    headers={
                        "Ocp-Apim-Subscription-Key": self.subscription_key,
                        "Content-Type": "application/ssml+xml",
                        "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
                        "User-Agent": "EnglishTrainer",
                    },
                    content=ssml.encode("utf-8"),
                )

                if response.status_code == 403:
                    raise TTSServiceError(
                        "Azure TTS authentication failed",
                        {"status": response.status_code},
                    )

                if response.status_code == 429:
                    raise TTSServiceError(
                        "Azure TTS rate limit exceeded",
                        {"status": response.status_code},
                    )

                if response.status_code != 200:
                    raise TTSServiceError(
                        f"Azure TTS error: {response.status_code}",
                        {"response": response.text[:500]},
                    )

                audio_data = response.content
                duration = self._estimate_duration(request.text)

                return TTSResponse(
                    audio_data=audio_data,
                    duration_seconds=duration,
                    format="mp3",
                    sample_rate=16000,
                )

        return await self.circuit_breaker.call(
            retry_with_backoff,
            RetryConfig(max_attempts=3),
            _request,
        )

    def _build_ssml(self, request: TTSRequest) -> str:
        """Build SSML for Azure TTS."""
        escaped_text = self._escape_xml(request.text)

        return f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
            <voice name="{request.voice}">
                <prosody rate="{request.rate}%" pitch="{request.pitch}%" volume="{request.volume}">
                    {escaped_text}
                </prosody>
            </voice>
        </speak>"""

    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    def _validate_text(self, text: str) -> None:
        """Validate input text."""
        if not text or not text.strip():
            raise TTSServiceError("Text cannot be empty")

        if len(text) > 10000:
            raise TTSServiceError(
                "Text too long",
                {"max_length": 10000, "actual_length": len(text)},
            )

    def _estimate_duration(self, text: str) -> float:
        """Estimate audio duration based on text length."""
        word_count = len(text.split())
        words_per_minute = 150
        return (word_count / words_per_minute) * 60

    def _generate_cache_key(self, request: TTSRequest) -> str:
        """Generate cache key for TTS request."""
        text_hash = hashlib.md5(request.text.encode()).hexdigest()
        return f"tts:{request.voice}:{request.rate}:{request.pitch}:{text_hash}"

    def get_available_voices(self) -> dict[str, dict[str, str]]:
        """Get list of available voices."""
        return AVAILABLE_VOICES.copy()
