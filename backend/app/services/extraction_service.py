from pathlib import Path

import pymupdf
from pptx import Presentation


def extract_text_from_pdf(file_path: Path) -> str:
    """
    Extract text from every page of a PDF file.

    Args:
        file_path: Path to the PDF file.

    Returns:
        All extracted page text combined into one string.
    """

    extracted_text = []

    # Open the PDF document.
    document = pymupdf.open(file_path)

    try:
        # Process every page in the document.
        for page in document:
            page_text = page.get_text()

            if page_text.strip():
                extracted_text.append(page_text.strip())

    finally:
        # Always close the PDF after extraction.
        document.close()

    return "\n\n".join(extracted_text)


def extract_text_from_pptx(file_path: Path) -> str:
    """
    Extract text from all slides of a PPTX presentation.

    Args:
        file_path: Path to the PPTX file.

    Returns:
        All extracted slide text combined into one string.
    """

    extracted_text = []

    # Open the PowerPoint presentation.
    presentation = Presentation(file_path)

    # Process every slide.
    for slide in presentation.slides:

        # Process every shape on the slide.
        for shape in slide.shapes:

            # Only text-containing shapes are relevant.
            if hasattr(shape, "text") and shape.text.strip():
                extracted_text.append(shape.text.strip())

    return "\n\n".join(extracted_text)


def extract_text(file_path: Path) -> str:
    """
    Automatically select the correct extraction method
    based on the file extension.
    """

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension == ".pptx":
        return extract_text_from_pptx(file_path)

    raise ValueError(
        "Unsupported file type. Only PDF and PPTX are supported."
    )

def extract_text_from_stored_document(stored_filename: str) -> str:
    """
    Locate a previously uploaded document using its stored filename
    and extract its text.

    The database stores the unique filename, while the actual file
    is stored inside data/uploads/.
    """

    # Build the path to the uploaded document.
    file_path = Path("data/uploads") / stored_filename

    # Make sure the physical file actually exists.
    if not file_path.exists():
        raise FileNotFoundError(
            f"Stored document not found: {stored_filename}"
        )

    # Reuse the existing PDF/PPTX extraction logic.
    return extract_text(file_path)