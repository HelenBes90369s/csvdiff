"""csvdiff — public API."""
from csvdiff.parser import CSVParseError, read_csv, index_rows
from csvdiff.differ import (
    CSVDiffError,
    FieldChange,
    RowChange,
    DiffResult,
    diff_results,
)
from csvdiff.formatter import format_diff
from csvdiff.filter import FilterError, filter_columns, filter_diff_by_columns, exclude_columns
from csvdiff.summary import DiffSummary, summarize, format_summary
from csvdiff.pager import DiffPage, paginate_diff, page_to_diff_result
from csvdiff.sorter import SortError, sort_diff, sort_keys
from csvdiff.merger import MergeError, merge_diff
from csvdiff.stats import DiffStats, compute_stats
from csvdiff.exporter import ExportError, export_diff
from csvdiff.validator import ValidationError, ValidationRule, validate_diff, assert_valid
from csvdiff.reporter import DiffReport, build_report, format_report
from csvdiff.highlighter import HighlightError, HighlightedField, highlight_diff
from csvdiff.truncator import TruncateError, TruncateOptions, TruncateResult, truncate_diff
from csvdiff.sampler import SampleError, SampleOptions, sample_diff
from csvdiff.annotator import AnnotationError, Annotation, AnnotatedRow, annotate_diff
from csvdiff.scorer import ScorerError, SimilarityScore, score_rows, rank_candidates
from csvdiff.normalizer import NormalizeError, NormalizeOptions, normalize_row, normalize_diff
from csvdiff.grouper import GroupError, DiffGroup, group_by_kind, group_by_field
from csvdiff.limiter import LimitError, LimitOptions, LimitResult, limit_diff
from csvdiff.matcher import MatchError, MatchedPair, match_orphans
from csvdiff.deduplicator import DeduplicateError, DeduplicateOptions, deduplicate_diff
from csvdiff.classifier import ClassifyError, ClassifyOptions, ClassifiedChange, classify_diff
from csvdiff.pivotter import PivotError, FieldPivot, pivot_diff
from csvdiff.ranker import RankError, RankOptions, rank_diff, top_n

__all__ = [
    # parser
    "CSVParseError", "read_csv", "index_rows",
    # differ
    "CSVDiffError", "FieldChange", "RowChange", "DiffResult", "diff_results",
    # formatter
    "format_diff",
    # filter
    "FilterError", "filter_columns", "filter_diff_by_columns", "exclude_columns",
    # summary
    "DiffSummary", "summarize", "format_summary",
    # pager
    "DiffPage", "paginate_diff", "page_to_diff_result",
    # sorter
    "SortError", "sort_diff", "sort_keys",
    # merger
    "MergeError", "merge_diff",
    # stats
    "DiffStats", "compute_stats",
    # exporter
    "ExportError", "export_diff",
    # validator
    "ValidationError", "ValidationRule", "validate_diff", "assert_valid",
    # reporter
    "DiffReport", "build_report", "format_report",
    # highlighter
    "HighlightError", "HighlightedField", "highlight_diff",
    # truncator
    "TruncateError", "TruncateOptions", "TruncateResult", "truncate_diff",
    # sampler
    "SampleError", "SampleOptions", "sample_diff",
    # annotator
    "AnnotationError", "Annotation", "AnnotatedRow", "annotate_diff",
    # scorer
    "ScorerError", "SimilarityScore", "score_rows", "rank_candidates",
    # normalizer
    "NormalizeError", "NormalizeOptions", "normalize_row", "normalize_diff",
    # grouper
    "GroupError", "DiffGroup", "group_by_kind", "group_by_field",
    # limiter
    "LimitError", "LimitOptions", "LimitResult", "limit_diff",
    # matcher
    "MatchError", "MatchedPair", "match_orphans",
    # deduplicator
    "DeduplicateError", "DeduplicateOptions", "deduplicate_diff",
    # classifier
    "ClassifyError", "ClassifyOptions", "ClassifiedChange", "classify_diff",
    # pivotter
    "PivotError", "FieldPivot", "pivot_diff",
    # ranker
    "RankError", "RankOptions", "rank_diff", "top_n",
]
