import operator
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph


# ── Shared state schema ──────────────────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    session_id: str
    intent: str              # "rag" | "action" | "chat"
    retrieved_docs: list[str]
    tool_result: str
    final_response: str
    error: str


# ── Routing logic ─────────────────────────────────────────────────────────────

def _route(state: AgentState) -> str:
    intent = state.get("intent", "chat")
    if intent not in ("rag", "action", "chat"):
        return "chat"
    return intent


# ── Graph builder ─────────────────────────────────────────────────────────────

def build_graph():
    from app.agents.supervisor import supervisor_node
    from app.agents.researcher import researcher_node
    from app.agents.action_agent import action_agent_node
    from app.agents.chat_agent import chat_agent_node
    from app.agents.formatter import formatter_node

    wf = StateGraph(AgentState)

    wf.add_node("supervisor", supervisor_node)
    wf.add_node("researcher", researcher_node)
    wf.add_node("action_agent", action_agent_node)
    wf.add_node("chat_agent", chat_agent_node)
    wf.add_node("formatter", formatter_node)

    wf.set_entry_point("supervisor")

    wf.add_conditional_edges(
        "supervisor",
        _route,
        {
            "rag": "researcher",
            "action": "action_agent",
            "chat": "chat_agent",
        },
    )

    wf.add_edge("researcher", "formatter")
    wf.add_edge("action_agent", "formatter")
    wf.add_edge("chat_agent", "formatter")
    wf.add_edge("formatter", END)

    return wf.compile()
