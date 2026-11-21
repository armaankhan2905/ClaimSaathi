from pathlib import Path

import numpy as np
import pytest

from app.config import BASE_DIR, get_settings
from app.understanding import search as search_mod
from app.understanding.search import SearchDoc, clause_search_text, embed, from_bytes, search, to_bytes

CLAUSES = [
    ("3.2", "Room, boarding and nursing", "Room rent is payable up to 1% of the Sum Insured per day."),
    ("4.2", "Specified illnesses and procedures", "Joint replacement surgery, including knee and hip replacement; cataract; hernia. Payable after 24 months."),
    ("9", "Grievances", "Write to the Grievance Officer. You may approach the Insurance Ombudsman."),
    ("3.7", "Maternity expenses", "Childbirth expenses up to Rs. 50,000 after 36 months."),
]


def _docs(with_vectors: bool):
    texts = [clause_search_text(r, t, "", b) for r, t, b in CLAUSES]
    vecs = embed(texts) if with_vectors else None
    return [SearchDoc(i, CLAUSES[i][0], texts[i], vecs[i] if vecs is not None else None) for i in range(len(CLAUSES))]


def test_keyword_search_without_model(monkeypatch):
    monkeypatch.setattr(get_settings(), "embeddings_enabled", False)
    monkeypatch.setattr(search_mod, "_model", None)
    docs = _docs(with_vectors=False)
    assert search("Is knee replacement covered?", docs)[0][0] == 1
    assert search("room rent limit", docs)[0][0] == 0
    assert search("ombudsman", docs, k=1) == [(2, 1.0)]
    assert search("", docs) == []


def test_clause_number_in_question_wins(monkeypatch):
    monkeypatch.setattr(get_settings(), "embeddings_enabled", False)
    monkeypatch.setattr(search_mod, "_model", None)
    assert search("what does clause 3.7 say", _docs(False))[0][0] == 3


def test_vector_round_trip():
    v = np.array([0.1, -0.5, 0.25], dtype=np.float32)
    assert np.allclose(from_bytes(to_bytes(v)), v)


MODEL_CACHED = (BASE_DIR / "models").exists() and any((BASE_DIR / "models").iterdir())


@pytest.mark.skipif(not MODEL_CACHED, reason="embedding model not downloaded yet")
@pytest.mark.parametrize(
    "question,expected_ref",
    [
        ("Is knee replacement covered?", "4.2"),
        ("घुटने का ऑपरेशन कब से कवर होगा?", "4.2"),  # Hindi
        ("knee surgery kab se cover hogi", "4.2"),  # Hinglish
        ("how much room rent can I claim", "3.2"),
        ("where can I complain about my insurer", "9"),
        ("delivery of a baby", "3.7"),
    ],
)
def test_multilingual_semantic_search(question, expected_ref):
    docs = _docs(with_vectors=True)
    best = search(question, docs, k=1)[0][0]
    assert docs[best].ref == expected_ref
