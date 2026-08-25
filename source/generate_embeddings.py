"""
Generates embeddings for the knowledge base CSV using a local sentence-transformers
model (no API key / cost needed). Saves results to kb_embeddings.json.

Run: python3 generate_embeddings.py
"""

import os
import csv
import json
import sys

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    print("Missing dependency: sentence_transformers. Install with: pip install sentence-transformers")
    raise

# Resolve paths relative to the repository root (one level up from `source/`)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_CSV = os.path.join(BASE_DIR, "data", "kb.csv")
OUTPUT_JSON = os.path.join(BASE_DIR, "kb_embeddings.json")
MODEL_NAME = "all-mpnet-base-v2"  # stronger semantic quality than MiniLM, still free/local

if not os.path.exists(INPUT_CSV):
    print(f"Input CSV not found: {INPUT_CSV}")
    sys.exit(2)

print(f"Loading model {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)

rows = []
with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Embedding {len(rows)} KB entries...")
texts = [f"{r.get('title','')}: {r.get('content','')}" for r in rows]
embeddings = model.encode(texts, show_progress_bar=True).tolist()

output = []
for row, embedding in zip(rows, embeddings):
    output.append({
        "id": row.get("id"),
        "title": row.get("title"),
        "content": row.get("content"),
        "embedding": embedding,
    })

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f)

print(f"Saved {len(output)} embeddings to {OUTPUT_JSON}")