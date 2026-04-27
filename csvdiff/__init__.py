"""csvdiff – public re-exports."""
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
from csvdiff.validator import ValidationError, ValidationResult, validate_diff, assert_valid
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
from csvdiff.indexer import IndexError as DiffIndexError, DiffIndex
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
from csvdiff.labeler import LabelError, LabelOptions, LabeledChange
from csvdiff.snapshotter import SnapshotError, SnapshotMeta, save_snapshot, load_snapshot
from csvdiff.pruner import PruneError, PruneOptions, PruneResult, prune_diff
from csvdiff.scorer2 import WeightError, WeightOptions, ScoredChange
from csvdiff.joiner import JoinError, JoinOptions, join_diff
from csvdiff.scaler import ScaleError, ScaledChange
from csvdiff.aligner import AlignError, AlignedPair, align_diff
from csvdiff.windower import WindowError, WindowOptions, DiffWindow
from csvdiff.differ_cache import CacheError, CacheOptions
from csvdiff.differ_watch import WatchError, WatchOptions, WatchState
from csvdiff.differ_timeout import TimeoutError as DiffTimeoutError, TimeoutOptions, run_with_timeout
from csvdiff.differ_retry import RetryError, RetryOptions, run_with_retry
from csvdiff.differ_progress import ProgressError, ProgressOptions, ProgressState
from csvdiff.differ_throttle import ThrottleError, ThrottleOptions, ThrottleState
from csvdiff.differ_batch import BatchError, BatchOptions, BatchEntry
from csvdiff.differ_audit import AuditError, AuditEntry, build_entry
from csvdiff.differ_hook import HookError, HookOptions, HookState, run_hooks
from csvdiff.differ_schema import SchemaError, DiffSchema, build_schema
from csvdiff.differ_log import LogError, LogOptions, LogEntry
from csvdiff.differ_pipeline import PipelineError, PipelineOptions, PipelineResult, run_pipeline
from csvdiff.differ_metrics import MetricsError, MetricsOptions, DiffMetrics, collect_metrics
from csvdiff.differ_event import EventError, EventOptions, EventState
from csvdiff.differ_debounce import DebounceError, DebounceOptions, DebounceState
from csvdiff.differ_lock import LockError, LockOptions, LockHandle
from csvdiff.differ_notify import NotifyError, NotifyOptions, NotifyPayload
from csvdiff.differ_rate import RateError, RateOptions, RateState
from csvdiff.differ_checkpoint import CheckpointError, CheckpointOptions, CheckpointMeta
from csvdiff.differ_queue import QueueError, QueueOptions, QueueEntry
from csvdiff.differ_pool import PoolError, PoolOptions, PoolResult
from csvdiff.differ_dispatcher import DispatchError, DispatchOptions, dispatch
from csvdiff.differ_circuit import CircuitError, CircuitOptions, CircuitState
from csvdiff.differ_replay import ReplayError, ReplayOptions, ReplayResult
from csvdiff.differ_tracer import TracerError, TracerOptions, Span
from csvdiff.differ_semaphore import SemaphoreError, SemaphoreOptions, SemaphoreState
from csvdiff.differ_buffer import BufferError, BufferOptions, BufferState
from csvdiff.differ_router import RouterError, RouterOptions
from csvdiff.differ_cursor import CursorError, CursorOptions, CursorState
from csvdiff.differ_dedupe_run import DedupeRunError, DedupeRunOptions, DedupeRunState
from csvdiff.differ_throttle_burst import BurstThrottleError, BurstThrottleOptions, BurstThrottleState
from csvdiff.differ_fallback import FallbackError, FallbackStep, FallbackResult
from csvdiff.differ_hedge import HedgeError, HedgeOptions, HedgeResult
from csvdiff.differ_signal import SignalError, SignalOptions, SignalState, emit_diff_signals

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
    "ValidationError", "ValidationResult", "validate_diff", "assert_valid",
    "DiffReport", "build_report", "format_report",
    "HighlightError", "HighlightedField", "highlight_diff",
    "SignalError", "SignalOptions", "SignalState", "emit_diff_signals",
]
