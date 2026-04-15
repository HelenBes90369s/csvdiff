"""Row similarity scoring used by the matcher."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple


class ScorerError(Exception):
    """Raised when scorer inputs are invalid."""


@dataclass(frozen=True)
class SimilarityScore:
    """Similarity between two rows."""

    score: float   # 0.0 – 1.0
    matched: int   # number of matching field values
    total: int     # total fields compared

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ScorerError(
                f"score must be between 0.0 and 1.0, got {self.score!r}"
            )
        if self.total < 0:
            raise ScorerError(f"total must be >= 0, got {self.total!r}")


def score_rows(
    row_a: Dict[str, str],
    row_b: Dict[str, str],
) -> SimilarityScore:
    """Compute a simple field-equality similarity score between two rows."""
    all_keys = set(row_a) | set(row_b)
    if not all_keys:
        return SimilarityScore(score=1.0, matched=0, total=0)
    matched = sum(
        1
        for k in all_keys
        if row_a.get(k) == row_b.get(k)
    )
    total = len(all_keys)
    return SimilarityScore(
        score=round(matched / total, 6),
        matched=matched,
        total=total,
    )


def rank_candidates(
    row: Dict[str, str],
    candidates: Sequence[Dict[str, str]],
    *,
    limit: int = 5,
) -> List[Tuple[SimilarityScore, int]]:
    """Return the top *limit* candidates ranked by similarity to *row*.

    Returns a list of ``(SimilarityScore, original_index)`` tuples sorted
    by descending score.
    """
    if limit < 1:
        raise ScorerError(f"limit must be >= 1, got {limit!r}")
    scored = [
        (score_rows(row, candidate), idx)
        for idx, candidate in enumerate(candidates)
    ]
    scored.sort(key=lambda t: t[0].score, reverse=True)
    return scored[:limit]
