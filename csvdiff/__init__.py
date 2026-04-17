"""csvdiff public API – re-exports key symbols for convenience."""
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
from csvdiff.validator import ValidationError, ValidationRule, validate_diff, assert_valid
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
from csvdiff.deduplicator import DeduplicateError, DeduplicateOptions
from csvdiff.classifier import ClassifyError, ClassifyOptions, ClassifiedChange
from csvdiff.pivotter import PivotError, FieldPivot
from csvdiff.ranker import RankError, RankOptions
from csvdiff.flattener import FlattenError, FlatRow, flatten_diff
from csvdiff.splitter import SplitError, SplitOptions
from csvdiff.partitioner import PartitionError, PartitionOptions, PartitionResult
from csvdiff.aggregator import AggregateError, FieldAggregate, aggregate_diff
from csvdiff.transformer import TransformError, TransformOptions
from csvdiff.redactor import RedactError, RedactOptions
from csvdiff.comparer import CompareError, CompareResult
from csvdiff.indexer import DiffIndex
from csvdiff.differ_patch import PatchError, Patch, build_patch
from csvdiff.resolver import ResolveError, ResolveOptions, resolve_diff
from csvdiff.renamer import RenameError, RenameOptions
from csvdiff.caster import CastError, CastOptions
from csvdiff.masker import MaskError, MaskOptions
from csvdiff.encoder import EncodeError, encode_diff, decode_diff
from csvdiff.compressor import CompressError, CompressedDiff, compress_diff, decompress_diff
from csvdiff.freezer import FreezeError, FrozenDiff, freeze_diff
from csvdiff.tagger import TagError, TagOptions, TaggedChange, tag_diff
from csvdiff.trimmer import TrimError, TrimOptions
from csvdiff.labeler import LabelError, LabelRule, LabelOptions
from csvdiff.snapshotter import SnapshotError, SnapshotMeta, save_snapshot, load_snapshot
from csvdiff.pruner import PruneError, PruneOptions, PruneResult, prune_diff

__all__ = [
    "CSVParseError", "read_csv", "index_rows",
    "CSVDiffError", "FieldChange", "RowChange", "DiffResult", "changed_fields",
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
    "TruncateError", "TruncateOptions", "TruncateResult",
    "SampleError", "SampleOptions", "sample_diff",
    "AnnotationError", "Annotation", "AnnotatedRow",
    "ScorerError", "SimilarityScore", "score_rows", "rank_candidates",
    "NormalizeError", "NormalizeOptions", "normalize_row",
    "GroupError", "DiffGroup",
    "LimitError", "LimitOptions", "LimitResult",
    "MatchError", "MatchedPair", "match_orphans",
    "DeduplicateError", "DeduplicateOptions",
    "ClassifyError", "ClassifyOptions", "ClassifiedChange",
    "PivotError", "FieldPivot",
    "RankError", "RankOptions",
    "FlattenError", "FlatRow", "flatten_diff",
    "SplitError", "SplitOptions",
    "PartitionError", "PartitionOptions", "PartitionResult",
    "AggregateError", "FieldAggregate", "aggregate_diff",
    "TransformError", "TransformOptions",
    "RedactError", "RedactOptions",
    "CompareError", "CompareResult",
    "DiffIndex",
    "PatchError", "Patch", "build_patch",
    "ResolveError", "ResolveOptions", "resolve_diff",
    "RenameError", "RenameOptions",
    "CastError", "CastOptions",
    "MaskError", "MaskOptions",
    "EncodeError", "encode_diff", "decode_diff",
    "CompressError", "CompressedDiff", "compress_diff", "decompress_diff",
    "FreezeError", "FrozenDiff", "freeze_diff",
    "TagError", "TagOptions", "TaggedChange", "tag_diff",
    "TrimError", "TrimOptions",
    "LabelError", "LabelRule", "LabelOptions",
    "SnapshotError", "SnapshotMeta", "save_snapshot", "load_snapshot",
    "PruneError", "PruneOptions", "PruneResult", "prune_diff",
]
