"""Tests for csvdiff.matcher."""

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.matcher import MatchError, MatchedPair, match_orphans


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _change(
    key: tuple,
    old: dict | None = None,
    new: dict | None = None,
    field_changes=None,
) -> RowChange:
    return RowChange(
        key=key,
        old_row=old or {},
        new_row=new or {},
        field_changes=field_changes or [],
    )


def make_result(
    added=None, removed=None, changed=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


# ---------------------------------------------------------------------------
# match_orphans
# ---------------------------------------------------------------------------

def test_match_orphans_empty_result_returns_empty():
    result = make_result()
    assert match_orphans(result) == []


def test_match_orphans_no_removed_returns_empty():
    result = make_result(
        added=[_change(("1",), new={"name": "Alice"})]
    )
    assert match_orphans(result) == []


def test_match_orphans_no_added_returns_empty():
    result = make_result(
        removed=[_change(("1",), old={"name": "Alice"})]
    )
    assert match_orphans(result) == []


def test_match_orphans_perfect_match():
    row = {"name": "Alice", "age": "30"}
    result = make_result(
        added=[_change(("A",), new=row)],
        removed=[_change(("B",), old=row)],
    )
    pairs = match_orphans(result, threshold=0.9)
    assert len(pairs) == 1
    assert pairs[0].added_key == ("A",)
    assert pairs[0].removed_key == ("B",)
    assert pairs[0].score.score == pytest.approx(1.0)


def test_match_orphans_below_threshold_excluded():
    result = make_result(
        added=[_change(("A",), new={"name": "Alice", "city": "NY"})],
        removed=[_change(("B",), old={"name": "Bob",  "city": "LA"})],
    )
    # No fields match → score 0.0 < threshold 0.5
    pairs = match_orphans(result, threshold=0.5)
    assert pairs == []


def test_match_orphans_picks_best_candidate():
    target = {"name": "Alice", "age": "30", "city": "NY"}
    close  = {"name": "Alice", "age": "30", "city": "LA"}  # 2/3
    far    = {"name": "Bob",   "age": "99", "city": "LA"}  # 0/3
    result = make_result(
        added=[_change(("A",), new=target)],
        removed=[
            _change(("B",), old=far),
            _change(("C",), old=close),
        ],
    )
    pairs = match_orphans(result, threshold=0.5)
    assert len(pairs) == 1
    assert pairs[0].removed_key == ("C",)


def test_match_orphans_invalid_threshold_raises():
    with pytest.raises(MatchError):
        match_orphans(make_result(), threshold=1.5)


def test_match_orphans_invalid_max_candidates_raises():
    with pytest.raises(MatchError):
        match_orphans(make_result(), max_candidates=0)
