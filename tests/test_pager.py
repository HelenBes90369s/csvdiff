"""Tests for csvdiff.pager pagination utilities."""

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.pager import DiffPage, paginate_diff, page_to_diff_result


def make_result(
    added=None, removed=None, changed=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


def make_change(key="k") -> RowChange:
    return RowChange(
        key=key,
        before={"id": key, "val": "old"},
        after={"id": key, "val": "new"},
    )


def test_paginate_empty_result_yields_one_empty_page():
    result = make_result()
    pages = list(paginate_diff(result, page_size=10))
    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert pages[0].total_pages == 1
    assert pages[0].added == []
    assert pages[0].removed == []
    assert pages[0].changed == []


def test_paginate_single_page():
    result = make_result(
        added=[{"id": "1"}, {"id": "2"}],
        removed=[{"id": "3"}],
    )
    pages = list(paginate_diff(result, page_size=10))
    assert len(pages) == 1
    assert pages[0].total_pages == 1
    assert pages[0].is_last is True
    assert len(pages[0].added) == 2
    assert len(pages[0].removed) == 1


def test_paginate_multiple_pages():
    added = [{"id": str(i)} for i in range(6)]
    result = make_result(added=added)
    pages = list(paginate_diff(result, page_size=4))
    assert len(pages) == 2
    assert pages[0].page_number == 1
    assert pages[0].total_pages == 2
    assert pages[0].is_last is False
    assert len(pages[0].added) == 4
    assert pages[1].page_number == 2
    assert pages[1].is_last is True
    assert len(pages[1].added) == 2


def test_paginate_mixed_types_across_pages():
    result = make_result(
        added=[{"id": "a"}],
        removed=[{"id": "b"}],
        changed=[make_change("c"), make_change("d")],
    )
    pages = list(paginate_diff(result, page_size=2))
    assert len(pages) == 2
    total_added = sum(len(p.added) for p in pages)
    total_removed = sum(len(p.removed) for p in pages)
    total_changed = sum(len(p.changed) for p in pages)
    assert total_added == 1
    assert total_removed == 1
    assert total_changed == 2


def test_paginate_invalid_page_size_raises():
    result = make_result()
    with pytest.raises(ValueError, match="page_size must be >= 1"):
        list(paginate_diff(result, page_size=0))


def test_page_to_diff_result_roundtrip():
    original = make_result(
        added=[{"id": "1"}],
        removed=[{"id": "2"}],
        changed=[make_change("3")],
    )
    pages = list(paginate_diff(original, page_size=100))
    assert len(pages) == 1
    restored = page_to_diff_result(pages[0])
    assert restored.added == original.added
    assert restored.removed == original.removed
    assert restored.changed == original.changed
