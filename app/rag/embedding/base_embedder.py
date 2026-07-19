from __future__ import annotations

from abc import ABC, abstractmethod


class BaseEmbedder(ABC):
    """
    Base interface for embedding providers.

    Concrete implementations:
    - OpenAIEmbedder
    - OllamaEmbedder
    - VoyageAIEmbedder
    - SentenceTransformerEmbedder
    """

    @abstractmethod
    async def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple documents.

        Parameters
        ----------
        texts
            Documents or chunks to embed.

        Returns
        -------
        list[list[float]]
            Embeddings in the same order as the input.
        """
        raise NotImplementedError

    @abstractmethod
    async def embed_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Generate an embedding for a search query.
        """
        raise NotImplementedError