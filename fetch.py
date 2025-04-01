import requests
import json
import time
import subprocess
import sys
import shutil
from pathlib import Path

# === Config ===
ASSIGNMENT_FILE = "assignment_data.json"
PROGRESS_FILE = "progress_assignment_data.json"
SUBJECT_DATA_FILE = "subject_data.json"
CONFIG_FILE = "config.json"
CONFIG_FILE_TEMPLATE = "config_template.json"
UPDATE_SCRIPT = "update_assignments.py"
API_ENDPOINT_TEMPLATE = "https://api.wanikani.com/v2/subjects/{subject_id}"
REQUESTS_PER_MINUTE = 58
SECONDS_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE

if not Path(CONFIG_FILE_TEMPLATE).exists():
    print("Config Template not found, exiting")
    exit(0)

if not Path(CONFIG_FILE).exists():
    print("⚠️  'config.json' not found. Creating from template...")
    shutil.copy("config_template.json", CONFIG_FILE)
    print("📄  Please fill in your actual API key in 'config.json'")
    exit(0)

# === Load Auth Key from config ===
with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)

AUTH_KEY = config.get("wanikani_api_key", "")
if not AUTH_KEY:
    print("❌ No 'wanikani_api_key' found in config.")
    exit(1)

HEADERS = {
    "Authorization": f"Bearer {AUTH_KEY}"
}

# === Load or create subject_data.json ===
if Path(SUBJECT_DATA_FILE).exists():
    with open(SUBJECT_DATA_FILE, 'r', encoding='utf-8') as f:
        subject_data = json.load(f)
else:
    subject_data = []

# Convert to dict for fast lookup of existing IDs
existing_ids = {entry["id"] for entry in subject_data}

# Run update.py to fetch assignment_data.json
print("📡 Running update_assignments.py to fetch assignment data...")
subprocess.run([sys.executable, UPDATE_SCRIPT], check=True)
if not Path(ASSIGNMENT_FILE).exists():
    print(f"❌ '{ASSIGNMENT_FILE}' not found after running update.")
    exit(1)

# === Load or create progress file ===
if Path(PROGRESS_FILE).exists():
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        progress_data = json.load(f)
    with open(ASSIGNMENT_FILE, 'r', encoding='utf-8') as f:
        assignment_data = json.load(f)

    for assignment in assignment_data:
        if ((sid := assignment["data"]["subject_id"]) not in existing_ids and sid not in {entry["data"]["subject_id"] for entry in progress_data}):
            progress_data.append(assignment)

    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

else:
    with open(ASSIGNMENT_FILE, 'r', encoding='utf-8') as f:
        progress_data = json.load(f)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)


# === Process ===
i = 0

while i < len(progress_data):
    assignment = progress_data[i]
    subject_id = assignment["data"]["subject_id"]

    if subject_id in existing_ids:
        print(f"✅ Skipping already-fetched subject_id {subject_id}")
        progress_data.pop(i)
        continue

    # Fetch subject data
    url = API_ENDPOINT_TEMPLATE.format(subject_id=subject_id)
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"❌ Failed to fetch subject_id {subject_id}: {response.status_code}")
        break

    subject = response.json()
    subject_data.append(subject)
    existing_ids.add(subject_id)
    print(f"⬇️ Fetched subject_id {subject_id}")

    # Remove from progress list
    progress_data.pop(i)

    # Save progress and subject data
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)
    with open(SUBJECT_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(subject_data, f, ensure_ascii=False, indent=2)

    time.sleep(SECONDS_BETWEEN_REQUESTS)

if not progress_data and Path(PROGRESS_FILE).exists():
    Path(PROGRESS_FILE).unlink()
    print("🧹 All subjects fetched. Deleted progress file.")