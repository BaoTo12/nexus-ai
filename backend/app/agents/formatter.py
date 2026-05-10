from app.agents.graph import AgentState


async def formatter_node(state: AgentState) -> dict:
    """
    Final node in the graph.
    Ensures final_response is always populated — provides a graceful fallback
    if upstream agent failed or produced nothing.
    """
    response = state.get("final_response", "").strip()

    if not response:
        error = state.get("error", "")
        if error:
            response = (
                f"⚠️ I encountered an issue processing your request.\n\n"
                f"**Error:** {error}\n\n"
                "Please try rephrasing or ask something else."
            )
        else:
            response = (
                "I'm sorry, I wasn't able to generate a response. "
                "Please try again."
            )

    return {"final_response": response}
