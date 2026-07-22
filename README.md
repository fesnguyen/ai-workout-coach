# AI Workout Coach

AI System for fitness knowledge retrieval and workout coaching

The project focuses on building an extensible AI backend capable of answering fitness questions, analyzing workout history, and safely interacting with users through Retrieval-Augmented Generation (RAG), configurable guardrails, and a tool-calling AI agent.

---

## Setup

### Prerequisites

- Docker
- Docker Compose

### Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Update `.env` with your OpenAI API key:

```text
OPENAI_API_KEY=your_api_key
```

### Run

Start the application:

```bash
docker compose up --build
```

The API will be available at:

```
http://localhost:8000
```

Swagger documentation:

```
http://localhost:8000/docs
```

---

## Tech Stack

- Python
- FastAPI
- OpenAI API
- ChromaDB
- Docker
- uv

---

# Architecture

## Application Container

The application uses a **singleton Application Container** to manage shared application context and dependencies.

It is responsible for:

- Initializing shared services during application startup.
- Managing singleton instances (LLM client, RAG service, agent, etc.).
- Providing dependency injection across the application.
- Ensuring expensive resources are created only once and reused throughout the application lifetime.

---

## AI Agent

The AI Agent orchestrates the application using a simple tool-calling loop.

```text
Build Messages
      │
      ▼
Invoke LLM
      │
      ▼
Tool Required?
      │
 ┌────┴─────┐
 │          │
Yes         No
 │          │
 ▼          ▼
Execute    Return Response
 Tool
 │
 ▼
Append Tool Result
 │
 ▼
Invoke LLM Again
```

The loop continues until the model determines that no additional tools are required.

The agent currently has access to two domain tools:

- **RAG Search Tool** — answer knowledge-based fitness questions.
- **Workout Analysis Tool** — analyze workout history and provide coaching feedback.

---

## System Prompt Strategy

Instead of maintaining a single large system prompt, the application composes multiple prompt blocks, each with a specific responsibility.

Current prompt blocks include:

- **Identity** — defines the assistant's role and behavior.
- **Developer Notes** — implementation-specific instructions.
- **Knowledge Rules** — how retrieved knowledge should be used.
- **Response Rules** — formatting and response requirements.
- **Safety Rules** — refusal and guardrail behavior.
- **Tool Rules** — when and how tools should be invoked.

This modular approach makes prompts easier to maintain, extend, and test independently.

---

## RAG Search Tool

**Endpoint**

```text
POST /rag/search
```

Purpose:

Answer user questions using the fitness knowledge base.

Workflow:

```text
Normalize Query
        │
        ▼
Query Expansion
        │
        ▼
LLM Guardrails
 • Intent Classification
 • Query Rewriting
        │
        ▼
──────── Decision ────────
│                        │
│ Out of Scope           │ Fitness Question
│                        │
▼                        ▼
Direct Response      Retrieve Chunks
                           │
                           ▼
                  Context Compression
                           │
                           ▼
                     Build Prompt
                           │
                           ▼
                     Generate Answer
```

---

## Workout Analysis Tool

**Endpoint**

```text
POST /workout/analyze
```

Purpose:

Analyze workout history and generate personalized coaching insights.

Workflow:

```text
Workout History
        │
        ▼
Extract Metrics
        │
        ▼
Compress Metrics
        │
        ▼
LLM Analysis
        │
        ▼
Workout Feedback
```

---

## Design Principles

The project is designed around several engineering principles:

- **Single Responsibility Principle** — each component has a single responsibility.
- **Extensible** — new tools, prompts, APIs, or workflows can be added with minimal changes.
- **Configurable** — prompts, models, retrieval, and behaviors are isolated from business logic.
- **Modular** — services are loosely coupled and independently maintainable.
- **Maintainable** — new features should require as little modification to existing code as possible.

---

## Project Structure

```text
app/
├── agent/                 # AI agent and tool execution
├── api/                   # FastAPI endpoints
├── configs/               # Application configuration
├── llm/                   # OpenAI integration
├── prompts/               # Modular system prompts
├── rag/                   # RAG pipeline
├── workout_analysis/      # Workout analysis
├── application_container.py
└── main.py

knowledge/                 # Fitness knowledge base
evaluation/                # Evaluation pipeline
docs/                      # Project documentation
```

---

## Evaluation

The project includes an evaluation pipeline to measure the quality of generated responses.

Evaluation categories include:

- RAG Search
- Workout Analysis
- Guardrails

The evaluation process is used to identify failure cases, perform root cause analysis, and iteratively improve prompts and system behavior.

---