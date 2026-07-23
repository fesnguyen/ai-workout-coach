# Project Decisions

This project is built around a few simple choices that keep the system easy to ship, easy to read, and easy to evolve.

## Deployment and project setup

- **We chose Docker Compose over Kubernetes** so the app can be deployed almost anywhere without making the setup heavier than it needs to be.
- **We use `uv`** to manage the Python project, versioning, and dependencies in one place. It keeps the workflow modern and reduces scattered tooling.
- **FastAPI** is the backend framework, and that is not negotiable. It gives us a clean async API surface and fits the rest of the architecture well.

## Agent and conversation flow

- **Agent workflow as a loop** is intentional, it's simple, readable and sufficient in the goal of this project.
- **Item-centric / `previous_response_id`** strategy to handle conversation state which let the provider manage conversation flow on their side. That reduces the amount of conversation management we need to own ourselves, even if it gives up some flexibility.

## Prompt and context design

- **System prompting** is structured as a context prompt made of blocks like developer notes, knowledge rules, safety rules, tool rules, and response rules.
- **Reusable prompt builders** are used for the agent, RAG, and workout analysis flows so each path can share the same policy language without duplicating it everywhere.
- The code is organized around base **interfaces and factories** for generators, embedders, and tools so the implementation stays swappable without turning the core flow into a tangle.

## RAG decisions

- **Chroma is the RAG store and search layer** because it keeps setup simple and fits the project size well.
- **The RAG pipeline** is split into ingestion, retrieval, query normalization, preprocessing, analysis, and compression so each stage has one job.
- **We do a query guardrail step before retrieval** so non-fitness questions can be redirected or refused early. Again the safety rules are applied once more time in the final response to ensure no leaked cases.

## Workout analysis decisions

- **Workout history** is stored in JSON files for now because it is simple and fast to iterate on.
- This is a **temporary choice**, and it should move to a database once the project is production-ready.
- **Workout analysis is built from metric-based components** plus compression strategies so the analysis stays structured even as the input grows.

## Evaluation decisions

- Evaluation is run with **unit-test-style** checks and judge outputs instead of relying on LangSmith, tracing, or MLflow.
- **Faithfulness** is the main signal for judging early-stage outputs because it is a cheap and practical way to verify that the model response stays grounded in the expected analysis.
- **This does not cover every edge case**, especially cases where tool calls or multi-step behavior matter, but it is a good tradeoff for early development.

## Other architecture decisions

- The app is initialized through **a shared application container** so long-lived services are created once and reused across the process.
- **FastAPI lifespan** hooks are used for startup and shutdown, which keeps resource setup in one place.
- **Pydantic schemas are used throughout the API** and internal workflow so inputs and outputs stay explicit and validated.
- **The codebase stays modular on purpose**: agent, RAG, workout analysis, LLM, prompts, and evaluation are separated so changes in one area do not spill everywhere else.

## Summary

The overall direction is simple on purpose: keep the stack small, keep the workflow readable, and make it easy to ship now while leaving room to replace pieces later when the project grows.