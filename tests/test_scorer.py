"""Tests for csvdiff.scorer."""

import pytest

from csvdiff.scorer import (
    SimilarityScore,
    ScorerError,
    score_rows,
    rank_candidates,
)


# ---------------------------------------------------------------------------
# SimilarityScore validation
# ---------------------------------------------------------------------------

def test_similarity_score_valid():
    s = SimilarityScore(score=0.75, matched=3, total=4)
    assert s.score == 0.75


def test_similarity_score_invalid_score_raises():
    with pytest.raises(ScorerError):
        SimilarityScore(score=1.5, matched=3, total=4)


def test_similarity_score_negative_total_raises():
    with pytest.raises(ScorerError):
        SimilarityScore(score=0.5, matched=1, total=-1)


# ---------------------------------------------------------------------------
# score_rows
# ---------------------------------------------------------------------------

def test_score_rows_identical():
    row = {"a": "1", "b": "2"}
    s = score_rows(row, row)
    assert s.score == 1.0
    assert s.matched == 2


def test_score_rows_no_match():
    s = score_rows({"a": "1"}, {"a": "2"})
    assert s.score == 0.0
    assert s.matched == 0


def test_score_rows_partial_match():
    s = score_rows({"a": "1", "b": "X"}, {"a": "1", "b": "Y"})
    assert s.matched == 1
    assert s.total == 2
    assert s.score == pytest.approx(0.5)


def test_score_rows_disjoint_keys():
    s = score_rows({"a": "1"}, {"b": "1"})
    # 'a' and 'b' are different keys; neither matches the other
    assert s.total == 2
    assert s.matched == 0


def test_score_rows_empty_rows():
    s = score_rows({}, {})
    assert s.score == 1.0
    assert s.total == 0


# ---------------------------------------------------------------------------
# rank_candidates
# ---------------------------------------------------------------------------

def test_rank_candidates_returns_sorted():
    target = {"a": "1", "b": "2", "c": "3"}
    candidates = [
        {"a": "1", "b": "X", "c": "X"},   # 1/3
        {"a": "1", "b": "2", "c": "X"},   # 2/3
        {"a": "1", "b": "2", "c": "3"},   # 3/3  ← best
    ]
    ranked = rank_candidates(target, candidates)
    assert ranked[0][1] == 2   # index of the perfect match
    assert ranked[0][0].score == 1.0


def test_rank_candidates_respects_limit():
    target = {"x": "1"}
    candidates = [{"x": str(i)} for i in range(10)]
    ranked = rank_candidates(target, candidates, limit=3)
    assert len(ranked) == 3


def test_rank_candidates_invalid_limit_raises():
    with pytest.raises(ScorerError):
        rank_candidates({}, [], limit=0)


def test_rank_candidates_empty_candidates():
    ranked = rank_candidates({"a": "1"}, [])
    assert ranked == []
