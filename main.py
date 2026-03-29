import requests
from datetime import datetime, timezone, timedelta
import math
import pandas as pd


def getDate(txt_path):
    with open(txt_path, "r") as f:
        date = f.read()
    return date


def getList(xlsx_path):
    xlsx_list = pd.read_excel(xlsx_path, sheet_name="list", engine="openpyxl")
    return xlsx_list

def getSelectionList(xlsx_path):
    xlsx_list = pd.read_excel(xlsx_path, sheet_name="list", engine="openpyxl")
    return xlsx_list


def getBlock(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    date += timedelta(days=1)
    timestamp_ms = int(date.timestamp()) * 1000
    url = f"https://blockchain.info/blocks/{timestamp_ms}?format=json"

    try:
        res = requests.get(url)
        res.raise_for_status()
        blocks = res.json()
        sorted_blocks = sorted(blocks, key=lambda b: b["time"])

        block_dict = {
            b["block_index"]: {
                "timestamp": datetime.fromtimestamp(
                    b["time"], tz=timezone.utc
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "hash": b["hash"],
                "height": b.get("height", b["block_index"]),
            }
            for b in sorted_blocks
        }
        # Write block data (as JSON) to a file for inspection
        import json
        with open("block_data.json", "w", encoding="utf-8") as outfile:
            json.dump(block_dict, outfile, indent=4, ensure_ascii=False)
        return block_dict

    except Exception as e:
        print("Error fetching blocks:", e)
        return {}


def generate(date_str, pool_list):

    all_results = []

    current_date_dt = datetime.strptime(date_str, "%Y-%m-%d")
    current_date_str = current_date_dt.strftime("%Y-%m-%d")

    block_data = getBlock(current_date_str)
    while not block_data:
        current_date_dt -= timedelta(days=1)
        current_date_str = current_date_dt.strftime("%Y-%m-%d")
        block_data = getBlock(current_date_str)

    decimal_stream = "".join(
        str(int(block["hash"], 16)) for block in block_data.values()
    )
    pos = 0

    for _, row in pool_list.iterrows():
        id = int(row["id"])
        uuriin_hayg = str(row["sector_name"])
        file_name = str(row["file_name"])
        choose_pool = int(row["choose_count"])
        chosen = []
        chosen_id = []
        chosen_name = []
        selection_list = getSelectionList(f"./list/{file_name}")
        total_pool = len(selection_list)
        digits = math.ceil(math.log10(total_pool + 1))
        while len(chosen) < choose_pool:
            if pos + digits > len(decimal_stream):
                prev_date_dt = current_date_dt - timedelta(days=1)
                prev_date_str = prev_date_dt.strftime("%Y-%m-%d")
                prev_block_data = getBlock(prev_date_str)
                while not prev_block_data:
                    prev_date_dt -= timedelta(days=1)
                    prev_date_str = prev_date_dt.strftime("%Y-%m-%d")
                    prev_block_data = getBlock(prev_date_str)

                new_stream = "".join(
                    str(int(block["hash"], 16)) for block in prev_block_data.values()
                )
                decimal_stream += new_stream
                current_date_dt = prev_date_dt
                current_date_str = prev_date_str

            chunk = decimal_stream[pos : pos + digits]
            pos += digits
            if len(chunk) < digits:
                continue

            num = int(chunk)
            if 1 <= num <= total_pool and num not in chosen:
                chosen.append(num)
        for _, row in selection_list.iterrows():
            if row["id"] in chosen:
                chosen_id.append(int(row["id"]))
                chosen_name.append(str(row["unique_id"]))
        all_results.append(
            {
                
                "id": id,
                "sector_name": uuriin_hayg,
                "file_name": file_name,
                "total_count": total_pool,
                "choose_count": choose_pool,
                "chosen_id": chosen_id,
                "chosen_name": chosen_name,
                "row_finished_on": current_date_str,
            }
        )

    return all_results


if __name__ == "__main__":
    date = getDate("./date.txt")
    pool_list = getList("./list.xlsx")
    df = pd.json_normalize(generate(date, pool_list))
    df.to_excel("./result.xlsx", index=False)
