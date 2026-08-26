"""
Retrieves the top-k most relevant KB entries for a given question, using
fastembed (ONNX-based local embeddings) + cosine similarity.

Usage (CLI, for testing):
    python3 retrieve.py "why do retries duplicate my notifications?"

Usage (as a tool call, e.g. from TrueForge):
    python3 retrieve.py "<question>" --top_k 3
"""

import argparse
import json

import numpy as np
from fastembed import TextEmbedding

EMBEDDINGS_JSON = "skills/kb_embeddings.json"
MODEL_NAME = "BAAI/bge-small-en-v1.5"


def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


parser = argparse.ArgumentParser()
parser.add_argument("question", type=str, help="The question to search the KB for")
parser.add_argument("--top_k", type=int, default=3, help="Number of results to return")
args = parser.parse_args()

with open(EMBEDDINGS_JSON, encoding="utf-8") as f:
    kb = json.load(f)

model = TextEmbedding(model_name=MODEL_NAME)
question_embedding = list(model.embed([args.question]))[0].tolist()

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