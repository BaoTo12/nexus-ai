from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from app.agents.graph import AgentState
from app.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """\
You are a routing assistant. Classify the user's intent into exactly ONE of these categories:

- rag    → User asks about documents, files, uploaded PDFs, or the knowledge base
- action → User wants to DO something: check weather, query data, send an email
- chat   → General conversation, greetings, questions about yourself, anything else

Reply with ONLY one lowercase word: rag, action, or chat. No explanation."""


async def supervisor_node(state: AgentState) -> dict:
    llm = ChatOllama(
        model=settings.CHAT_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0,
    )

    user_text = state["messages"][-1].content

    try:
        resp = await llm.ainvoke(
            [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_text)]
        )
        intent = resp.content.strip().lower().split()[0]
        if intent not in ("rag", "action", "chat"):
            intent = "chat"
    except Exception:
        intent = "chat"

    return {"intent": intent}
