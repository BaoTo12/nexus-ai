import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.db.models import Document
from app.db.session import get_db
from app.db.vector_store import store_embeddings

router = APIRouter()


@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a PDF or text file.
    The file is chunked, embedded via Ollama, and stored in pgvector.
    """
    filename = file.filename or "unknown"
    content_type = file.content_type or ""

    # ── Read file content ───────────────────────────────────────────────────
    raw = await file.read()

    if filename.endswith(".pdf") or "pdf" in content_type:
        text = _extract_pdf(raw)
    else:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Could not decode file as UTF-8 text.")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Uploaded file appears to be empty.")

    # ── Chunk text ──────────────────────────────────────────────────────────
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)

    # ── Save document record ────────────────────────────────────────────────
    doc = Document(
        filename=filename,
        content=text[:5000],  # store first 5k chars as preview
        doc_metadata={"chunks": len(chunks), "uploaded_by": current_user["sub"]},
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # ── Embed and store chunks ──────────────────────────────────────────────
    await store_embeddings(doc.id, chunks)

    return {
        "document_id": str(doc.id),
        "filename": filename,
        "chunks": len(chunks),
        "message": f"Successfully ingested '{filename}' into the knowledge base.",
    }


def _extract_pdf(raw_bytes: bytes) -> str:
    """Extract text from PDF bytes using pypdf."""
    import io
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(raw_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)
