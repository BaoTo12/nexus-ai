from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama

from app.agents.graph import AgentState
from app.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """\
You are NexusAI, a helpful, knowledgeable, and friendly AI assistant.
Be concise and accurate. Use markdown formatting where it improves clarity.
You have access to tools (weather, database queries, email) and a document knowledge base.
If you don't know something, say so honestly."""


async def chat_agent_node(state: AgentState) -> dict:
    """General conversation node with full chat history context."""
    llm = ChatOllama(
        model=settings.CHAT_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = await llm.ainvoke(messages)

    return {"final_response": response.content}
