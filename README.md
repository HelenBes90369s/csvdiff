# csvdiff

A fast CLI tool for diffing two CSV files with configurable key columns and output formats.

---

## Installation

```bash
pip install csvdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/csvdiff.git
cd csvdiff && pip install -e .
```

---

## Usage

```bash
csvdiff [OPTIONS] FILE_A FILE_B
```

**Basic diff using the first column as the key:**

```bash
csvdiff old.csv new.csv
```

**Specify key columns:**

```bash
csvdiff --key id old.csv new.csv
```

**Use multiple key columns:**

```bash
csvdiff --key dept --key id old.csv new.csv
```

**Use a different output format:**

```bash
csvdiff --key id --format json old.csv new.csv
```

**Ignore specific columns during comparison:**

```bash
csvdiff --key id --ignore updated_at old.csv new.csv
```

### Options

| Option | Description |
|---|---|
| `--key`, `-k` | Column name(s) to use as the row key (default: first column) |
| `--format`, `-f` | Output format: `text`, `json`, or `csv` (default: `text`) |
| `--ignore`, `-i` | Column(s) to ignore during comparison |
| `--no-header` | Treat files as having no header row |

### Example Output

```
~ row changed  [id=42]  name: "Alice" → "Alicia"
+ row added    [id=99]  name: "Bob", age: "31"
- row removed  [id=17]
```

---

## License

MIT © 2024 [Your Name](https://github.com/yourname)
