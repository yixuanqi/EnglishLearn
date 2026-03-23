"""STT client for speech-to-text services."""

from typing import Any, Optional

import httpx

from app.ai.base import BaseAIClient
from app.core.config import settings


class STTClient(BaseAIClient):
    """Client for Speech-to-Text service (Azure Speech)."""

    BASE_URL = "https://{region}.stt.speech.microsoft.com"

    def __init__(
        self,
        api_key: Optional[str] = None,
        region: str = "eastus",
        **kwargs: Any,
    ) -> None:
        super().__init__(api_key or settings.azure_speech_key, **kwargs)
        self.region = region or settings.azure_speech_region
        self.client: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> None:
        """Initialize HTTP client."""
        base_url = self.BASE_URL.format(region=self.region)
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
            },
            timeout=60.0,
        )

    async def close(self) -> None:
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "en-US",
    ) -> str:
        """Transcribe speech to text."""
        pass
