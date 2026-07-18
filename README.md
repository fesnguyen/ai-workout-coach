# AI Workout Coach

Production-ready AI backend for fitness knowledge retrieval and workout coaching.

## Prerequisites

- Docker
- Docker Compose

## Setup

```bash
cp .env.example .env
```

Update `.env` with your OpenAI API key:

```text
OPENAI_API_KEY=your_api_key
```

Start the development environment:

```bash
docker compose up --build
```

The API will be available at:

```
http://localhost:8000
```