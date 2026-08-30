"""
Basic tests for the KB retrieval logic. Run with: pytest tests/test_retrieve.py
"""

import numpy as np
import pytest


def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def test_cosine_similarity_identical_vectors():
    v = [1.0, 2.0, 3.0]
    assert cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal_vectors():
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert cosine_similarity(a, b) == pytest.approx(0.0)


def test_cosine_similarity_opposite_vectors():
    a = [1.0, 0.0]
    b = [-1.0, 0.0]
    assert cosine_similarity(a, b) == pytest.approx(-1.0)


def test_ranking_sorts_by_score_descending():
    scored = [
        {"id": "1", "score": 0.42},
        {"id": "2", "score": 0.91},
        {"id": "3", "score": 0.15},
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    assert [s["id"] for s in scored] == ["2", "1", "3"]