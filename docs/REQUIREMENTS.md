# Requirements Analysis

## Objective

Build an AI Workout Coach capable of:

1. Answering fitness questions using RAG
2. Analyzing workout history
3. Running an AI agent that chooses tools
4. Evaluating the quality of the system

---

# Functional Requirements

## Feature 1 — Fitness Knowledge RAG

Required

- ingest markdown documents
- chunk documents
- embed chunks
- store embeddings
- retrieve relevant chunks
- answer grounded questions
- return citations
- reject out-of-domain questions

Guardrails, refuse or redict question that could constitute medical advice

- diagnosis
- rehabilitation
- eating disorder advice

Do not reject

- normal fitness guidance
- workout programming
- exercise explanations

---

## Feature 2 — Workout Analysis

Input

- workout history
- natural language question

Output

- preprocess history
- compute statistics
- detect trends
- detect missing data
- isolate user data

Important Note

- don't dump raw JSON into prompts

---

## Feature 3 — Agent

At least 2 tools

- rag_search()
- analyze_history()

Required

- choose tools dynamically
- handle tool failures
- merge outputs

---

## Feature 4 — Evaluation

Required:

- at least 15 test cases
- LLM judge
- rule metrics
- failure analysis

---

# Non-functional Requirements

- local execution
- Docker
- FastAPI preferred
- environment variables
- extensible architecture
- production-ready