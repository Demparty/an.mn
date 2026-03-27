# Member selection

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
**Function Summaries (what each does):**

- **getDate(txt_path)**
  - Reads and returns a date string (expected format: `YYYY-MM-DD`) from a text file.

- **getList(xlsx_path)**
  - Loads the Excel sheet named `list` from the provided file into a pandas DataFrame.

- **getBlock(date_str)**
  - Parses `date_str` as UTC, adds one day, and converts it to a Unix timestamp (milliseconds).
  - Fetches blocks from `https://blockchain.info/blocks/<timestamp>?format=json`.
  - Sorts the blocks by their time.
  - Returns a dictionary mapping `block_index` to a dictionary with keys: `timestamp` and `hash` (and `height` if available).
  - On error, prints the exception and returns an empty dictionary (`{}`).

- **generate(date_str, pool_list)**
  - Main selection logic:
    - Fetches block data for the input date; if not present, steps back day by day until data is found.
    - Concatenates all block hashes for those blocks, converting each from hex to decimal digits, building one long stream (`decimal_stream`).
    - For each row in `pool_list`:
      - Reads `id`, `sector_name`, `total_pool`, and `choose_pool`.
      - Determines how many digits are needed per random number (using `ceil(log10(total_pool + 1))`).
      - Slices fixed-size chunks from `decimal_stream`, converts each to integer, and accepts it as a selection if:
        - The number is between 1 and `total_pool` (inclusive), **and**
        - The number hasn't already been picked for this row (ensures uniqueness).
      - If `decimal_stream` runs out of digits, fetches earlier day blocks and continues appending digits.
      - Collects and saves, for each row: chosen numbers, input metadata, date used for selection (`row_finished_on`), and the first 5 block hashes used.

## Dependencies

See `requirements.txt`: `pandas`, `openpyxl`, `requests`.
