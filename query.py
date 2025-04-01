from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

# === Config ===
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
INDEX_FILE = 'vocab_index.faiss'
METADATA_FILE = 'vocab_metadata.json'
TOP_K = 5

# === Load model and data ===
print("Loading model and vector index...")
model = SentenceTransformer(MODEL_NAME)
index = faiss.read_index(INDEX_FILE)

with open(METADATA_FILE, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# === Start query loop ===
print("\nType a word in Japanese or English to search (or 'exit'):")

while True:
    query = input("🔍 > ").strip()
    if query.lower() in ["exit", "quit"]:
        break
    if not query:
        continue

    # Encode and search
    query_vector = model.encode([query]).astype('float32')
    distances, indices = index.search(query_vector, TOP_K)

    # Display results
    print("\n📚 Top Matches:")
    for rank, idx in enumerate(indices[0]):
        if idx >= len(metadata):
            print(f"{rank + 1}. [Invalid index: {idx}]")
            continue

        entry = metadata[idx]
        print(f"{rank + 1}. {entry['text']} ({entry['type']})")
        print(f"   📖 Meanings: {', '.join(entry['meanings'])}")
        print(f"   📚 Readings: {', '.join(entry['readings'])}")
        if entry.get("wanikani_id") is not None:
            print(f"   🔗 WaniKani ID: {entry['wanikani_id']}")
        print(f"   🕒 Added: {entry['added_at']}")

        # Show example sentences
        if entry.get("example_sentences"):
            print("   ✍️ Examples:")
            for ex in entry["example_sentences"]:
                print(f"     ・{ex['jp']}")
                print(f"       {ex['en']}")
        print("")

print("👋 Done.")
