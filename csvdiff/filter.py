"""Filter and column-selection utilities for csvdiff."""

from typing import Dict, List, Optional, Set
from csvdiff.differ import DiffResult, RowChange


class FilterError(Exception):
    """Raised when a filter operation fails."""
    pass


def filter_columns(rows: List[Dict[str, str]], columns: List[str]) -> List[Dict[str, str]]:
    """Return rows with only the specified columns retained.

    Args:
        rows: List of row dicts.
        columns: Column names to keep.

    Raises:
        FilterError: If any requested column is not present in the rows.
    """
    if not rows:
        return []

    available = set(rows[0].keys())
    missing = set(columns) - available
    if missing:
        raise FilterError(
            f"Column(s) not found in data: {', '.join(sorted(missing))}"
        )

    return [{col: row[col] for col in columns} for row in rows]


def filter_diff_by_columns(
    result: DiffResult,
    columns: Optional[List[str]],
) -> DiffResult:
    """Return a new DiffResult with row data restricted to *columns*.

    If *columns* is None or empty the original result is returned unchanged.
    Only the row snapshots inside RowChange objects are filtered; key columns
    are always preserved so callers can still identify rows.
    """
    if not columns:
        return result

    col_set: Set[str] = set(columns)

    def _trim(row: Dict[str, str]) -> Dict[str, str]:
        return {k: v for k, v in row.items() if k in col_set}

    filtered_added = [_trim(r) for r in result["added"]]
    filtered_removed = [_trim(r) for r in result["removed"]]
    filtered_changed: List[RowChange] = [
        RowChange(key=rc.key, old=_trim(rc.old), new=_trim(rc.new))
        for rc in result["changed"]
    ]

    return DiffResult(added=filtered_added, removed=filtered_removed, changed=filtered_changed)


def exclude_columns(
    rows: List[Dict[str, str]], exclude: List[str]
) -> List[Dict[str, str]]:
    """Return rows with the specified columns removed."""
    if not rows or not exclude:
        return rows
    excl_set = set(exclude)
    return [{k: v for k, v in row.items() if k not in excl_set} for row in rows]
