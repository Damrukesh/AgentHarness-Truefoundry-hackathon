"""
Retrieves the top-k most relevant KB entries for a given question, using
cosine similarity against embeddings from HuggingFace's Inference API.

Requires a free HF token: https://huggingface.co/settings/tokens
Set it as an environment variable: HF_TOKEN

Usage (CLI, for testing):
    python3 retrieve.py "why do retries duplicate my notifications?"

Usage (as a tool call, e.g. from TrueForge):
    python3 retrieve.py "<question>" --top_k 3
"""

import argparse
import json
import os
import time

import numpy as np
import requests

EMBEDDINGS_JSON = "skills/kb_embeddings.json"
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
        time.sleep(5)
    raise RuntimeError(f"Failed to get embedding after 3 attempts: {response.text}")


def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


parser = argparse.ArgumentParser()
parser.add_argument("question", type=str, help="The question to search the KB for")
parser.add_argument("--top_k", type=int, default=3, help="Number of results to return")
args = parser.parse_args()

with open(EMBEDDINGS_JSON, encoding="utf-8") as f:
    kb = json.load(f)

question_embedding = get_embedding(args.question)

scored = []
for entry in kb:
    score = cosine_similarity(question_embedding, entry["embedding"])
    scored.append({
        "id": entry["id"],
        "title": entry["title"],
        "content": entry["content"],
        "score": round(score, 4),
    })

scored.sort(key=lambda x: x["score"], reverse=True)
top_results = scored[: args.top_k]

print(json.dumps(top_results, indent=2))