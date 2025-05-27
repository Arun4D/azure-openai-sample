from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
import tika
from tika import parser
from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
import numpy as np
from transformers import pipeline

app = FastAPI()

# Initialize models
tika.initVM()
embedder = SentenceTransformer('all-MiniLM-L6-v2')
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Global storage (in-memory for demo)
documents = []
chunks = []
embeddings = []
faiss_index = None

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile):
    global faiss_index, documents, chunks, embeddings

    content = await file.read()
    parsed = parser.from_buffer(content)
    text = parsed['content']
    documents.append(text)

    # Simple chunking
    chunk_list = [text[i:i+1000] for i in range(0, len(text), 1000)]
    chunks.extend(chunk_list)

    # Compute embeddings
    chunk_embeds = embedder.encode(chunk_list)
    embeddings.extend(chunk_embeds)

    # Build/rebuild FAISS index
    dim = chunk_embeds[0].shape[0]
    faiss_index = faiss.IndexFlatL2(dim)
    faiss_index.add(np.array(embeddings))

    return {"message": f"Uploaded and processed {file.filename}, total chunks: {len(chunks)}"}

@app.post("/query/")
async def query_pdf(query: str = Form(...)):
    if not faiss_index:
        return JSONResponse({"error": "No documents uploaded yet."}, status_code=400)

    # Embed query
    query_embed = embedder.encode([query])

    # Retrieve top 5 chunks
    D, I = faiss_index.search(np.array(query_embed), k=5)
    top_chunks = [chunks[idx] for idx in I[0]]

    # Rerank
    pairs = [(query, chunk) for chunk in top_chunks]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, top_chunks), reverse=True)
    best_chunk = ranked[0][1]

    # Summarize
    summary = summarizer(best_chunk, max_length=150, min_length=50, do_sample=False)[0]['summary_text']

    return {"query": query, "summary": summary}

@app.get("/")
def root():
    return {"message": "Patient Care AI Service is running."}
