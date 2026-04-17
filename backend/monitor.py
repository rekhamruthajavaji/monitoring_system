import os
import json
import sys
from datetime import datetime

# Check config argument
if len(sys.argv) < 2:
    print("Usage: python monitor.py <config_file>")
    exit()

config_file = sys.argv[1]

# Load config file
with open(config_file) as f:
    config = json.load(f)

SERVER_NAME = config["server"]["name"]
INPUT_PATH = config["server"]["input_path"]
OUTPUT_PATH = config["server"]["output_path"]

# BASE DIR (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# FIX PATHS
INPUT_PATH = os.path.abspath(os.path.join(BASE_DIR, INPUT_PATH))
OUTPUT_PATH = os.path.abspath(os.path.join(BASE_DIR, OUTPUT_PATH))

# JSON PATH
COMMON_JSON = os.path.join(BASE_DIR, "shared", "monitoring.json")

# Ensure shared folder exists
os.makedirs(os.path.dirname(COMMON_JSON), exist_ok=True)


# FUNCTION
def get_file_details(path):
    if not os.path.exists(path):
        print(f"❌ Path not found: {path}")
        return 0, {}, 0, [], {}

    total_files = 0
    total_size = 0
    types = {}
    type_sizes = {}
    file_list = []

    for root, dirs, files in os.walk(path):
        for f in files:
            file_path = os.path.join(root, f)

            if not os.path.isfile(file_path):
                continue

            size = os.path.getsize(file_path)

            total_files += 1
            total_size += size

            file_list.append({
                "name": os.path.relpath(file_path, path),
                "size": size
            })

            if "." in f:
                ext = f.split(".")[-1].lower()
                types[ext] = types.get(ext, 0) + 1
                type_sizes[ext] = type_sizes.get(ext, 0) + size

    return total_files, types, total_size, file_list, type_sizes


# UPDATE JSON
def update_json():
    print("📁 INPUT PATH:", INPUT_PATH)
    print("📁 OUTPUT PATH:", OUTPUT_PATH)
    print("💾 Saving JSON at:", COMMON_JSON)

    input_count, input_types, input_size, input_files, input_type_sizes = get_file_details(INPUT_PATH)
    output_count, output_types, output_size, output_files, output_type_sizes = get_file_details(OUTPUT_PATH)

    # ✅ STATUS BASED ON FILE COUNT
    if input_count <= output_count:
        status = "SUCCESS"
    else:
        status = "FAIL"

    server_data = {
        "last_run": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input": input_count,
        "output": output_count,
        "input_size": input_size,
        "output_size": output_size,
        "input_types": input_types,
        "output_types": output_types,
        "input_type_sizes": input_type_sizes,
        "output_type_sizes": output_type_sizes,
        "input_files": input_files,
        "output_files": output_files,
        "status": status
    }

    # Read existing JSON
    if os.path.exists(COMMON_JSON):
        with open(COMMON_JSON, "r") as f:
            content = json.load(f)
    else:
        content = {"servers": {}}

    content["servers"][SERVER_NAME] = server_data

    # Write JSON
    with open(COMMON_JSON, "w") as f:
        json.dump(content, f, indent=4)

    print(f"✅ {SERVER_NAME} updated successfully")


# RUN
if __name__ == "__main__":
    update_json()