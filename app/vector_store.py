from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

from app.config import settings


class VectorStore:
    def __init__(self) -> None:
        Path("data/chroma").mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path="data/chroma")
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.embedding_model = SentenceTransformer(settings.embedding_model)

    def add_chunks(self, chunks: list[str], source_name: str) -> int:
        if not chunks:
            return 0

        ids = [
            f"{source_name}-{i}"
            for i in range(len(chunks))
        ]

        embeddings = self.embedding_model.encode(
            chunks,
            normalize_embeddings=True,
        ).tolist()

        metadata = [
            {
                "source": source_name,
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        # Re-ingesting the same filename replaces its previous chunks.
        try:
            self.collection.delete(where={"source": source_name})
        except Exception:
            pass

        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadata,
        )

        return len(chunks)

    def search(self, query: str, top_k: int = 4) -> list[dict]:
        if self.collection.count() == 0:
            return []

        query_embedding = self.embedding_model.encode(
            [query],
            normalize_embeddings=True,
        ).tolist()

        result = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        matches = []
        for document, metadata, distance in zip(
            documents, metadatas, distances
        ):
            # Chroma cosine distance: 0 = identical, 2 = opposite.
            similarity = 1 - float(distance)

            matches.append(
                {
                    "text": document,
                    "source": metadata["source"],
                    "chunk_index": metadata["chunk_index"],
                    "similarity": similarity,
                }
            )

        return matches
