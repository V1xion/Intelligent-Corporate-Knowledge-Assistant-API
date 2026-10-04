def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100) -> list[str]:
    """Simple character-based chunking with overlap.

    It keeps chunks small enough for retrieval while preserving nearby context.
    """
    text = " ".join(text.split())

    if not text:
        return []

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks
