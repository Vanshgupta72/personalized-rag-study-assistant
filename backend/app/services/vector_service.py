from typing import List

import chromadb

from backend.app.core.config import settings


# -------------------------------------------------
# ChromaDB client
# -------------------------------------------------

chroma_client = chromadb.PersistentClient(
    path=settings.VECTOR_DB_PATH
)


# -------------------------------------------------
# Document collection
# -------------------------------------------------

document_collection = chroma_client.get_or_create_collection(
    name="study_documents"
)


# -------------------------------------------------
# Add document chunks
# -------------------------------------------------

def add_document_chunks(
    document_id: int,
    user_id: int,
    subject_id: int | None,
    topic_id: int | None,
    chunks: List[str],
    embeddings: List[List[float]],
    filename: str
) -> None:
    """
    Store document chunks and their embeddings
    in ChromaDB.

    Each chunk receives metadata containing:
    - user_id
    - document_id
    - subject_id
    - topic_id
    - chunk_index
    - filename
    """

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks must match "
            "number of embeddings."
        )

    # Create a unique ID for every chunk.
    chunk_ids = [
        f"document_{document_id}_chunk_{index}"
        for index in range(len(chunks))
    ]

    # Store metadata with every chunk.
    metadatas = [
        {
            "user_id": user_id,
            "document_id": document_id,
            "subject_id": subject_id,
            "topic_id": topic_id,
            "chunk_index": index,
            "filename": filename
        }
        for index in range(len(chunks))
    ]

    document_collection.add(
        ids=chunk_ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )


# -------------------------------------------------
# Delete all chunks belonging to a document
# -------------------------------------------------

def delete_document_chunks(
    document_id: int
) -> None:
    """
    Delete every ChromaDB chunk belonging
    to the specified document.
    """

    document_collection.delete(
        where={
            "document_id": document_id
        }
    )