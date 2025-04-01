from fastapi import FastAPI, Query, HTTPException
from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np
import subprocess
import sys

app = FastAPI()

# Shared app state
vector_index = None
metadata = None
model = None

@app.on_event("startup")
def initial_startup():
    load_vector_database()

def load_vector_database():
    global vector_index, metadata, model

    if all([vector_index, metadata, model]):
        return False  # Already loaded

    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    vector_index = faiss.read_index("vocab_index.faiss")
    with open("vocab_metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)

    print("✅ Vector DB loaded manually")
    return True


@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/pingdb")
def pingdb():
    status = all([vector_index, metadata, model])
    return {"status": "ok" if status else "error"}

@app.post("/startup")
def manual_startup():
    loaded = load_vector_database()
    return {"status": "loaded" if loaded else "already loaded"}

@app.get("/search")
def search(q: str = Query(..., description="Query string"), top_k: int = 5):
    # Encode the query
    query_vector = model.encode([q]).astype('float32')
    
    # Search FAISS
    D, I = vector_index.search(query_vector, k=top_k)
    
    # Format results
    results = []
    for idx, dist in zip(I[0], D[0]):
        if idx < len(metadata):
            entry = metadata[idx]
            results.append({
                "text": entry["text"],
                "readings": entry["readings"],
                "meanings": entry["meanings"],
                "type": entry["type"],
                "distance": float(dist)
            })

    return {"results": results}

@app.post("/fetch")
def run_fetch_script():
    try:
        result = subprocess.run(
            [sys.executable, "fetch.py"],
            check=True,
            capture_output=True,
            text=True
        )
        return {"status": "ok", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fetch script failed:\n{e.stderr}"
        )

@app.post("/stagepending")
def run_parse_script():
    try:
        result = subprocess.run(
            [sys.executable, "parse.py", "--api"],
            check=True,
            capture_output=True,
            text=True
        )

        stdout = result.stdout.strip()
        added = 0
        for line in stdout.splitlines():
            if line.startswith("ADDED_COUNT::"):
                added = int(line.split("::")[1])
                break

        return {"status": "ok", "added": added}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Parse script failed:\n{e.stderr.strip()}"
        )

@app.post("/update")
def run_parse_script():
    try:
        result = subprocess.run(
            [sys.executable, "update.py", "--api"],
            check=True,
            capture_output=True,
            text=True
        )

        stdout = result.stdout.strip()
        new = 0
        for line in stdout.splitlines():
            if line.startswith("NEW_COUNT::"):
                new = int(line.split("::")[1])
                break

        return {"status": "ok", "new": new}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Update script failed:\n{e.stderr.strip()}"
        )
