"""csvdiff public API."""
from csvdiff.parser import CSVParseError, read_csv, index_rows
from csvdiff.differ import (
    CSVDiffError,
    FieldChange,
    RowChange,
    DiffResult,
    diff_csv,
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
from csvdiff.truncator import TruncateError, TruncateOptions, truncate_diff
from csvdiff.sampler import SampleError, SampleOptions, sample_diff
from csvdiff.annotator import AnnotationError, Annotation, AnnotatedRow, annotate_diff
from csvdiff.scorer import ScorerError, SimilarityScore, score_rows, rank_candidates
from csvdiff.normalizer import NormalizeError, NormalizeOptions, normalize_diff
from csvdiff.grouper import GroupError, DiffGroup, group_diff
from csvdiff.limiter import LimitError, LimitOptions, limit_diff
from csvdiff.matcher import MatchError, MatchedPair, match_orphans
from csvdiff.deduplicator import DeduplicateError, DeduplicateOptions, deduplicate_diff
from csvdiff.classifier import ClassifyError, ClassifyOptions, ClassifiedChange, classify_diff
from csvdiff.pivotter import PivotError, FieldPivot, pivot_diff
from csvdiff.ranker import RankError, RankOptions, rank_diff
from csvdiff.flattener import FlattenError, FlatRow, flatten_diff
from csvdiff.splitter import SplitError, SplitOptions, split_diff
from csvdiff.partitioner import PartitionError, PartitionOptions, PartitionResult, partition_diff
from csvdiff.aggregator import AggregateError, FieldAggregate, aggregate_diff
from csvdiff.transformer import TransformError, TransformOptions, transform_diff
from csvdiff.redactor import RedactError, RedactOptions, redact_diff
from csvdiff.comparer import CompareError, CompareResult, compare_diffs
from csvdiff.indexer import IndexError, DiffIndex, build_index
from csvdiff.differ_patch import PatchError, Patch, build_patch, apply_patch
from csvdiff.resolver import ResolveError, ResolveOptions, resolve_diff
from csvdiff.renamer import RenameError, RenameOptions, rename_diff

__all__ = [
    "CSVParseError", "read_csv", "index_rows",
    "CSVDiffError", "FieldChange", "RowChange", "DiffResult", "diff_csv",
    "format_diff",
    "FilterError", "filter_columns", "filter_diff_by_columns", "exclude_columns",
    "DiffSummary", "summarize", "format_summary",
    "DiffPage", "paginate_diff", "page_to_diff_result",
    "SortError", "sort_diff", "sort_keys",
    "MergeError", "merge_diff",
    "DiffStats", "compute_stats",
    "ExportError", "export_diff",
    "ValidationError", "ValidationRule", "validate_diff", "assert_valid",
    "DiffReport", "build_report", "format_report",
    "HighlightError", "HighlightedField", "highlight_diff",
    "TruncateError", "TruncateOptions", "truncate_diff",
    "SampleError", "SampleOptions", "sample_diff",
    "AnnotationError", "Annotation", "AnnotatedRow", "annotate_diff",
    "ScorerError", "SimilarityScore", "score_rows", "rank_candidates",
    "NormalizeError", "NormalizeOptions", "normalize_diff",
    "GroupError", "DiffGroup", "group_diff",
    "LimitError", "LimitOptions", "limit_diff",
    "MatchError", "MatchedPair", "match_orphans",
    "DeduplicateError", "DeduplicateOptions", "deduplicate_diff",
    "ClassifyError", "ClassifyOptions", "ClassifiedChange", "classify_diff",
    "PivotError", "FieldPivot", "pivot_diff",
    "RankError", "RankOptions", "rank_diff",
    "FlattenError", "FlatRow", "flatten_diff",
    "SplitError", "SplitOptions", "split_diff",
    "PartitionError", "PartitionOptions", "PartitionResult", "partition_diff",
    "AggregateError", "FieldAggregate", "aggregate_diff",
    "TransformError", "TransformOptions", "transform_diff",
    "RedactError", "RedactOptions", "redact_diff",
    "CompareError", "CompareResult", "compare_diffs",
    "IndexError", "DiffIndex", "build_index",
    "PatchError", "Patch", "build_patch", "apply_patch",
    "ResolveError", "ResolveOptions", "resolve_diff",
    "RenameError", "RenameOptions", "rename_diff",
]
