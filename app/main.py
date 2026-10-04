from pathlib import Path
import shutil
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.chunker import chunk_text
from app.config import settings
from app.document_loader import load_document
from app.llm import generate_answer
from app.vector_store import VectorStore


app = FastAPI(
    title="Intelligent Corporate Knowledge Assistant API",
    description="Simple RAG backend for internal corporate policy documents.",
    version="1.0.0",
)

vector_store = VectorStore()


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "documents_indexed": vector_store.collection.count(),
        "llm_provider": settings.llm_provider,
    }


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in {".pdf", ".txt", ".md"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, and MD files are supported.",
        )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp:
        shutil.copyfileobj(file.file, temp)
        temp_path = Path(temp.name)

    try:
        text = load_document(temp_path)
        chunks = chunk_text(
            text,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
        )

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="The uploaded document contains no readable text.",
            )

        count = vector_store.add_chunks(
            chunks=chunks,
            source_name=file.filename or "unknown",
        )

        return {
            "message": "Document ingested successfully.",
            "filename": file.filename,
            "chunks_created": count,
        }

    finally:
        temp_path.unlink(missing_ok=True)


@app.post("/chat")
def chat(request: ChatRequest):
    matches = vector_store.search(
        request.question,
        top_k=settings.top_k,
    )

    if not matches:
        raise HTTPException(
            status_code=400,
            detail="No documents have been ingested yet.",
        )

    # Retrieval-level guardrail.
    # Cosine similarity close to 1 means strong semantic similarity.
    relevant_matches = [
        match
        for match in matches
        if match["similarity"] >= settings.similarity_threshold
    ]

    if not relevant_matches:
        return {
            "answer": "Maaf, saya hanya bisa menjawab terkait kebijakan internal perusahaan.",
            "sources": [],
        }

    try:
        answer = generate_answer(
            question=request.question,
            matches=relevant_matches,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider error: {str(exc)}",
        )

    return {
        "answer": answer,
        "sources": [
            {
                "document": match["source"],
                "chunk_index": match["chunk_index"],
                "similarity": round(match["similarity"], 4),
            }
            for match in relevant_matches
        ],
    }
