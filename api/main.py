import json, numpy as np
from fastapi import FastAPI, Query
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import faiss, os

load_dotenv()
app = FastAPI(title="Order Intelligence RAG API")

# Mongo
mongo = MongoClient(os.getenv("MONGO_URI"))
mdb = mongo[os.getenv("MONGO_DB")]

# Model + index
model = SentenceTransformer(os.getenv("EMBEDDING_MODEL","all-MiniLM-L6-v2"))
index = faiss.read_index("data/processed/faiss.index")
with open("data/processed/faiss_ids.json") as f:
    id_map = json.load(f)

class SearchResponse(BaseModel):
    query: str
    top_k: int
    results: list

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/search", response_model=SearchResponse)
def search(q: str = Query(...), k: int = 5):
    vec = model.encode([q], convert_to_numpy=True, normalize_embeddings=True).astype('float32')
    scores, idxs = index.search(vec, k)
    idxs = idxs[0].tolist()
    scores = scores[0].tolist()
    chunks = []
    for rank, (i, s) in enumerate(zip(idxs, scores)):
        if i == -1: continue
        chunk_id = id_map[i]
        c = mdb.chunks.find_one({"chunk_id": chunk_id}, {"_id":0})
        if c:
            c["score"] = float(s)
            chunks.append(c)
    return {"query": q, "top_k": k, "results": chunks}
