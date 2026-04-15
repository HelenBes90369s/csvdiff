"""csvdiff — public API re-exports."""

from csvdiff.parser import CSVParseError, read_csv, index_rows
from csvdiff.differ import (
    CSVDiffError,
    FieldChange,
    RowChange,
    DiffResult,
    changed_fields,
)
from csvdiff.formatter import format_diff
from csvdiff.summary import DiffSummary, summarize, format_summary
from csvdiff.filter import FilterError, filter_columns, filter_diff_by_columns, exclude_columns
from csvdiff.pager import DiffPage, paginate_diff, page_to_diff_result
from csvdiff.sorter import SortError, sort_diff, sort_keys
from csvdiff.merger import MergeError, merge_diff
from csvdiff.stats import DiffStats, compute_stats
from csvdiff.exporter import ExportError, export_diff
from csvdiff.validator import ValidationError, ValidationResult, validate_diff, assert_valid
from csvdiff.reporter import DiffReport, build_report, format_report
from csvdiff.highlighter import HighlightError, HighlightedField, highlight_diff
from csvdiff.truncator import TruncateError, TruncateOptions, TruncateResult
from csvdiff.sampler import SampleError, SampleOptions, sample_diff
from csvdiff.annotator import AnnotationError, AnnotatedRow
from csvdiff.scorer import ScorerError, SimilarityScore, score_rows, rank_candidates
from csvdiff.normalizer import NormalizeError, NormalizeOptions, normalize_row
from csvdiff.grouper import GroupError, DiffGroup
from csvdiff.limiter import LimitError, LimitOptions, LimitResult
from csvdiff.matcher import MatchError, MatchedPair, match_orphans
from csvdiff.deduplicator import DeduplicateError, DeduplicateOptions, deduplicate_diff
from csvdiff.classifier import (
    ClassifyError,
    ClassifyOptions,
    ClassifiedChange,
    classify_diff,
    severity_counts,
)

__all__ = [
    "CSVParseError", "read_csv", "index_rows",
    "CSVDiffError", "FieldChange", "RowChange", "DiffResult", "changed_fields",
    "format_diff",
    "DiffSummary", "summarize", "format_summary",
    "FilterError", "filter_columns", "filter_diff_by_columns", "exclude_columns",
    "DiffPage", "paginate_diff", "page_to_diff_result",
    "SortError", "sort_diff", "sort_keys",
    "MergeError", "merge_diff",
    "DiffStats", "compute_stats",
    "ExportError", "export_diff",
    "ValidationError", "ValidationResult", "validate_diff", "assert_valid",
    "DiffReport", "build_report", "format_report",
    "HighlightError", "HighlightedField", "highlight_diff",
    "TruncateError", "TruncateOptions", "TruncateResult",
    "SampleError", "SampleOptions", "sample_diff",
    "AnnotationError", "AnnotatedRow",
    "ScorerError", "SimilarityScore", "score_rows", "rank_candidates",
    "NormalizeError", "NormalizeOptions", "normalize_row",
    "GroupError", "DiffGroup",
    "LimitError", "LimitOptions", "LimitResult",
    "MatchError", "MatchedPair", "match_orphans",
    "DeduplicateError", "DeduplicateOptions", "deduplicate_diff",
    "ClassifyError", "ClassifyOptions", "ClassifiedChange", "classify_diff", "severity_counts",
]
