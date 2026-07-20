from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # Temporarily hard code using open ai
    llm_provider: str = "openai"
    openai_model: str = "gpt-5.4-nano"

    # From .env
    openai_api_key: str | None = None


llm_settings = LLMSettings()