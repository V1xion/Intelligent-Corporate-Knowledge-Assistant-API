from app.chunker import chunk_text


def test_chunk_text_returns_chunks():
    text = "A" * 1500
    chunks = chunk_text(text, chunk_size=500, overlap=100)

    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)


def test_empty_text():
    assert chunk_text("") == []
