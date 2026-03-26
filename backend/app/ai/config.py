"""AI service configuration - Supports MiniMax, Doubao, and Alibaba Cloud."""

from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    """AI service settings loaded from environment variables."""

    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_base_url: str = "https://api.openai.com/v1"

    minimax_api_key: str = ""
    minimax_model: str = "abab6.5s-chat"
    minimax_base_url: str = "https://api.minimax.chat/v1"

    deepseek_api_key: str = "xxx"
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"

    doubao_api_key: str = ""
    doubao_model: str = "doubao-pro"
    doubao_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"

    azure_speech_key: str = ""
    azure_speech_region: str = "cn-east-1"
    azure_speech_endpoint: str = ""

    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_deployment: str = "gpt-4"

    tts_default_voice: str = "en-US-JennyNeural"
    tts_cache_ttl: int = 604800

    stt_max_audio_size: int = 10485760
    stt_default_language: str = "en-US"

    llm_max_retries: int = 3
    llm_timeout: int = 60

    ai_provider: str = "deepseek"

    class Config:
        env_prefix = "AI_"
        env_file = ".env"
        extra = "ignore"


ai_settings = AISettings()
