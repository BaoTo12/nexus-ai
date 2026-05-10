# NexusAI — Multi-Agent Chatbot

A learn-and-demo multi-agent chatbot built with **LangGraph**, **FastAPI**, **Next.js 14**, and **PostgreSQL + pgvector**. Runs entirely locally with Ollama.

## Architecture

```
User → Next.js (SSE) → FastAPI → LangGraph
                                    ├── Supervisor   (classifies intent)
                                    ├── Researcher   (RAG via pgvector)
                                    ├── ActionAgent  (weather / db / email tools)
                                    ├── ChatAgent    (general conversation)
                                    └── Formatter    (graceful fallback)
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Node.js 20+](https://nodejs.org/) (for local frontend dev only)
- 4 GB+ RAM free (for Ollama models)

## Quick Start

### 1. Clone & configure

```bash
git clone <repo-url>
cd nexusai
cp .env.example .env
```

Edit `.env` and fill in:
- `SECRET_KEY` — any long random string
- `LANGCHAIN_API_KEY` — from [smith.langchain.com](https://smith.langchain.com) (free)

### 2. Start all services

```bash
docker-compose up -d
```

This starts: **postgres**, **redis**, **ollama**, **backend**, **frontend**.

### 3. Pull Ollama models (one-time, ~2.5 GB total)

```bash
# Wait for ollama service to start (~10 seconds), then:
docker exec nexusai_ollama ollama pull llama3.2:3b
docker exec nexusai_ollama ollama pull nomic-embed-text
```

> **Note:** `llama3.2:3b` requires ~2 GB RAM. For lower-spec machines, use `qwen2:1.5b` instead (change `CHAT_MODEL` in `.env`).

### 4. Open the app

| Service | URL |
|---|---|
| Frontend (ChatGPT UI) | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |
| LangSmith traces | https://smith.langchain.com |

## Features

| Feature | How to demo it |
|---|---|
| **General chat** | Ask anything — "Explain quantum computing" |
| **Weather tool** | "What's the weather in London?" |
| **DB query tool** | "Show me total revenue by product" |
| **Email tool** | "Send an email to bob@test.com about the meeting tomorrow" |
| **RAG** | Upload a PDF via the sidebar → ask questions about it |
| **Clarification loop** | "Send an email" (with no recipient) |
| **Rate limiting** | 10 messages/minute per user |
| **LangSmith tracing** | Each agent step is traced on smith.langchain.com |

## Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
# Update DATABASE_URL and REDIS_URL in .env to point to localhost
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
nexusai/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── app/
│   │   ├── agents/        ← LangGraph nodes
│   │   ├── api/           ← FastAPI routes
│   │   ├── auth/          ← JWT
│   │   ├── db/            ← SQLAlchemy + pgvector
│   │   ├── middleware/    ← Rate limiting
│   │   ├── tools/         ← weather, database, email
│   │   ├── config.py
│   │   └── main.py
│   └── requirements.txt
└── frontend/
    └── src/
        ├── app/           ← Next.js App Router pages
        ├── components/    ← Sidebar, ChatWindow, InputBar, etc.
        └── lib/           ← API client, utilities
```

## Switching Models

Edit `CHAT_MODEL` in `.env`:

| Model | RAM needed | Quality |
|---|---|---|
| `llama3.2:3b` (default) | ~2 GB | Good |
| `qwen2:1.5b` | ~1 GB | Basic |
| `mistral:7b` | ~4.5 GB | Better |
| `llama3.1:8b` | ~5 GB | Best local |
