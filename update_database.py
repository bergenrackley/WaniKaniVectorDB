import json
import faiss
import numpy as np
import sys
from sentence_transformers import SentenceTransformer
from pathlib import Path

# === Config ===
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
INDEX_FILE = 'vocab_index.faiss'
METADATA_FILE = 'vocab_metadata.json'
NEW_VOCAB_FILE = 'new_vocab.json'

# === Load new vocab entries ===
if not Path(NEW_VOCAB_FILE).exists():
    print(f"❌ '{NEW_VOCAB_FILE}' not found. Nothing to add.")
    exit(0)

with open(NEW_VOCAB_FILE, 'r', encoding='utf-8') as f:
    new_vocab = json.load(f)

if not new_vocab:
    print("ℹ️ No new vocab entries to add.")
    exit(0)

# === Load existing metadata ===
if Path(METADATA_FILE).exists():
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        vocab_metadata = json.load(f)
else:
    vocab_metadata = []

# === Load or create FAISS index ===
if Path(INDEX_FILE).exists():
    index = faiss.read_index(INDEX_FILE)
else:
    index = None

# === Load embedding model ===
print("🧠 Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

# === Encode new text entries ===
texts = [entry["text"] for entry in new_vocab]
print(f"🔡 Encoding {len(texts)} new entries...")
embeddings = model.encode(texts)
embeddings = np.array(embeddings).astype('float32')

# === Create or update index ===
if index is None:
    print("📦 Creating new FAISS index...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
else:
    print("📥 Appending to existing FAISS index...")

index.add(embeddings)

# === Append to metadata and save ===
vocab_metadata.extend(new_vocab)
with open(METADATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(vocab_metadata, f, ensure_ascii=False, indent=2)

# === Save updated index ===
faiss.write_index(index, INDEX_FILE)

# === Clear new_vocab.json ===
Path(NEW_VOCAB_FILE).unlink()

if "--api" in sys.argv:
    print(f"NEW_COUNT::{len(new_vocab)}")
else:
    print(f"✅ Added {len(new_vocab)} new vocab entries to the database and cleared '{NEW_VOCAB_FILE}'.")

