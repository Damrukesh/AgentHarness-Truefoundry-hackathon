"""
Generates semantic embeddings for the knowledge base CSV using HuggingFace's
free Inference API (no local model download, no torch, sandbox-safe).

Requires a free HF token: https://huggingface.co/settings/tokens
Set it as an environment variable: HF_TOKEN

Run: python3 generate_embeddings.py
"""

import csv
import json
import os
import time

import requests

INPUT_CSV = "skills/kb.csv"
OUTPUT_JSON = "skills/kb_embeddings.json"
MODEL_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-mpnet-base-v2/pipeline/feature-extraction"

HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("Set the HF_TOKEN environment variable (free token from huggingface.co/settings/tokens)")

headers = {"Authorization": f"Bearer {HF_TOKEN}"}


def get_embedding(text):
    for attempt in range(3):
        response = requests.post(MODEL_URL, headers=headers, json={"inputs": text})
        if response.status_code == 200:
            return response.json()
        # model may be "cold starting" on HF's servers, wait and retry
        time.sleep(5)
    raise RuntimeError(f"Failed to get embedding after 3 attempts: {response.text}")


rows = []
with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Embedding {len(rows)} KB entries via HuggingFace Inference API...")
output = []
for row in rows:
    text = f"{row['title']}: {row['content']}"
    embedding = get_embedding(text)
    output.append({
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "embedding": embedding,
    })
    print(f"  embedded entry {row['id']}: {row['title']}")

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f)

print(f"Saved {len(output)} embeddings to {OUTPUT_JSON}")