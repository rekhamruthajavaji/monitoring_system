import os
import json
import sys
from datetime import datetime

if len(sys.argv) < 2:
    print("Usage: python monitor.py <config_file>")
    exit()

config_file = sys.argv[1]

with open(config_file) as f:
    config = json.load(f)

SERVER_NAME = config["server"]["name"]
INPUT_PATH = config["server"]["input_path"]
OUTPUT_PATH = config["server"]["output_path"]
COMMON_JSON = config["common_json"]
def get_file_details(path):
    if not os.path.exists(path):
        return 0, {}

    total_files = 0
    types = {}

    # 🔥 Traverse all folders and subfolders
    for root, dirs, files in os.walk(path):
        for f in files:
            total_files += 1

            if "." in f:
                ext = f.split(".")[-1]
                types[ext] = types.get(ext, 0) + 1

    return total_files, types

def update_json():
    input_count, input_types = get_file_details(INPUT_PATH)
    output_count, output_types = get_file_details(OUTPUT_PATH)

    status = "SUCCESS" if output_count >= input_count else "FAIL"

    server_data = {
        "last_run": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input": input_count,
        "output": output_count,
        "input_types": input_types,
        "output_types": output_types,
        "status": status
    }

    if os.path.exists(COMMON_JSON):
        with open(COMMON_JSON, "r") as f:
            content = json.load(f)
    else:
        content = {"servers": {}}

    content["servers"][SERVER_NAME] = server_data

    with open(COMMON_JSON, "w") as f:
        json.dump(content, f, indent=4)

    print(f"{SERVER_NAME} updated JSON")

if __name__ == "__main__":
    update_json()
