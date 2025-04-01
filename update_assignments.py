import requests
import json
import time
import shutil
from pathlib import Path

# === Config ===
API_URL = "https://api.wanikani.com/v2/assignments?in_review=true"
ASSIGNMENT_FILE = "assignment_data.json"
CONFIG_FILE = "config.json"
CONFIG_FILE_TEMPLATE = "config_template.json"
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
if not Path(CONFIG_FILE).exists():
    print(f"❌ Missing '{CONFIG_FILE}'. Create it with your WaniKani API key.")
    exit(1)

with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)

AUTH_KEY = config.get("wanikani_api_key", "")
if not AUTH_KEY:
    print("❌ No 'wanikani_api_key' found in config.")
    exit(1)

HEADERS = {
    "Authorization": f"Bearer {AUTH_KEY}"
}

def fetch_all_assignments():
    url = API_URL
    all_data = []

    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Failed to fetch: {response.status_code}")
            break

        payload = response.json()
        page_data = payload.get("data", [])
        all_data.extend(page_data)

        url = payload.get("pages", {}).get("next_url")

        time.sleep(SECONDS_BETWEEN_REQUESTS)

    # Save to file
    with open(ASSIGNMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(all_data)} assignments to '{ASSIGNMENT_FILE}'")

fetch_all_assignments()