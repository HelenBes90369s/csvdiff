"""Fuzzy row matching: find the closest counterpart for added/removed rows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from csvdiff.differ import DiffResult, RowChange
from csvdiff.scorer import SimilarityScore, score_rows, rank_candidates


class MatchError(Exception):
    """Raised when matching configuration is invalid."""


@dataclass(frozen=True)
class MatchedPair:
    """An added row paired with its closest removed-row counterpart."""

    added_key: Tuple[str, ...]
    removed_key: Tuple[str, ...]
    score: SimilarityScore


def match_orphans(
    result: DiffResult,
    *,
    threshold: float = 0.5,
    max_candidates: int = 5,
) -> List[MatchedPair]:
    """Return fuzzy matches between added and removed rows.
 every added row, the *removed* rows are ranked by similarity and the
    best candidate is returned if its score meets *threshold*.

    Args:
        result:         The diff result to inspect.
        threshold:      Minimum similarity score (0.0–1.0) to accept a match.
        max_candidates: How many removed rows to consider per added row.

    Returns:
        A list of :class:`MatchedPair` instances, one per matched added row.
    """
    if not 0.0 <= threshold <= 1.0:
        raise MatchError(f"threshold must be between 0.0 and 1.0, got {threshold!r}")
    if max_candidates < 1:
        raise MatchError(f"max_candidates must be >= 1, got {max_candidates!r}")

    added: Dict[Tuple[str, ...], Dict[str, str]] = {
        change.key: change.new_row
        for change in result.added
    }
    removed: Dict[Tuple[str, ...], Dict[str, str]] = {
        change.key: change.old_row
        for change in result.removed
    }

    if not added or not removed:
        return []

    removed_rows = list(removed.values())
    removed_keys = list(removed.keys())

    pairs: List[MatchedPair] = []
    for a_key, a_row in added.items():
        ranked = rank_candidates(
            a_row,
            removed_rows,
            limit=max_candidates,
        )
        if not ranked:
            continue
        best_score, best_idx = ranked[0]
        if best_score.score >= threshold:
            pairs.append(
                MatchedPair(
                    added_key=a_key,
                    removed_key=removed_keys[best_idx],
                    score=best_score,
                )
            )
    return pairs
