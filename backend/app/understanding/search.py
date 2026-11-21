"""Find the clauses relevant to a question, within one policy.

Hybrid search: a local multilingual embedding model (understands English, Hindi and Hinglish
by meaning) plus exact keyword overlap (catches specific words like "knee" or "cataract").
Policies have tens to a few hundred clauses and search is always within one policy, so the
vectors live next to each clause and are compared in memory: no vector database needed.
"""

import logging
import math
import re
import threading
from collections import Counter
from dataclasses import dataclass

import numpy as np

from ..config import BASE_DIR, get_settings

log = logging.getLogger(__name__)
_model = None
_model_failed = False
_lock = threading.Lock()

SEMANTIC_WEIGHT = 0.65
_STOP = set("a an the of to in on for and or is are be by with from as at it this that if any all your you can i my me what how when which who does do will shall may not no under per".split())


def _get_model():
    global _model, _model_failed
    if _model is not None or _model_failed or not get_settings().embeddings_enabled:
        return _model
    with _lock:
        if _model is None and not _model_failed:
            try:
                from fastembed import TextEmbedding

                _model = TextEmbedding(get_settings().embedding_model, cache_dir=str(BASE_DIR / "models"))
            except Exception:  # offline on first run, disk full, ...: fall back to keywords
                log.exception("Embedding model unavailable; clause search will use keywords only")
                _model_failed = True
    return _model


def embed(texts: list[str]) -> np.ndarray | None:
    """Unit-length float32 vectors, one row per text, or None when no model is available."""
    model = _get_model()
    if model is None or not texts:
        return None
    with _lock:
        vectors = np.array(list(model.embed(texts)), dtype=np.float32)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-9
    return vectors


def to_bytes(v: np.ndarray) -> bytes:
    return v.astype(np.float32).tobytes()


def from_bytes(b: bytes) -> np.ndarray:
    return np.frombuffer(b, dtype=np.float32)


def clause_search_text(ref: str, title: str, section: str, text: str) -> str:
    return f"{ref} {title}. {section}. {text}"[:1500]


def _tokens(s: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9ऀ-ॿ]+", s.lower()) if w not in _STOP and len(w) > 1]


@dataclass
class SearchDoc:
    """What search needs from a clause (kept independent of the database model)."""

    key: int
    ref: str
    text: str  # clause_search_text(...)
    vector: np.ndarray | None


def search(query: str, docs: list[SearchDoc], k: int = 5) -> list[tuple[int, float]]:
    """Returns [(doc key, score 0..1)], best first."""
    if not docs or not query.strip():
        return []

    # Keyword part: IDF-weighted overlap, scaled to 0..1
    doc_tokens = [set(_tokens(d.text)) for d in docs]
    df = Counter(t for toks in doc_tokens for t in toks)
    n = len(docs)
    q_tokens = set(_tokens(query))
    keyword = np.zeros(n, dtype=np.float32)
    for i, toks in enumerate(doc_tokens):
        keyword[i] = sum(math.log(1 + n / df[t]) for t in q_tokens & toks)
    if keyword.max() > 0:
        keyword /= keyword.max()

    # "clause 4.2" or "section 4.2" in the question points straight at that clause
    for ref in re.findall(r"(?:clause|section)\s+(\d+(?:\.\d+)*)", query, re.IGNORECASE):
        for i, d in enumerate(docs):
            if d.ref == ref:
                keyword[i] = 2.0

    scores = keyword
    vectors = [d.vector for d in docs]
    if all(v is not None for v in vectors):
        q = embed([query])
        if q is not None:
            semantic = np.clip(np.stack(vectors) @ q[0], 0, 1)
            scores = SEMANTIC_WEIGHT * semantic + (1 - SEMANTIC_WEIGHT) * keyword

    order = np.argsort(-scores)[:k]
    return [(docs[i].key, float(min(scores[i], 1.0))) for i in order if scores[i] > 0]
