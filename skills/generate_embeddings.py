"""
Generates semantic embeddings for the knowledge base CSV using fastembed
(ONNX-based, no torch, small footprint, fully local — no API key needed).

Run: python3 generate_embeddings.py
"""

import csv
import json

from fastembed import TextEmbedding

INPUT_CSV = "skills/kb.csv"
OUTPUT_JSON = "skills/kb_embeddings.json"
MODEL_NAME = "BAAI/bge-small-en-v1.5"  # small, fast, strong semantic quality, ONNX-based

print(f"Loading model {MODEL_NAME}...")
model = TextEmbedding(model_name=MODEL_NAME)

rows = []
with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Embedding {len(rows)} KB entries...")
texts = [f"{r['title']}: {r['content']}" for r in rows]
embeddings = list(model.embed(texts))

output = []
for row, embedding in zip(rows, embeddings):
    output.append({
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "embedding": embedding.tolist(),
    })

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f)

print(f"Saved {len(output)} embeddings to {OUTPUT_JSON}")