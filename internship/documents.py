import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    page: int


def split_text(text, size=800, overlap=120):
    if size < 1 or not 0 <= overlap < size:
        raise ValueError('Require size > 0 and 0 <= overlap < size.')
    text = re.sub(r'[ \t]+', ' ', text).strip()
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = text.rfind(' ', start + size // 2, end)
            if boundary > start:
                end = boundary
        part = text[start:end].strip()
        if part:
            yield part
        if end == len(text):
            break
        start = max(start + 1, end - overlap)


def load_chunks(paths, size=800, overlap=120):
    chunks = []
    for path in paths:
        path = Path(path)
        if path.suffix.lower() == '.pdf':
            try:
                from pypdf import PdfReader
            except ImportError as exc:
                raise RuntimeError('Install requirements.txt to read PDF files.') from exc
            reader = PdfReader(path)
            if reader.is_encrypted:
                raise ValueError(f'{path.name}: encrypted PDFs are unsupported.')
            pages = [(i + 1, page.extract_text() or '') for i, page in enumerate(reader.pages)]
        elif path.suffix.lower() in ('.txt', '.md'):
            pages = [(1, path.read_text(encoding='utf-8-sig'))]
        else:
            raise ValueError(f'Unsupported document type: {path.suffix}')
        before = len(chunks)
        for page, text in pages:
            for index, part in enumerate(split_text(text, size, overlap)):
                raw_id = f'{path.name}|{page}|{index}|{part}'
                chunks.append(Chunk(hashlib.sha256(raw_id.encode()).hexdigest(), part, path.name, page))
        if len(chunks) == before:
            raise ValueError(f'{path.name}: no readable text. Scanned PDFs require OCR, which is not included.')
    return chunks
