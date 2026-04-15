"""csvdiff – public API.

This file re-exports the most commonly used symbols so users can write::

    from csvdiff import read_csv, diff_csv, format_diff
"""
from .parser import CSVParseError, read_csv, index_rows
from .differ import (
    CSVDiffError,
    FieldChange,
    RowChange,
    DiffResult,
    changed_fields,
)
from .formatter import format_diff
from .filter import FilterError, filter_columns, filter_diff_by_columns, exclude_columns
from .summary import DiffSummary, summarize, format_summary
from .sorter import SortError, sort_diff, sort_keys
from .merger import MergeError, merge_diff
from .stats import DiffStats, compute_stats
from .exporter import ExportError, export_diff
from .validator import ValidationError, ValidationRule, validate_diff, assert_valid
from .reporter import DiffReport, build_report, format_report
from .highlighter import HighlightError, HighlightedField, highlight_diff
from .truncator import TruncateError, TruncateOptions, TruncateResult
from .sampler import SampleError, SampleOptions, sample_diff
from .annotator import AnnotationError, Annotation, AnnotatedRow
from .scorer import ScorerError, SimilarityScore, score_rows, rank_candidates
from .normalizer import NormalizeError, NormalizeOptions, normalize_row
from .grouper import GroupError, DiffGroup
from .limiter import LimitError, LimitOptions, LimitResult
from .matcher import MatchError, MatchedPair, match_orphans
from .deduplicator import DeduplicateError, DeduplicateOptions, deduplicate_diff
from .classifier import ClassifyError, ClassifyOptions, ClassifiedChange
from .pivotter import PivotError, FieldPivot
from .ranker import RankError, RankOptions
from .flattener import FlattenError, FlatRow, flatten_diff
from .splitter import SplitError, SplitOptions
from .partitioner import PartitionError, PartitionOptions, PartitionResult
from .aggregator import AggregateError, FieldAggregate, aggregate import TransformError, TransformOptions
from .redactor import RedactError, RedactOptions
from .comparer import CompareError, CompareResult
from .indexer import IndexError as DiffIndexError, DiffIndex, build_index

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
    "changed_fields",
    # formatter
    "format_diff",
    # filter
    "FilterError",
    "filter_columns",
    "filter_diff_by_columns",
    "exclude_columns",
    # summary
    "DiffSummary",
    "summarize",
    "format_summary",
    # sorter
    "SortError",
    "sort_diff",
    "sort_keys",
    # merger
    "MergeError",
    "merge_diff",
    # stats
    "DiffStats",
    "compute_stats",
    # exporter
    "ExportError",
    "export_diff",
    # validator
    "ValidationError",
    "ValidationRule",
    "validate_diff",
    "assert_valid",
    # reporter
    "DiffReport",
    "build_report",
    "format_report",
    # highlighter
    "HighlightError",
    "HighlightedField",
    "highlight_diff",
    # truncator
    "TruncateError",
    "TruncateOptions",
    "TruncateResult",
    # sampler
    "SampleError",
    "SampleOptions",
    "sample_diff",
    # annotator
    "AnnotationError",
    "Annotation",
    "AnnotatedRow",
    # scorer
    "ScorerError",
    "SimilarityScore",
    "score_rows",
    "rank_candidates",
    # normalizer
    "NormalizeError",
    "NormalizeOptions",
    "normalize_row",
    # grouper
    "GroupError",
    "DiffGroup",
    # limiter
    "LimitError",
    "LimitOptions",
    "LimitResult",
    # matcher
    "MatchError",
    "MatchedPair",
    "match_orphans",
    # deduplicator
    "DeduplicateError",
    "DeduplicateOptions",
    "deduplicate_diff",
    # classifier
    "ClassifyError",
    "ClassifyOptions",
    "ClassifiedChange",
    # pivotter
    "PivotError",
    "FieldPivot",
    # ranker
    "RankError",
    "RankOptions",
    # flattener
    "FlattenError",
    "FlatRow",
    "flatten_diff",
    # splitter
    "SplitError",
    "SplitOptions",
    # partitioner
    "PartitionError",
    "PartitionOptions",
    "PartitionResult",
    # aggregator
    "AggregateError",
    "FieldAggregate",
    "aggregate_diff",
    # transformer
    "TransformError",
    "TransformOptions",
    # redactor
    "RedactError",
    "Red comparer
    "CompareError",
    "CompareResult",
    # indexer
    "DiffIndexError",
    "DiffIndex",
    "build_index",
]
