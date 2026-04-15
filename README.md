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
csvdiff old.csv new.csv --key id --columns price,stock
```

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--key` | `id` | Comma-separated key column(s) |
| `--format` | `text` | Output format: `text`, `json`, `csv` |
| `--columns` | *(all)* | Only diff these columns |
| `--exclude` | *(none)* | Exclude these columns from diff |
| `--page` | *(off)* | Page size for paginated output |
| `--sort` | *(off)* | Sort output by key column |
| `--limit` | *(off)* | Max rows per change type |
| `--top` | *(off)* | Show top N most-changed rows |

## Python API

```python
from csvdiff import read_csv, index_rows, diff_results, format_diff
from csvdiff import rank_diff, top_n, RankOptions

old_rows = read_csv("old.csv")
new_rows = read_csv("new.csv")

old_idx = index_rows(old_rows, keys=["id"])
new_idx = index_rows(new_rows, keys=["id"])

result = diff_results(old_idx, new_idx)

# Print a text diff
print(format_diff(result))

# Rank changes — most fields changed first
ranked = rank_diff(result)

# Top 5 rows with the most changes to the 'price' field
hot = top_n(result, 5, RankOptions(field="price"))
```

## Modules

| Module | Purpose |
|--------|---------|
| `parser` | Read and index CSV files |
| `differ` | Core diff algorithm |
| `formatter` | Text / JSON / CSV output |
| `filter` | Column inclusion / exclusion |
| `summary` | High-level change summary |
| `pager` | Paginate large diffs |
| `sorter` | Sort changes by key |
| `merger` | Apply a diff to a base CSV |
| `stats` | Numeric statistics about a diff |
| `exporter` | Export diffs to files |
| `validator` | Assert diff stays within thresholds |
| `reporter` | Structured diff reports |
| `highlighter` | ANSI colour highlighting |
| `truncator` | Truncate long field values |
| `sampler` | Random / top-N sampling |
| `annotator` | Attach metadata annotations |
| `scorer` | Similarity scoring for row matching |
| `normalizer` | Normalise values before diffing |
| `grouper` | Group changes by kind or field |
| `limiter` | Cap result sizes |
| `matcher` | Match orphaned added/removed rows |
| `deduplicator` | Remove duplicate changes |
| `classifier` | Classify changes by severity |
| `pivotter` | Pivot field-level change stats |
| `ranker` | Rank changes by number of field edits |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No differences found |
| 1 | Differences found |
| 2 | Error (missing file, bad CSV, etc.) |

## License

MIT
