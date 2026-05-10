import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.db.models import ChatMessage, ChatSession
from app.db.session import get_db
from app.middleware.rate_limit import check_rate_limit

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


async def _sse_event(data: dict) -> str:
    """Format a dict as a Server-Sent Event string."""
    return f"data: {json.dumps(data)}\n\n"


async def _stream_agent(
    user_message: str,
    session_id: str,
    history: list,
) -> AsyncGenerator[str, None]:
    """Run the LangGraph agent and yield SSE events."""
    from app.agents.graph import build_graph

    # Build message list for the graph state
    lc_messages = []
    for msg in history:
        if msg.role == "user":
            lc_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            lc_messages.append(AIMessage(content=msg.content))
    lc_messages.append(HumanMessage(content=user_message))

    graph = build_graph()

    initial_state = {
        "messages": lc_messages,
        "session_id": session_id,
        "intent": "",
        "retrieved_docs": [],
        "tool_result": "",
        "final_response": "",
        "error": "",
    }

    try:
        # Stream intermediate steps as SSE events
        async for event in graph.astream_events(initial_state, version="v1"):
            kind = event.get("event")
            name = event.get("name", "")

            # Emit agent step labels so the UI can show "🔍 Searching docs…"
            if kind == "on_chain_start" and name in (
                "supervisor", "researcher", "action_agent", "chat_agent", "formatter"
            ):
                yield await _sse_event({"type": "step", "node": name})

            # Stream final token chunks from the LLM
            elif kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content") and chunk.content:
                    yield await _sse_event({"type": "token", "content": chunk.content})

        # After graph completes, grab full final_response from last state
        final_state = await graph.ainvoke(initial_state)
        final_text = final_state.get("final_response", "")
        yield await _sse_event({"type": "done", "full_response": final_text})

    except Exception as exc:
        yield await _sse_event({"type": "error", "content": str(exc)})


@router.post("/chat")
async def chat(
    body: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user["sub"]
    await check_rate_limit(user_id)

    # ── Resolve / create session ────────────────────────────────────────────
    session_id = body.session_id
    if session_id:
        res = await db.execute(
            select(ChatSession).where(ChatSession.id == uuid.UUID(session_id))
        )
        if not res.scalar_one_or_none():
            session_id = None

    if not session_id:
        session = ChatSession(user_id=uuid.UUID(user_id))
        db.add(session)
        await db.commit()
        await db.refresh(session)
        session_id = str(session.id)

    # ── Save user message ───────────────────────────────────────────────────
    user_msg = ChatMessage(
        session_id=uuid.UUID(session_id),
        role="user",
        content=body.message,
    )
    db.add(user_msg)
    await db.commit()

    # ── Load last 20 messages as history ───────────────────────────────────
    history_res = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == uuid.UUID(session_id))
        .order_by(ChatMessage.created_at)
        .limit(20)
    )
    history = history_res.scalars().all()

    # ── Stream response ─────────────────────────────────────────────────────
    async def event_generator() -> AsyncGenerator[str, None]:
        full_response = ""
        async for chunk in _stream_agent(body.message, session_id, history[:-1]):
            yield chunk
            # Capture the final response text to persist
            try:
                payload = json.loads(chunk.replace("data: ", "").strip())
                if payload.get("type") == "done":
                    full_response = payload.get("full_response", "")
            except Exception:
                pass

        # Persist assistant reply
        if full_response:
            async with db.begin():
                ai_msg = ChatMessage(
                    session_id=uuid.UUID(session_id),
                    role="assistant",
                    content=full_response,
                )
                db.add(ai_msg)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "X-Session-Id": session_id,
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == uuid.UUID(session_id))
        .order_by(ChatMessage.created_at)
    )
    messages = res.scalars().all()
    return [
        {"role": m.role, "content": m.content, "id": str(m.id)}
        for m in messages
    ]


@router.get("/sessions")
async def list_sessions(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == uuid.UUID(current_user["sub"]))
        .order_by(ChatSession.created_at.desc())
    )
    sessions = res.scalars().all()
    return [
        {"id": str(s.id), "title": s.title, "created_at": s.created_at.isoformat()}
        for s in sessions
    ]


@router.post("/sessions")
async def create_session(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = ChatSession(user_id=uuid.UUID(current_user["sub"]), title="New Chat")
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"id": str(session.id), "title": session.title}
