# myapp/research_agent/memory.py
import faiss
import numpy as np

# Facebook BERT embedding dimension
EMBEDDING_DIM = 768

_memory = {
    "texts": [],
    "metas": [],
    "faiss_index": faiss.IndexFlatL2(EMBEDDING_DIM),
}

def init_memory():
    """
    Initialize / reset memory store.
    """
    global _memory
    _memory = {
        "texts": [],
        "metas": [],
        "faiss_index": faiss.IndexFlatL2(EMBEDDING_DIM),
    }

def add_to_memory(embedder, query, summary, url=None):
    """
    Adds a summarized document to vector memory.
    """
    vec = embedder.encode(summary)

    if vec.shape[0] != EMBEDDING_DIM:
        raise ValueError(
            f"Embedding dimension mismatch: expected {EMBEDDING_DIM}, got {vec.shape[0]}"
        )

    _memory["faiss_index"].add(
        np.array([vec]).astype("float32")
    )

    _memory["texts"].append(summary)
    _memory["metas"].append({
        "query": query,
        "url": url
    })

def search_memory(embedder, query, top_k=3):
    if len(_memory["texts"]) == 0:
        return []

    qvec = embedder.encode(query)
    D, I = _memory["faiss_index"].search(
        np.array([qvec]).astype("float32"),
        top_k
    )

    results = []
    for idx in I[0]:
        if idx < len(_memory["texts"]):
            results.append({
                "summary": _memory["texts"][idx],
                "meta": _memory["metas"][idx]
            })

    return results
