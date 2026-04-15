"""csvdiff — fast CSV diffing library."""

from csvdiff.differ import (
    CSVDiffError,
    DiffResult,
    FieldChange,
    RowChange,
    compute_diff,
)
from csvdiff.limiter import LimitError, LimitOptions, LimitResult, limit_diff
from csvdiff.parser import CSVParseError, index_rows, read_csv

__all__ = [
    # parser
    "CSVParseError",
    "read_csv",
    "index_rows",
    # differ
    "CSVDiffError",
    "FieldChange",
    "RowChange",
    "DiffResult",
    "compute_diff",
    # limiter
    "LimitError",
    "LimitOptions",
    "LimitResult",
    "limit_diff",
]
