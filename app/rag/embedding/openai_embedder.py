from __future__ import annotations

from openai import AsyncOpenAI

from app.rag.embedding.base_embedder import BaseEmbedder


class OpenAIEmbedder(BaseEmbedder):
    """
    Generate vector embeddings using OpenAI.

    Default model
    -------------

    text-embedding-3-small

    Advantages

    - High quality
    - Fast
    - Low cost
    - 1536-dimensional vectors
    """

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
    ) -> None:
        self._client = AsyncOpenAI(
            api_key=api_key,
        )
        self._model = model

    async def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        The OpenAI API supports batch embedding,
        which is significantly faster than embedding
        one document at a time.
        """

        if not texts:
            return []

        response = await self._client.embeddings.create(
            model=self._model,
            input=texts,
        )

        return [
            item.embedding
            for item in response.data
        ]

    async def embed_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Generate an embedding for a search query.
        """

        response = await self._client.embeddings.create(
            model=self._model,
            input=query,
        )

        return response.data[0].embedding