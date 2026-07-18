# Design Decisions

## Deployment - Docker Compose

- Running locally with a single `docker compose up`.
- Lightweight and easy to set up.
- Avoids unnecessary orchestration complexity for a single application.

---

## Architecture - Layered Architecture

- Cleanly separates API, business logic, AI, and data access.
- Simpler to develop and deploy as a single application.
- Easy to extend without introducing distributed system complexity.

---

## Backend - FastAPI

- Excellent support for asynchronous APIs.
- Automatic OpenAPI documentation.
- Built-in request validation with Pydantic.

---

## Workflow - Simple Workflow Loop

- Archieve agent target with minimal complexity.
- Easy to understand and debug.
- Can be upgraded to a graph-based workflow if future requirements become more complex.

---

## Vector Database - ChromaDB

- Persistent local vector database with metadata support.
- Simple setup for a small knowledge base.
- No additional infrastructure required.

---

## LLM - OpenAI API

- Reliable structured outputs and function calling.
- Managed inference with automatic scalability.
- Allows the project to focus on application architecture instead of model hosting.
- Easily replaceable through an LLM abstraction layer.

## OpenAI conversation strategy - Item Centric:

- Item Centric (Provider-Managed) is newest and modern approach, it's popular for AI development. Older approach: Message Centric (Client-Managed)
- Saving effort for managing conversation flow, formating, prompt caching. Reduce development complexity.