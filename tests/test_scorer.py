"""Tests for csvdiff.scorer."""

import pytest

from csvdiff.scorer import (
    ScorerError,
    SimilarityScore,
    rank_candidates,
    score_rows,
)


# ---------------------------------------------------------------------------
# SimilarityScore construction
# ---------------------------------------------------------------------------

def test_similarity_score_valid() -> None:
    s = SimilarityScore(score=0.75, matched_fields=3, total_fields=4)
    assert s.score == 0.75


def test_similarity_score_invalid_score_raises() -> None:
    with pytest.raises(ScorerError, match="score must be in"):
        SimilarityScore(score=1.5, matched_fields=1, total_fields=1)


def test_similarity_score_negative_total_raises() -> None:
    with pytest.raises(ScorerError, match="total_fields"):
        SimilarityScore(score=0.0, matched_fields=0, total_fields=-1)


# ---------------------------------------------------------------------------
# score_rows
# ---------------------------------------------------------------------------

def test_score_rows_identical() -> None:
    row = {"a": "1", "b": "2", "c": "3"}
    result = score_rows(row, row.copy())
    assert result.score == 1.0
    assert result.matched_fields == 3
    assert result.total_fields == 3


def test_score_rows_no_match() -> None:
    a = {"x": "1", "y": "2"}
    b = {"x": "9", "y": "8"}
    result = score_rows(a, b)
    assert result.score == 0.0
    assert result.matched_fields == 0


def test_score_rows_partial_match() -> None:
    a = {"name": "Alice", "age": "30", "city": "NYC"}
    b = {"name": "Alice", "age": "31", "city": "NYC"}
    result = score_rows(a, b)
    assert result.score == pytest.approx(2 / 3)
    assert result.matched_fields == 2


def test_score_rows_explicit_fields_subset() -> None:
    a = {"name": "Alice", "age": "30", "city": "NYC"}
    b = {"name": "Alice", "age": "99", "city": "LA"}
    # Only compare 'name' — should be 1.0
    result = score_rows(a, b, fields=["name"])
    assert result.score == 1.0
    assert result.total_fields == 1


def test_score_rows_empty_rows_returns_perfect() -> None:
    result = score_rows({}, {})
    assert result.score == 1.0
    assert result.total_fields == 0


def test_score_rows_missing_key_treated_as_empty_string() -> None:
    a = {"a": ""}
    b = {}  # 'a' missing → treated as ""
    result = score_rows(a, b, fields=["a"])
    assert result.score == 1.0


# ---------------------------------------------------------------------------
# rank_candidates
# ---------------------------------------------------------------------------

def test_rank_candidates_sorted_descending() -> None:
    target = {"name": "Alice", "score": "100"}
    candidates = [
        {"name": "Bob", "score": "50"},    # 0/2
        {"name": "Alice", "score": "99"},  # 1/2
        {"name": "Alice", "score": "100"}, # 2/2
    ]
    results = rank_candidates(target, candidates)
    assert len(results) == 3
    assert results[0].score == 1.0
    assert results[1].score == pytest.approx(0.5)
    assert results[2].score == 0.0


def test_rank_candidates_threshold_filters() -> None:
    target = {"a": "1", "b": "2"}
    candidates = [
        {"a": "1", "b": "9"},  # 0.5
        {"a": "9", "b": "9"},  # 0.0
    ]
    results = rank_candidates(target, candidates, threshold=0.5)
    assert len(results) == 1
    assert results[0].score == pytest.approx(0.5)


def test_rank_candidates_invalid_threshold_raises() -> None:
    with pytest.raises(ScorerError, match="threshold"):
        rank_candidates({}, [], threshold=1.5)


def test_rank_candidates_empty_candidates() -> None:
    results = rank_candidates({"a": "1"}, [])
    assert results == []
