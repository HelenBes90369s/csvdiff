"""csvdiff – public re-exports."""
from csvdiff.differ import DiffResult, RowChange, FieldChange, DiffResult  # noqa: F811
from csvdiff.parser import read_csv, index_rows
from csvdiff.formatter import format_diff
from csvdiff.differ_metrics import (
    MetricsOptions,
    DiffMetrics,
    collect_metrics,
)

__all__ = [
    "DiffResult",
    "RowChange",
    "FieldChange",
    "read_csv",
    "index_rows",
    "format_diff",
    "MetricsOptions",
    "DiffMetrics",
    "collect_metrics",
]
