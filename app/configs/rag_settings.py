from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class RAGSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    embedding_provider: str = "openai"

    # Temporary
    openai_api_key: str | None = None

    model: str = "text-embedding-3-small"

    rag_knowledge_path: Path = Path("knowledge")
    rag_database_path: Path = Path("data/chroma")


rag_settings = RAGSettings()