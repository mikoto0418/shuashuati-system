"""
文本提取工具
"""
from pathlib import Path
from typing import Callable, Dict

import pdfplumber
from docx import Document


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_docx(path: Path) -> str:
    document = Document(path)
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def _read_pdf(path: Path) -> str:
    texts: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            texts.append(page_text)
    return "\n".join(texts)


READERS: Dict[str, Callable[[Path], str]] = {
    ".txt": _read_txt,
    ".doc": _read_docx,
    ".docx": _read_docx,
    ".pdf": _read_pdf,
}


def extract_text(file_path: Path) -> str:
    """
    根据文件后缀提取文本内容。
    """
    suffix = file_path.suffix.lower()
    reader = READERS.get(suffix)
    if reader is None:
        raise ValueError(f"暂不支持的文件类型：{suffix}")
    return reader(file_path)
