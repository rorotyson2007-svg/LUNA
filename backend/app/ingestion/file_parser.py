from pathlib import Path
from io import BytesIO

from pypdf import PdfReader
from docx import Document


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}


def extract_text_from_file(
    filename: str,
    file_bytes: bytes,
) -> dict:

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported types: PDF, DOCX, TXT, MD."
        )

    # ============================================================
    # TEXT / MARKDOWN
    # ============================================================

    if extension in {".txt", ".md"}:

        text = file_bytes.decode(
            "utf-8",
            errors="replace",
        )

        return {
            "filename": filename,
            "file_type": extension.replace(".", "").upper(),
            "text": text.strip(),
            "page_count": None,
        }

    # ============================================================
    # PDF
    # ============================================================

    if extension == ".pdf":

        reader = PdfReader(
            BytesIO(file_bytes)
        )

        pages = []

        for index, page in enumerate(reader.pages):

            page_text = page.extract_text() or ""

            pages.append(
                f"[PAGE {index + 1}]\n{page_text}"
            )

        text = "\n\n".join(pages)

        return {
            "filename": filename,
            "file_type": "PDF",
            "text": text.strip(),
            "page_count": len(reader.pages),
        }

    # ============================================================
    # DOCX
    # ============================================================

    if extension == ".docx":

        document = Document(
            BytesIO(file_bytes)
        )

        paragraphs = []

        for paragraph in document.paragraphs:

            content = paragraph.text.strip()

            if content:
                paragraphs.append(content)

        text = "\n\n".join(paragraphs)

        return {
            "filename": filename,
            "file_type": "DOCX",
            "text": text.strip(),
            "page_count": None,
        }

    raise ValueError(
        "Could not determine how to read this file."
    )