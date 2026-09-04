import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

EMBED_MODEL = "BAAI/bge-small-en-v1.5"


class Retriever:
    def __init__(self):
        self.model = None
        self.index = None
        self.chunks = None

    def load(self):
        self.model = SentenceTransformer(EMBED_MODEL)
        self.index = faiss.read_index("data/faiss.index")
        with open("data/chunks_meta.json") as f:
            self.chunks = json.load(f)

    def search(self, query: str, k: int = 3):
        query_embedding = self.model.encode([query], normalize_embeddings=True)
        scores, indices = self.index.search(np.array(query_embedding, dtype="float32"), k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            chunk = self.chunks[idx]
            results.append({
                "text": chunk["text"],
                "source": chunk["source"],
                "section": chunk["section"],
                "score": float(score),
            })
        return results


if __name__ == "__main__":
    r = Retriever()
    r.load()
    results = r.search("service running out of memory")
    for res in results:
        print(f"{res['score']:.3f} | {res['source']}: {res['text'][:80]}")