from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    llm_provider: str = "openai"

    openai_api_key: str

    # -------------------------------------------------------------------------
    # OpenAI Models
    #
    # Notes:
    # - GPT-4.1 models do NOT support the `reasoning` parameter.
    # - GPT-5 models support `reasoning={"effort": "minimal|low|medium|high"}`.
    # - GPT-5 reasoning parameters and its value set are varied based on model version.
    # -------------------------------------------------------------------------
    openai_model: str = "gpt-5.4-nano"


settings = LLMSettings()