from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

from app.agents.graph import AgentState
from app.config import get_settings
from app.db.vector_store import similarity_search

settings = get_settings()


async def researcher_node(state: AgentState) -> dict:
    """RAG node: similarity-search pgvector, augment prompt, generate answer."""
    llm = ChatOllama(
        model=settings.CHAT_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )

    user_query = state["messages"][-1].content

    # ── Retrieve relevant chunks ──────────────────────────────────────────
    docs = await similarity_search(user_query, top_k=4)

    if docs:
        context = "\n\n---\n\n".join(docs)
        prompt = (
            "Use the following context from the knowledge base to answer the question. "
            "If the context does not contain the answer, say so clearly.\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION: {user_query}"
        )
    else:
        prompt = (
            f"The user asked: {user_query}\n\n"
            "No relevant documents were found in the knowledge base. "
            "Let the user know politely and offer to help in another way."
        )

    response = await llm.ainvoke([HumanMessage(content=prompt)])

    return {
        "retrieved_docs": docs,
        "final_response": response.content,
    }
