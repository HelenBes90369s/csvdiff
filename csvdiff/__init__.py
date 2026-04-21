"""csvdiff — fast CSV diffing library."""
from csvdiff.differ import (
    CSVDiffError,
    DiffResult,
    FieldChange,
    RowChange,
    compute_diff,
)
from csvdiff.parser import CSVParseError, index_rows, read_csv
from csvdiff.formatter import format_diff
from csvdiff.filter import filter_columns, exclude_columns
from csvdiff.summary import summarize, format_summary
from csvdiff.stats import compute_stats
from csvdiff.exporter import export_diff
from csvdiff.validator import validate_diff, assert_valid
from csvdiff.reporter import build_report, format_report
from csvdiff.encoder import encode_diff, decode_diff
from csvdiff.differ_tracer import trace_pipeline, TracerOptions, TraceResult

__all__ = [
    # core
    "CSVDiffError",
    "CSVParseError",
    "DiffResult",
    "FieldChange",
    "RowChange",
    "compute_diff",
    "read_csv",
    "index_rows",
    # formatting
    "format_diff",
    "format_report",
    "format_summary",
    # pipeline helpers
    "filter_columns",
    "exclude_columns",
    "summarize",
    "compute_stats",
    "export_diff",
    "validate_diff",
    "assert_valid",
    "build_report",
    "encode_diff",
    "decode_diff",
    # tracer
    "trace_pipeline",
    "TracerOptions",
    "TraceResult",
]
