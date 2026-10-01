from typing import List

from sentence_transformers import SentenceTransformer


# Lightweight sentence-transformer model suitable for
# semantic search and document retrieval.
MODEL_NAME = "all-MiniLM-L6-v2"


# Load the model once when the service starts.
# Reusing the same model avoids loading it for every request.
_embedding_model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> List[float]:
    """
    Convert a single text chunk into an embedding vector.

    Args:
        text: Text that needs to be converted into a vector.

    Returns:
        A list of floating-point values representing
        the semantic meaning of the text.
    """

    # Convert the text into its numerical embedding.
    embedding = _embedding_model.encode(
        text,
        convert_to_numpy=True
    )

    # Convert NumPy array to a normal Python list
    # so it can easily be stored/transmitted.
    return embedding.tolist()


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple text chunks.

    Args:
        texts: List of document chunks.

    Returns:
        List of embedding vectors, one vector per chunk.
    """

    # Encode all chunks together for better efficiency.
    embeddings = _embedding_model.encode(
        texts,
        convert_to_numpy=True
    )

    return embeddings.tolist()