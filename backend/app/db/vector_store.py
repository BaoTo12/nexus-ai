import uuid

from sqlalchemy import select

from app.config import get_settings
from app.db.models import Document, DocumentEmbedding
from app.db.session import AsyncSessionLocal

settings = get_settings()


def _get_embeddings():
    from langchain_ollama import OllamaEmbeddings
    return OllamaEmbeddings(
        model=settings.EMBED_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )


async def store_embeddings(document_id: uuid.UUID, chunks: list[str]) -> None:
    """Embed text chunks and store them in pgvector."""
    embeddings_model = _get_embeddings()
    vectors = await embeddings_model.aembed_documents(chunks)

    async with AsyncSessionLocal() as session:
        for chunk_text, vector in zip(chunks, vectors):
            embedding = DocumentEmbedding(
                document_id=document_id,
                chunk_text=chunk_text,
                embedding=vector,
            )
            session.add(embedding)
        await session.commit()


async def similarity_search(query: str, top_k: int = 3) -> list[str]:
    """Return the top-k most similar chunks for a query string."""
    embeddings_model = _get_embeddings()
    query_vector = await embeddings_model.aembed_query(query)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(DocumentEmbedding.chunk_text)
            .order_by(DocumentEmbedding.embedding.cosine_distance(query_vector))
            .limit(top_k)
        )
        return list(result.scalars().all())
