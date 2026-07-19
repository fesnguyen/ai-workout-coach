"""
Embedding provider factory.
"""

from __future__ import annotations

from app.rag.embedding.base_embedder import BaseEmbedder
from app.rag.embedding.openai_embedder import OpenAIEmbedder


class EmbedderFactory:
    """Factory for creating embedding providers."""

    @staticmethod
    def create(
        *,
        provider: str,
        api_key: str,
        model: str,
    ) -> BaseEmbedder:
        match provider.lower():
            case "openai":
                return OpenAIEmbedder(
                    api_key=api_key,
                    model=model,
                )

            case _:
                raise ValueError(
                    f"Unsupported embedding provider: {provider}"
                )