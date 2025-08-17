import os, json, numpy as np
import typer, pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import faiss

app = typer.Typer()
load_dotenv()

mongo = MongoClient(os.getenv("MONGO_URI"))
mdb = mongo[os.getenv("MONGO_DB")]

# Lazy-load model globally
_model = None
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(os.getenv("EMBEDDING_MODEL","all-MiniLM-L6-v2"))
    return _model

@app.command()
def chunk_docs(limit: int = 20):
    """Convert documents.content_text into chunks (if not chunked yet)."""
    docs = mdb.documents.find({"content_text": {"$exists": True}}).limit(limit)
    for d in docs:
        text = d["content_text"]
        # naive chunker
        parts = [p.strip() for p in text.split(". ") if p.strip()]
        window = 5
        out = []
        for i in range(0, len(parts), window):
            chunk = ". ".join(parts[i:i+window])
            out.append({
                "doc_id": d["doc_id"],
                "chunk_id": f"{d['doc_id']}#{i//window:02d}",
                "chunk_index": i//window,
                "text": chunk,
                "tokens": len(chunk.split()),
                "meta": {"type": d.get("type"), "order_id": d.get("order_id")},
                "_schemaVersion": 1
            })
        if out:
            mdb.chunks.insert_many(out)
    typer.echo("Chunking done.")

@app.command()
def embed_chunks():
    """Create embeddings for chunks and save metadata to Mongo; persist FAISS index to disk."""
    model = get_model()
    chunks = list(mdb.chunks.find({}))
    if not chunks:
        typer.echo("No chunks to embed.")
        raise typer.Exit()

    texts = [c["text"] for c in chunks]
    vecs = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    dim = vecs.shape[1]

    # Save (optional) vectors in Mongo if you want
    # (for Atlas Vector Search, you'd store vectors there)
    emb_col = mdb.embeddings
    emb_col.delete_many({})
    emb_docs = [{
        "chunk_id": c["chunk_id"],
        "vector": vecs[i].tolist(),  # omit if using FAISS-only
        "dim": int(dim),
        "meta": c["meta"]
    } for i,c in enumerate(chunks)]
    emb_col.insert_many(emb_docs)

    # Build FAISS index
    index = faiss.IndexFlatIP(dim)  # using cosine via normalized vectors
    index.add(vecs.astype('float32'))
    faiss.write_index(index, "data/processed/faiss.index")

    # Map FAISS ids -> chunk_ids
    with open("data/processed/faiss_ids.json","w") as f:
        json.dump([c["chunk_id"] for c in chunks], f)

    typer.echo(f"Embedded {len(chunks)} chunks, dim={dim}.")

if __name__ == "__main__":
    app()
