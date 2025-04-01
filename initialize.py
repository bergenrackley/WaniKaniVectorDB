from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
from pathlib import Path

# === Config ===
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
SOURCE_FILE = 'vocab_source.json'
INDEX_FILE = 'vocab_index.faiss'
METADATA_FILE = 'vocab_metadata.json'

# === Load vocab entries from source file ===
if not Path(SOURCE_FILE).exists():
    print(f"❌ Source file '{SOURCE_FILE}' not found.")
    exit(1)

with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
    entries = json.load(f)

if not entries:
    print("❌ No entries found in the source file.")
    exit(1)

# === Load model ===
print("🔤 Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

# === Generate embeddings ===
print("🧠 Generating embeddings...")
texts = [entry["text"] for entry in entries]
embeddings = model.encode(texts)
embeddings = np.array(embeddings).astype('float32')

# === Create FAISS index ===
print("📦 Creating and saving FAISS index...")
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, INDEX_FILE)

# === Save metadata ===
print("🗂 Saving metadata...")
with open(METADATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f"\n✅ Vector database initialized with {len(entries)} entries.")
