"""Pagination support for large diff outputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Iterator

from csvdiff.differ import DiffResult, RowChange


@dataclass
class DiffPage:
    """A single page of diff results."""
    added: List[dict] = field(default_factory=list)
    removed: List[dict] = field(default_factory=list)
    changed: List[RowChange] = field(default_factory=list)
    page_number: int = 1
    total_pages: int = 1

    @property
    def is_last(self) -> bool:
        return self.page_number >= self.total_pages


def paginate_diff(result: DiffResult, page_size: int = 50) -> Iterator[DiffPage]:
    """Yield pages of DiffResult entries, each containing at most page_size total rows."""
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size}")

    all_items: list = (
        [("added", r) for r in result.added]
        + [("removed", r) for r in result.removed]
        + [("changed", r) for r in result.changed]
    )

    total_items = len(all_items)
    if total_items == 0:
        yield DiffPage(page_number=1, total_pages=1)
        return

    total_pages = (total_items + page_size - 1) // page_size

    for page_num, start in enumerate(range(0, total_items, page_size), start=1):
        chunk = all_items[start : start + page_size]
        page = DiffPage(page_number=page_num, total_pages=total_pages)
        for kind, row in chunk:
            if kind == "added":
                page.added.append(row)
            elif kind == "removed":
                page.removed.append(row)
            else:
                page.changed.append(row)
        yield page


def page_to_diff_result(page: DiffPage) -> DiffResult:
    """Convert a DiffPage back into a DiffResult for formatting."""
    return DiffResult(
        added=page.added,
        removed=page.removed,
        changed=page.changed,
    )
