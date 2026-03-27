# Randomizer

Python utility that draws **verifiable random selections** from numbered pools. It uses digits derived from **Bitcoin block hashes** (via [Blockchain.com](https://www.blockchain.com/)’s public API) as the random stream, so anyone can reproduce the picks given the same start date and pool definitions.

## Requirements

- Python 3.8+ (3.13 works)
- Internet access (to fetch block data)

## Setup

```bash
cd path/to/Randomizer
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate`.

## Input files

Place these next to `main.py` before running:

| File | Purpose |
|------|--------|
| `date.txt` | Single line: start date as `YYYY-MM-DD` (e.g. `2025-12-05`). Block lookup uses UTC and advances one calendar day for the API query; the script then walks backward across days if it needs more entropy. |
| `list.xlsx` | Excel workbook with a sheet named **`list`**. Columns: **`total_pool`** (int, size of the pool, numbers `1` … `total_pool`) and **`choose_pool`** (int, how many distinct numbers to pick per row). |

## Run

```bash
python main.py
```

Optional: copy `run.bat` and point it at your Python executable and project folder, or run the command above from this directory.

## Output

- **`result.xlsx`** — One row per input row, including `total_pool`, `choose_pool`, `chosen` (selected numbers), and `row_finished_on` (date context used when that row finished).

## How it works (short)

1. Loads blocks for the relevant day from the API, sorts them, and builds a stream of decimal digits from their hex hashes.
2. For each row, it reads fixed-width chunks from that stream, maps them into `1` … `total_pool`, skips duplicates and out-of-range values, until `choose_pool` unique picks exist.
3. If the stream runs out, it prepends data from earlier days’ blocks.

## Dependencies

See `requirements.txt`: `pandas`, `openpyxl`, `requests`.
