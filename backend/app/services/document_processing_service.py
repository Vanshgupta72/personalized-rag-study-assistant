from pathlib import Path

from backend.app.services.chunking_service import chunk_text
from backend.app.services.embedding_service import generate_embeddings
from backend.app.services.extraction_service import (
    extract_text_from_stored_document
)
from backend.app.services.vector_service import add_document_chunks


def process_document(
    document_id: int,
    user_id: int,
    stored_filename: str,
    original_filename: str,
    subject_id: int | None,
    topic_id: int | None
) -> int:
    """
    Process an uploaded study document and store its
    chunks and embeddings in the vector database.

    Processing pipeline:

    Stored Document
        ↓
    Text Extraction
        ↓
    Text Chunking
        ↓
    Embedding Generation
        ↓
    Vector Database
    """

    # ---------------------------------------------
    # 1. Extract text
    # ---------------------------------------------

    text = extract_text_from_stored_document(
        stored_filename
    )

    if not text.strip():
        raise ValueError(
            "No readable text was found in the document."
        )

    # ---------------------------------------------
    # 2. Create chunks
    # ---------------------------------------------

    chunks = chunk_text(text)

    if not chunks:
        raise ValueError(
            "Document did not produce any text chunks."
        )

    # ---------------------------------------------
    # 3. Generate embeddings
    # ---------------------------------------------

    embeddings = generate_embeddings(chunks)

    # ---------------------------------------------
    # 4. Store chunks + metadata in ChromaDB
    # ---------------------------------------------

    add_document_chunks(
        document_id=document_id,
        user_id=user_id,
        subject_id=subject_id,
        topic_id=topic_id,
        chunks=chunks,
        embeddings=embeddings,
        filename=original_filename
    )

    return len(chunks)