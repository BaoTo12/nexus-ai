import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from app.agents.graph import AgentState
from app.config import get_settings
from app.tools.database import query_database
from app.tools.email_tool import send_email
from app.tools.weather import get_weather

settings = get_settings()

TOOLS_PROMPT = """\
You are a tool-calling assistant. Based on the user's request, decide which tool to call.

Available tools:
1. get_weather       — args: {"location": "<city name>"}
2. query_database    — args: {"sql_query": "<SELECT ...>"}
3. send_email        — args: {"to": "<email>", "subject": "<subject>", "body": "<body>"}

Rules:
- Respond ONLY with a valid JSON object — no markdown, no explanation.
- If you have all required arguments, output:
  {"tool": "<tool_name>", "args": {<args>}}
- If required arguments are MISSING, output:
  {"tool": "clarify", "message": "<polite question asking for what you need>"}

Examples:
User: "What's the weather in Paris?"
→ {"tool": "get_weather", "args": {"location": "Paris"}}

User: "Send an email"
→ {"tool": "clarify", "message": "Sure! Who should I send the email to, and what's the subject?"}
"""

TOOLS_MAP = {
    "get_weather": get_weather,
    "query_database": query_database,
    "send_email": send_email,
}


async def action_agent_node(state: AgentState) -> dict:
    llm = ChatOllama(
        model=settings.CHAT_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0,
    )

    user_message = state["messages"][-1].content

    try:
        resp = await llm.ainvoke(
            [SystemMessage(content=TOOLS_PROMPT), HumanMessage(content=user_message)]
        )

        raw = resp.content.strip()

        # Strip markdown code fences if the model adds them
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(
                line for line in lines if not line.startswith("```")
            ).strip()

        tool_call = json.loads(raw)

    except (json.JSONDecodeError, Exception):
        return {
            "final_response": (
                "I wasn't sure which action to take. "
                "Could you rephrase your request? For example: "
                "*\"What's the weather in Tokyo?\"* or "
                "*\"Send an email to alice@example.com about the meeting\"*."
            )
        }

    # ── Clarification needed ──────────────────────────────────────────────
    if tool_call.get("tool") == "clarify":
        return {"final_response": tool_call.get("message", "Could you provide more details?")}

    # ── Execute tool ──────────────────────────────────────────────────────
    tool_name = tool_call.get("tool")
    tool_args = tool_call.get("args", {})

    if tool_name not in TOOLS_MAP:
        return {"final_response": f"Unknown tool requested: `{tool_name}`."}

    try:
        result = await TOOLS_MAP[tool_name](**tool_args)
        return {"tool_result": result, "final_response": result}
    except TypeError as exc:
        return {
            "final_response": (
                f"I couldn't execute **{tool_name}** — missing argument: {exc}. "
                "Please provide the missing details."
            )
        }
