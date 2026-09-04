import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

chunks = []
with open("data/knowledge_base.jsonl") as f:
    for line in f:
        if line.strip():
            chunks.append(json.loads(line))

print(f"Loaded {len(chunks)} chunks")

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
texts = [c["text"] for c in chunks]
embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
print(f"Generated embeddings with shape: {embeddings.shape}")

dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(np.array(embeddings, dtype="float32"))
print(f"Index built with {index.ntotal} vectors")

faiss.write_index(index, "data/faiss.index")
with open("data/chunks_meta.json", "w") as f:
    json.dump(chunks, f, indent=2)
print("Saved index and metadata to disk")


query = "database connections timing out"
query_embedding = model.encode([query], normalize_embeddings=True)

scores, indices = index.search(np.array(query_embedding, dtype="float32"), k=2)

print(f"\nQuery: '{query}'")
for score, idx in zip(scores[0], indices[0]):
    print(f"  Score: {score:.3f} | {chunks[idx]['source']} / {chunks[idx]['section']}: {chunks[idx]['text'][:80]}...")