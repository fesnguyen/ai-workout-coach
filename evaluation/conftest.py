from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio

from app.application_container import ApplicationContainer
from app.llm.base_generator import BaseGenerator
from app.rag.rag_service import RAGService


@pytest_asyncio.fixture(scope="session")
async def container() -> AsyncGenerator[ApplicationContainer, None]:
    """
    Initialize the application once for the entire test session.
    """
    container = ApplicationContainer()

    await container.initialize()

    yield container

    await container.shutdown()


@pytest.fixture(scope="session")
def rag(
    container: ApplicationContainer,
) -> RAGService:
    """
    Shared RAG service.
    """
    return container.rag_service


@pytest.fixture(scope="session")
def generator(
    container: ApplicationContainer,
) -> BaseGenerator:
    """
    Shared LLM generator.
    """
    return container.generator