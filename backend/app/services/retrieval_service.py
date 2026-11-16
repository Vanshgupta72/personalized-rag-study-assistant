from typing import Any, Dict, List

from backend.app.services.embedding_service import generate_embedding
from backend.app.services.vector_service import document_collection


# Provisional relevance cutoff calibrated against current sample queries.
MAX_L2_DISTANCE = 1.2


def search_documents(
    query: str,
    user_id: int,
    top_k: int = 3,
    subject_id: int | None = None,
    topic_id: int | None = None
) -> List[Dict[str, Any]]:
    """
    Search the authenticated user's document chunks.

    Optional subject/topic filters allow retrieval to be
    scoped to a particular area of the student's knowledge base.
    """

    query_embedding = generate_embedding(query)

    # ---------------------------------------------
    # Build metadata filters
    # ---------------------------------------------

    filters = [
        {
            "user_id": user_id
        }
    ]

    if subject_id is not None:
        filters.append(
            {
                "subject_id": subject_id
            }
        )

    if topic_id is not None:
        filters.append(
            {
                "topic_id": topic_id
            }
        )

    # ChromaDB expects:
    # one condition → direct dictionary
    # multiple conditions → $and
    if len(filters) == 1:
        where_filter = filters[0]
    else:
        where_filter = {
            "$and": filters
        }

    # ---------------------------------------------
    # Semantic search
    # ---------------------------------------------

    results = document_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter
    )

    retrieved_chunks = []

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        if distance > MAX_L2_DISTANCE:
            continue
        retrieved_chunks.append(
            {
                "text": document,
                "metadata": metadata,
                "distance": distance
            }
        )

    return retrieved_chunks