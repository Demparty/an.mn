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

### What each function does
- getDate(txt_path)
Reads a date string from a text file (expected format: YYYY-MM-DD).

- getList(xlsx_path)
Loads the Excel sheet named list into a pandas DataFrame.

- getBlock(date_str)

Parses the given date in UTC, adds 1 day, and converts that to a timestamp (ms).
Calls https://blockchain.info/blocks/<timestamp>?format=json.
Sorts returned blocks by time.
Returns a dictionary like:
key: block_index
value: { "timestamp": "...", "hash": "..." }
On any error, prints it and returns {}.
generate(date_str, pool_list)
- Core logic:

Gets block data for the input date; if unavailable, keeps stepping back day-by-day until data exists.
Converts each block hash from hex to decimal and concatenates all digits into one long decimal_stream.
For each row in pool_list:
Reads ID, uuriin_hayg, total_pool, choose_pool.
Computes digit width with ceil(log10(total_pool + 1)) (how many digits to read per attempt).
Repeatedly slices fixed-size chunks from decimal_stream, converts to int, and accepts numbers that are:
between 1 and total_pool
not already chosen (unique picks)
If stream runs out, it fetches older day blocks, appends more digits, and continues.
Stores one result object per row:
metadata + selected numbers (chosen)
date where row finished (row_finished_on)
a hash field.

## Dependencies

See `requirements.txt`: `pandas`, `openpyxl`, `requests`.
