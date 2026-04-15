"""csvdiff – public API."""

from csvdiff.parser import read_csv, index_rows, CSVParseError
from csvdiff.differ import (
    DiffResult,
    RowChange,
    FieldChange,
    diff_results,
    compute_diff,
)
from csvdiff.formatter import format_diff
from csvdiff.summary import summarize, DiffSummary
from csvdiff.filter import filter_diff_by_columns, exclude_columns
from csvdiff.sorter import sort_diff, sort_keys
from csvdiff.merger import merge_diff
from csvdiff.stats import compute_stats, DiffStats
from csvdiff.exporter import export_diff
from csvdiff.validator import validate_diff, ValidationResult
from csvdiff.reporter import build_report, DiffReport
from csvdiff.highlighter import highlight_diff
from csvdiff.truncator import truncate_diff
from csvdiff.sampler import sample_diff
from csvdiff.annotator import annotate_diff
from csvdiff.scorer import score_rows, rank_candidates
from csvdiff.matcher import match_orphans, MatchedPair
from csvdiff.normalizer import normalize_row
from csvdiff.grouper import group_diff
from csvdiff.limiter import limit_diff

__all__ = [
    "read_csv", "index_rows", "CSVParseError",
    "DiffResult", "RowChange", "FieldChange", "diff_results", "compute_diff",
    "format_diff",
    "summarize", "DiffSummary",
    "filter_diff_by_columns", "exclude_columns",
    "sort_diff", "sort_keys",
    "merge_diff",
    "compute_stats", "DiffStats",
    "export_diff",
    "validate_diff", "ValidationResult",
    "build_report", "DiffReport",
    "highlight_diff",
    "truncate_diff",
    "sample_diff",
    "annotate_diff",
    "score_rows", "rank_candidates",
    "match_orphans", "MatchedPair",
    "normalize_row",
    "group_diff",
    "limit_diff",
]
