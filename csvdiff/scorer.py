"""Similarity scoring for CSV diff rows.

Provides a numeric similarity score (0.0–1.0) between two CSV rows,
useful for fuzzy matching and ranking potential row moves.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


class ScorerError(Exception):
    """Raised when scoring cannot be performed."""


@dataclass(frozen=True)
class SimilarityScore:
    """Result of comparing two rows."""

    score: float          # 0.0 (no match) to 1.0 (identical)
    matched_fields: int
    total_fields: int
    key: Optional[str] = None  # optional label for the row pair

    def __post_init__(self) -> None:
        if not (0.0 <= self.score <= 1.0):
            raise ScorerError(f"score must be in [0, 1], got {self.score}")
        if self.total_fields < 0:
            raise ScorerError("total_fields must be >= 0")


def score_rows(
    row_a: Dict[str, str],
    row_b: Dict[str, str],
    fields: Optional[List[str]] = None,
) -> SimilarityScore:
    """Return a SimilarityScore comparing *row_a* to *row_b*.

    Args:
        row_a: First row as a field→value mapping.
        row_b: Second row as a field→value mapping.
        fields: Explicit list of fields to compare.  When *None* the union
                of both rows' keys is used.

    Returns:
        A :class:`SimilarityScore` instance.
    """
    if fields is None:
        fields = sorted(set(row_a) | set(row_b))

    if not fields:
        return SimilarityScore(score=1.0, matched_fields=0, total_fields=0)

    matched = sum(
        1 for f in fields if row_a.get(f, "") == row_b.get(f, "")
    )
    return SimilarityScore(
        score=matched / len(fields),
        matched_fields=matched,
        total_fields=len(fields),
    )


def rank_candidates(
    target: Dict[str, str],
    candidates: List[Dict[str, str]],
    fields: Optional[List[str]] = None,
    threshold: float = 0.0,
) -> List[SimilarityScore]:
    """Score *target* against each candidate and return sorted results.

    Results are sorted descending by score.  Candidates whose score is
    strictly below *threshold* are excluded.
    """
    if not (0.0 <= threshold <= 1.0):
        raise ScorerError(f"threshold must be in [0, 1], got {threshold}")

    scores = [
        score_rows(target, candidate, fields)
        for candidate in candidates
    ]
    return sorted(
        (s for s in scores if s.score >= threshold),
        key=lambda s: s.score,
        reverse=True,
    )
