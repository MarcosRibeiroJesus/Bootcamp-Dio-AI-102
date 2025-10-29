from bs4 import BeautifulSoup
import requests
from io import BytesIO
from typing import Optional
import pdfplumber
import docx


def extract_text_from_url(url: str) -> Optional[str]:
    """Fetch URL and extract visible text using BeautifulSoup."""
    resp = requests.get(url, timeout=15)
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    return text


def extract_text_from_docx(file_obj: BytesIO) -> Optional[str]:
    """Extract text from a docx file-like object."""
    try:
        # python-docx's Document can accept a file-like object
        document = docx.Document(file_obj)
        paragraphs = [p.text for p in document.paragraphs if p.text]
        return "\n\n".join(paragraphs)
    except Exception:
        return None


def extract_text_from_pdf(file_obj: BytesIO) -> Optional[str]:
    """Extract text from a PDF using pdfplumber."""
    try:
        text_parts = []
        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n\n".join(text_parts)
    except Exception:
        return None
