from pathlib import Path
from pypdf import PdfReader

def extract_pdf_text(file_path: str | Path) -> str:
    """Extract text from a normal text-based PDF."""
    reader = PdfReader(str(file_path))
    pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(pages).strip()

def clean_text(text: str) -> str:
    lines = [line.strip() for line in text.replace("\r", "\n").split("\n")]
    return "\n".join(line for line in lines if line).strip()
