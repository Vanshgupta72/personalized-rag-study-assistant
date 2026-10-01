from typing import List


# Maximum number of characters in one chunk.
# Keeping chunks reasonably small improves retrieval quality.
DEFAULT_CHUNK_SIZE = 1000

# Number of characters repeated between consecutive chunks.
# This overlap helps preserve context at chunk boundaries.
DEFAULT_CHUNK_OVERLAP = 200


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
) -> List[str]:
    """
    Split extracted document text into overlapping chunks.

    Args:
        text: Extracted text from a PDF or PPTX.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Characters shared between adjacent chunks.

    Returns:
        A list of cleaned text chunks.
    """

    # Validate chunk configuration.
    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )

    # Remove unnecessary whitespace.
    cleaned_text = " ".join(text.split())

    # Nothing to process.
    if not cleaned_text:
        return []

    chunks = []

    start = 0
    text_length = len(cleaned_text)

    while start < text_length:

        # Calculate the end position of the current chunk.
        end = min(start + chunk_size, text_length)

        # Extract the chunk.
        chunk = cleaned_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        # Stop after the final chunk.
        if end >= text_length:
            break

        # Move forward while preserving overlap.
        start = end - chunk_overlap

    return chunks