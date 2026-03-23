"""LLM client for OpenAI, MiniMax, Doubao (Volcengine), and Alibaba Cloud."""

import json
from typing import Any, Optional

import httpx

from app.ai.config import ai_settings
from app.ai.exceptions import LLMServiceError, RateLimitError, ServiceUnavailableError
from app.ai.retry import CircuitBreaker, RetryConfig, retry_with_backoff


class LLMClient:
    """Client for LLM API calls with multi-provider support."""

    PROVIDERS = {
        "openai": {
            "api_key": "openai_api_key",
            "model": "openai_model",
            "base_url": "openai_base_url",
        },
        "minimax": {
            "api_key": "minimax_api_key",
            "model": "minimax_model",
            "base_url": "minimax_base_url",
        },
        "deepseek": {
            "api_key": "deepseek_api_key",
            "model": "deepseek_model",
            "base_url": "deepseek_base_url",
        },
        "doubao": {
            "api_key": "doubao_api_key",
            "model": "doubao_model",
            "base_url": "doubao_base_url",
        },
        "azure": {
            "api_key": "azure_openai_api_key",
            "model": "azure_openai_deployment",
            "base_url": "azure_openai_endpoint",
        },
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> None:
        self.provider = provider or ai_settings.ai_provider
        provider_config = self.PROVIDERS.get(self.provider, self.PROVIDERS["openai"])

        self.api_key = api_key or getattr(ai_settings, provider_config["api_key"])
        self.model = model or getattr(ai_settings, provider_config["model"])
        self.base_url = base_url or getattr(ai_settings, provider_config["base_url"])
        self.timeout = ai_settings.llm_timeout
        self.circuit_breaker = CircuitBreaker()

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[dict[str, str]] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate text using the configured LLM provider."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        if self.provider == "minimax":
            return await self._call_minimax(messages, temperature, max_tokens)
        elif self.provider == "deepseek":
            return await self._call_deepseek(messages, temperature, max_tokens)
        elif self.provider == "doubao":
            return await self._call_doubao(messages, temperature, max_tokens)
        elif self.provider == "azure":
            return await self._call_azure(messages, temperature, max_tokens)
        else:
            return await self._call_openai(messages, temperature, max_tokens, response_format)

    async def generate_json(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        """Generate JSON response using the configured LLM provider."""
        response = await self.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise LLMServiceError(
                "Failed to parse JSON response",
                {"response": response, "error": str(e)},
            )

    async def _call_openai(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[dict[str, str]] = None,
    ) -> str:
        """Call OpenAI API."""
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            payload["response_format"] = response_format

        async def _request() -> str:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

                if response.status_code == 429:
                    retry_after = response.headers.get("retry-after")
                    raise RateLimitError(
                        service="OpenAI",
                        retry_after=int(retry_after) if retry_after else None,
                    )

                if response.status_code >= 500:
                    raise ServiceUnavailableError(
                        service="OpenAI",
                        details=response.text,
                    )

                if response.status_code != 200:
                    raise LLMServiceError(
                        f"OpenAI API error: {response.status_code}",
                        response.text,
                    )

                data = response.json()
                return data["choices"][0]["message"]["content"]

        return await self.circuit_breaker.call(
            retry_with_backoff,
            RetryConfig(max_attempts=ai_settings.llm_max_retries),
            _request,
        )

    async def _call_minimax(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call MiniMax API."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async def _request() -> str:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/text/chatcompletion_v2",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

                if response.status_code == 429:
                    raise RateLimitError(service="MiniMax", retry_after=60)

                if response.status_code >= 500:
                    raise ServiceUnavailableError(
                        service="MiniMax",
                        details=response.text,
                    )

                if response.status_code != 200:
                    raise LLMServiceError(
                        f"MiniMax API error: {response.status_code}",
                        response.text,
                    )

                data = response.json()
                return data["choices"][0]["message"]["content"]

        return await self.circuit_breaker.call(
            retry_with_backoff,
            RetryConfig(max_attempts=ai_settings.llm_max_retries),
            _request,
        )

    async def _call_deepseek(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call DeepSeek API."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async def _request() -> str:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

                if response.status_code == 429:
                    raise RateLimitError(service="DeepSeek", retry_after=60)

                if response.status_code >= 500:
                    raise ServiceUnavailableError(
                        service="DeepSeek",
                        details=response.text,
                    )

                if response.status_code != 200:
                    raise LLMServiceError(
                        f"DeepSeek API error: {response.status_code}",
                        response.text,
                    )

                data = response.json()
                return data["choices"][0]["message"]["content"]

        return await self.circuit_breaker.call(
            retry_with_backoff,
            RetryConfig(max_attempts=ai_settings.llm_max_retries),
            _request,
        )

    async def _call_doubao(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call Doubao (Volcengine) API."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async def _request() -> str:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

                if response.status_code == 429:
                    raise RateLimitError(service="Doubao", retry_after=60)

                if response.status_code >= 500:
                    raise ServiceUnavailableError(
                        service="Doubao",
                        details=response.text,
                    )

                if response.status_code != 200:
                    raise LLMServiceError(
                        f"Doubao API error: {response.status_code}",
                        response.text,
                    )

                data = response.json()
                return data["choices"][0]["message"]["content"]

        return await self.circuit_breaker.call(
            retry_with_backoff,
            RetryConfig(max_attempts=ai_settings.llm_max_retries),
            _request,
        )

    async def _call_azure(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call Azure OpenAI API."""
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async def _request() -> str:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/openai/deployments/{self.model}/chat/completions?api-version=2024-02-15-preview"
                response = await client.post(
                    url,
                    headers={
                        "api-key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

                if response.status_code == 429:
                    raise RateLimitError(service="AzureOpenAI", retry_after=60)

                if response.status_code >= 500:
                    raise ServiceUnavailableError(
                        service="AzureOpenAI",
                        details=response.text,
                    )

                if response.status_code != 200:
                    raise LLMServiceError(
                        f"Azure OpenAI API error: {response.status_code}",
                        response.text,
                    )

                data = response.json()
                return data["choices"][0]["message"]["content"]

        return await self.circuit_breaker.call(
            retry_with_backoff,
            RetryConfig(max_attempts=ai_settings.llm_max_retries),
            _request,
        )


class AzureOpenAIClient:
    """Client for Azure OpenAI API (legacy compatibility)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or ai_settings.azure_openai_api_key
        self.endpoint = endpoint or ai_settings.azure_openai_endpoint
        self.deployment = deployment or ai_settings.azure_openai_deployment
        self.timeout = ai_settings.llm_timeout
        self.circuit_breaker = CircuitBreaker()

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate text using Azure OpenAI API."""
        messages = [{"role": "user", "content": prompt}]
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async def _request() -> str:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version=2024-02-15-preview"
                response = await client.post(
                    url,
                    headers={
                        "api-key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

                if response.status_code == 429:
                    raise RateLimitError(service="AzureOpenAI", retry_after=60)

                if response.status_code >= 500:
                    raise ServiceUnavailableError(
                        service="AzureOpenAI",
                        details=response.text,
                    )

                if response.status_code != 200:
                    raise LLMServiceError(
                        f"Azure OpenAI API error: {response.status_code}",
                        response.text,
                    )

                data = response.json()
                return data["choices"][0]["message"]["content"]

        return await self.circuit_breaker.call(
            retry_with_backoff,
            RetryConfig(max_attempts=ai_settings.llm_max_retries),
            _request,
        )
