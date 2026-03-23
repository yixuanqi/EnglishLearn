"""Speech-to-Text service using Azure Cognitive Services."""

import json
from typing import Optional

import httpx

from app.ai.config import ai_settings
from app.ai.exceptions import STTServiceError
from app.ai.retry import CircuitBreaker, RetryConfig, retry_with_backoff
from app.ai.schemas import WordTimestamp


class STTRequest:
    """STT request parameters."""

    def __init__(
        self,
        audio_data: bytes,
        audio_format: str = "wav",
        language: str = "en-US",
        profanity_filter: bool = True,
        enable_word_timestamps: bool = False,
    ) -> None:
        self.audio_data = audio_data
        self.audio_format = audio_format
        self.language = language
        self.profanity_filter = profanity_filter
        self.enable_word_timestamps = enable_word_timestamps


class STTResponse:
    """STT response data."""

    def __init__(
        self,
        text: str,
        confidence: float,
        language_detected: str,
        duration_seconds: float,
        word_timestamps: Optional[list[WordTimestamp]] = None,
    ) -> None:
        self.text = text
        self.confidence = confidence
        self.language_detected = language_detected
        self.duration_seconds = duration_seconds
        self.word_timestamps = word_timestamps or []


class STTService:
    """Speech-to-Text service using Azure Cognitive Services."""

    def __init__(
        self,
        subscription_key: Optional[str] = None,
        region: Optional[str] = None,
    ) -> None:
        self.subscription_key = subscription_key or ai_settings.azure_speech_key
        self.region = region or ai_settings.azure_speech_region
        self.max_audio_size = ai_settings.stt_max_audio_size
        self.default_language = ai_settings.stt_default_language
        self.circuit_breaker = CircuitBreaker()

    async def transcribe(self, request: STTRequest) -> STTResponse:
        """Transcribe audio to text."""
        self._validate_audio(request.audio_data)

        return await self._transcribe_azure(request)

    async def _transcribe_azure(self, request: STTRequest) -> STTResponse:
        """Call Azure STT API."""
        endpoint = f"https://{self.region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"

        content_type = self._get_content_type(request.audio_format)

        params = {
            "language": request.language,
        }

        async def _request() -> STTResponse:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    endpoint,
                    headers={
                        "Ocp-Apim-Subscription-Key": self.subscription_key,
                        "Content-Type": content_type,
                        "Accept": "application/json",
                    },
                    params=params,
                    content=request.audio_data,
                )

                if response.status_code == 403:
                    raise STTServiceError(
                        "Azure STT authentication failed",
                        {"status": response.status_code},
                    )

                if response.status_code == 429:
                    raise STTServiceError(
                        "Azure STT rate limit exceeded",
                        {"status": response.status_code},
                    )

                if response.status_code != 200:
                    raise STTServiceError(
                        f"Azure STT error: {response.status_code}",
                        {"response": response.text[:500]},
                    )

                data = response.json()
                return self._parse_azure_response(data, request)

        return await self.circuit_breaker.call(
            retry_with_backoff,
            RetryConfig(max_attempts=3),
            _request,
        )

    def _parse_azure_response(
        self,
        data: dict,
        request: STTRequest,
    ) -> STTResponse:
        """Parse Azure STT response."""
        display_text = data.get("DisplayText", "")
        confidence = 0.0
        duration_seconds = 0.0
        word_timestamps: list[WordTimestamp] = []

        if "NBest" in data and len(data["NBest"]) > 0:
            best = data["NBest"][0]
            confidence = best.get("Confidence", 0.0)

            if "Words" in best and request.enable_word_timestamps:
                for word_data in best["Words"]:
                    word_timestamps.append(
                        WordTimestamp(
                            word=word_data.get("Word", ""),
                            start_time=word_data.get("Offset", 0) / 10000000,
                            end_time=(word_data.get("Offset", 0) + word_data.get("Duration", 0)) / 10000000,
                            confidence=word_data.get("PronunciationAssessment", {}).get("AccuracyScore", 0.0),
                        )
                    )

        return STTResponse(
            text=display_text,
            confidence=confidence,
            language_detected=request.language,
            duration_seconds=duration_seconds,
            word_timestamps=word_timestamps,
        )

    def _get_content_type(self, audio_format: str) -> str:
        """Get content type for audio format."""
        format_map = {
            "wav": "audio/wav; codecs=audio/pcm; samplerate=16000",
            "mp3": "audio/mp3",
            "ogg": "audio/ogg",
            "webm": "audio/webm",
        }
        return format_map.get(audio_format.lower(), "audio/wav")

    def _validate_audio(self, audio_data: bytes) -> None:
        """Validate audio data."""
        if not audio_data or len(audio_data) == 0:
            raise STTServiceError("Audio data is empty")

        if len(audio_data) > self.max_audio_size:
            raise STTServiceError(
                "Audio file too large",
                {
                    "max_size": self.max_audio_size,
                    "actual_size": len(audio_data),
                },
            )

    async def transcribe_with_duration(
        self,
        audio_data: bytes,
        audio_format: str = "wav",
        language: str = "en-US",
    ) -> tuple[str, float]:
        """Transcribe audio and return text with duration."""
        request = STTRequest(
            audio_data=audio_data,
            audio_format=audio_format,
            language=language,
        )

        response = await self.transcribe(request)
        return response.text, response.duration_seconds
