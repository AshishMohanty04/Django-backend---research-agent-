# myapp/research_agent/models.py
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import threading

# Thread-safe lazy loading
_lock = threading.Lock()
_state = {
    "summarizer": None,
    "embedder": None
}

def load_models():
    """
    Loads models only once for the entire Django server.
    - Summarizer: BART (best for summarization)
    - Embedder: Facebook BERT (semantic embeddings)
    """
    with _lock:
        if _state["summarizer"] is None:
            print("Loading summarization model (BART)...")
            _state["summarizer"] = pipeline(
                task="summarization",
                model="facebook/bart-large-cnn",
                device=-1  # CPU; use 0 if GPU
            )

        if _state["embedder"] is None:
            print("Loading embedding model (Facebook BERT)...")
            _state["embedder"] = SentenceTransformer(
                "bert-base-uncased"
            )

    return _state["summarizer"], _state["embedder"]
