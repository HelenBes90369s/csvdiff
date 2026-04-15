"""csvdiff – public API."""

from csvdiff.parser import CSVParseError, read_csv, index_rows
from csvdiff.differ import (
    CSVDiffError,
    FieldChange,
    RowChange,
    DiffResult,
    changed_fields,
)
from csvdiff.formatter import format_diff
from csvdiff.filter import FilterError, filter_columns, filter_diff_by_columns, exclude_columns
from csvdiff.summary import DiffSummary, summarize, format_summary
from csvdiff.pager import DiffPage, paginate_diff, page_to_diff_result
from csvdiff.sorter import SortError, sort_diff, sort_keys
from csvdiff.merger import MergeError, merge_diff
from csvdiff.stats import DiffStats, compute_stats
from csvdiff.exporter import ExportError, export_diff
from csvdiff.validator import ValidationError, ValidationRule, ValidationResult, validate_diff, assert_valid
from csvdiff.reporter import DiffReport, build_report, format_report
from csvdiff.highlighter import HighlightError, HighlightedField, highlight_diff
from csvdiff.truncator import TruncateError, TruncateOptions, TruncateResult
from csvdiff.sampler import SampleError, SampleOptions, sample_diff
from csvdiff.annotator import AnnotationError, Annotation, AnnotatedRow
from csvdiff.scorer import ScorerError, SimilarityScore, score_rows, rank_candidates
from csvdiff.normalizer import NormalizeError, NormalizeOptions, normalize_row
from csvdiff.grouper import GroupError, DiffGroup
from csvdiff.limiter import LimitError, LimitOptions, LimitResult
from csvdiff.matcher import MatchError, MatchedPair, match_orphans
from csvdiff.deduplicator import DeduplicateError, DeduplicateOptions, deduplicate_diff
from csvdiff.classifier import ClassifyError, ClassifyOptions, ClassifiedChange
from csvdiff.pivotter import PivotError, FieldPivot
from csvdiff.ranker import RankError, RankOptions
from csvdiff.flattener import FlattenError, FlatRow, flatten_diff
from csvdiff.splitter import SplitError, SplitOptions
from csvdiff.partitioner import PartitionError, PartitionOptions, PartitionResult
from csvdiff.aggregator import AggregateError, FieldAggregate, aggregate_diff
from csvdiff.transformer import TransformError, TransformOptions, transform_diff
from csvdiff.redactor import RedactError, RedactOptions, redact_diff

__all__ = [
    # parser
    "CSVParseError", "read_csv", "index_rows",
    # differ
    "CSVDiffError", "FieldChange", "RowChange", "DiffResult", "changed_fields",
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
    "ValidationError", "ValidationRule", "ValidationResult", "validate_diff", "assert_valid",
    # reporter
    "DiffReport", "build_report", "format_report",
    # highlighter
    "HighlightError", "HighlightedField", "highlight_diff",
    # truncator
    "TruncateError", "TruncateOptions", "TruncateResult",
    # sampler
    "SampleError", "SampleOptions", "sample_diff",
    # annotator
    "AnnotationError", "Annotation", "AnnotatedRow",
    # scorer
    "ScorerError", "SimilarityScore", "score_rows", "rank_candidates",
    # normalizer
    "NormalizeError", "NormalizeOptions", "normalize_row",
    # grouper
    "GroupError", "DiffGroup",
    # limiter
    "LimitError", "LimitOptions", "LimitResult",
    # matcher
    "MatchError", "MatchedPair", "match_orphans",
    # deduplicator
    "DeduplicateError", "DeduplicateOptions", "deduplicate_diff",
    # classifier
    "ClassifyError", "ClassifyOptions", "ClassifiedChange",
    # pivotter
    "PivotError", "FieldPivot",
    # ranker
    "RankError", "RankOptions",
    # flattener
    "FlattenError", "FlatRow", "flatten_diff",
    # splitter
    "SplitError", "SplitOptions",
    # partitioner
    "PartitionError", "PartitionOptions", "PartitionResult",
    # aggregator
    "AggregateError", "FieldAggregate", "aggregate_diff",
    # transformer
    "TransformError", "TransformOptions", "transform_diff",
    # redactor
    "RedactError", "RedactOptions", "redact_diff",
]
