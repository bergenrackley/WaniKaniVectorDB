import json
import sys
from pathlib import Path
from datetime import datetime

# === Config ===
SUBJECT_DATA_FILE = "subject_data.json"
SOURCE_FILE = "vocab_source.json"
NEW_VOCAB_FILE = "new_vocab.json"

# === Load subject_data.json ===
if not Path(SUBJECT_DATA_FILE).exists():
    print(f"❌ '{SUBJECT_DATA_FILE}' not found.")
    exit(1)

with open(SUBJECT_DATA_FILE, 'r', encoding='utf-8') as f:
    subject_data = json.load(f)

# === Load or initialize vocab_source.json ===
source_exists = Path(SOURCE_FILE).exists()
if source_exists:
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        vocab_source = json.load(f)
    existing_texts_source = {entry["text"] for entry in vocab_source}
else:
    vocab_source = []
    existing_texts_source = set()

# === Load or initialize new_vocab.json ONLY if vocab_source exists ===
if source_exists:
    if Path(NEW_VOCAB_FILE).exists():
        with open(NEW_VOCAB_FILE, 'r', encoding='utf-8') as f:
            new_vocab = json.load(f)
    else:
        new_vocab = []
    existing_texts_new = {entry["text"] for entry in new_vocab}
else:
    new_vocab = None
    existing_texts_new = set()

# === Extract entries ===
added_count = 0

for subject in subject_data:
    data = subject.get("data", {})
    subject_type = subject.get("object")
    if subject_type not in ["kanji", "vocabulary"]:
        continue

    text = data.get("characters")
    if not text:
        continue

    if text in existing_texts_source or text in existing_texts_new:
        continue

    meanings = [m["meaning"] for m in data.get("meanings", []) if m.get("accepted_answer")]
    readings = [r["reading"] for r in data.get("readings", []) if r.get("accepted_answer")] if "readings" in data else []

    # Extract context sentences
    example_sentences = []
    if subject_type == "vocabulary" and "context_sentences" in data:
        for sentence in data["context_sentences"]:
            if "ja" in sentence and "en" in sentence:
                example_sentences.append({
                    "jp": sentence["ja"],
                    "en": sentence["en"]
                })

    entry = {
        "text": text,
        "readings": readings,
        "meanings": meanings,
        "type": subject_type,
        "example_sentences": example_sentences,
        "added_at": datetime.utcnow().isoformat(),
        "wanikani_id": subject.get("id")
    }

    vocab_source.append(entry)
    if new_vocab is not None:
        new_vocab.append(entry)

    added_count += 1

# === Save files ===
with open(SOURCE_FILE, 'w', encoding='utf-8') as f:
    json.dump(vocab_source, f, ensure_ascii=False, indent=2)

if new_vocab is not None:
    with open(NEW_VOCAB_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_vocab, f, ensure_ascii=False, indent=2)

if "--api" in sys.argv:
    print(f"ADDED_COUNT::{added_count}")
else:
    print(f"✅ Added {added_count} new vocab entries.")
