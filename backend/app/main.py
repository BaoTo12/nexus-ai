import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db.session import create_tables

settings = get_settings()

# Configure LangSmith tracing at startup
if settings.LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_TRACING_V2"] = str(settings.LANGCHAIN_TRACING_V2).lower()
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB tables
    await create_tables()
    yield
    # Shutdown: nothing to clean up


app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-agent chatbot with RAG, Function Calling, and LangGraph",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"},
    )


# ── Routers ───────────────────────────────────────────────────────────────────
from app.api import auth, chat, ingest  # noqa: E402

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(ingest.router, tags=["Ingest"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "chat_model": settings.CHAT_MODEL,
        "embed_model": settings.EMBED_MODEL,
        "langsmith": bool(settings.LANGCHAIN_API_KEY),
    }
