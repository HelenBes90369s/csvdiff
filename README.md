# csvdiff

A fast CLI tool for diffing two CSV files with configurable key columns and output formats.

## Installation

```bash
pip install csvdiff
```

## Quick Start

```bash
csvdiff old.csv new.csv --key id
csvdiff old.csv new.csv --key id,name --format json
csvdiff old.csv new.csv --key id --format csv --output diff.csv
```

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--key` | `id` | Comma-separated key columns |
| `--format` | `text` | Output format: `text`, `json`, `csv` |
| `--output` | stdout | Write output to file |
| `--columns` | all | Restrict diff to these columns |
| `--exclude` | none | Exclude these columns from diff |
| `--ignore-case` | off | Case-insensitive comparison |
| `--strip` | off | Strip whitespace before comparing |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No differences found |
| 1 | Differences found |
| 2 | Error (missing file, bad CSV, etc.) |

## Python API

```python
from csvdiff import read_csv, index_rows, compute_diff

old_rows = read_csv("old.csv")
new_rows = read_csv("new.csv")
old_index = index_rows(old_rows, keys=["id"])
new_index = index_rows(new_rows, keys=["id"])
result = compute_diff(old_index, new_index)
```

## Signal / Lifecycle Hooks

`SignalOptions` lets you attach callbacks to diff lifecycle events without
modifying the core pipeline.

```python
from csvdiff import SignalOptions, SignalState, emit_diff_signals

def on_changed(result):
    print(f"Changes detected: {len(result.changed)} rows modified")

opts = SignalOptions(
    handlers={
        "on_changed": [on_changed],
        "on_empty": [lambda r: print("Files are identical")],
    }
)
state = SignalState(options=opts)

# After running your diff:
emit_diff_signals(state, diff_result)
```

### Available Signals

| Signal | Fired when |
|--------|------------|
| `pre_diff` | Before diffing starts (fire manually) |
| `post_diff` | After every successful diff |
| `on_empty` | Result has no changes |
| `on_changed` | Result has at least one change |
| `on_error` | An error occurred during diffing |

## Modules

| Module | Purpose |
|--------|---------|
| `parser` | Read and index CSV files |
| `differ` | Core diff algorithm |
| `formatter` | Text / JSON / CSV output |
| `filter` | Column inclusion/exclusion |
| `summary` | High-level change summary |
| `pager` | Paginate large diffs |
| `sorter` | Sort diff results |
| `merger` | Apply a diff back to a dataset |
| `stats` | Numeric statistics over a diff |
| `exporter` | Export diff to file formats |
| `validator` | Enforce rules on a diff |
| `reporter` | Structured diff reports |
| `highlighter` | ANSI colour highlighting |
| `truncator` | Truncate long field values |
| `sampler` | Random / top-N sampling |
| `annotator` | Attach metadata to changes |
| `scorer` | Row similarity scoring |
| `normalizer` | Pre-diff value normalisation |
| `grouper` | Group changes by kind or field |
| `limiter` | Hard caps on change counts |
| `matcher` | Match orphaned add/remove pairs |
| `deduplicator` | Remove duplicate change rows |
| `classifier` | Severity classification |
| `pivotter` | Pivot field-level changes |
| `ranker` | Rank rows by change magnitude |
| `flattener` | Flatten diff to plain rows |
| `splitter` | Split diff by column value |
| `partitioner` | Partition diff into buckets |
| `aggregator` | Numeric aggregation per field |
| `transformer` | Apply transforms to row values |
| `redactor` | Redact sensitive fields |
| `comparer` | Compare two diff results |
| `indexer` | Random-access index over a diff |
| `differ_patch` | Patch-set representation |
| `resolver` | Conflict resolution strategies |
| `renamer` | Rename columns in a diff |
| `caster` | Type-cast field values |
| `masker` | Mask field values |
| `encoder` | JSON serialisation round-trip |
| `compressor` | In-memory diff compression |
| `freezer` | Immutable signed snapshots |
| `tagger` | Rule-based tagging |
| `trimmer` | Whitespace trimming |
| `labeler` | Human-readable labels |
| `snapshotter` | Persist diff to disk |
| `pruner` | Predicate-based pruning |
| `scorer2` | Weighted change scoring |
| `joiner` | Join two diff results |
| `scaler` | Numeric delta scaling |
| `aligner` | Align two diff results |
| `windower` | Sliding-window views |
| `differ_signal` | Lifecycle signal callbacks |

## Contributing

```bash
git clone https://github.com/example/csvdiff
cd csvdiff
pip install -e .[dev]
pytest
```

## Licence

MIT
