"""FastAPI — RAG 챗봇 API."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal

from pydantic import BaseModel, Field

from rag.generator import generate_answer
from rag.indexer import build_index
from rag.retriever import Retriever

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

retriever: Retriever | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global retriever
    count = build_index()
    logger.info("RAG index chunks: %s", count)
    retriever = Retriever()
    yield


app = FastAPI(title="KU International Student Chat API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    lang: Literal["en", "zh", "ja"] = "en"


class Citation(BaseModel):
    source_id: str
    title: str
    lang: str
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    model_used: bool


@app.get("/health")
def health():
    n = retriever._collection.count() if retriever else 0
    return {"status": "ok", "indexed_chunks": n}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if retriever is None:
        raise HTTPException(503, "Retriever not ready")
    docs = retriever.search(req.message)
    answer, model_used = generate_answer(req.message, docs, req.lang)
    citations = [
        Citation(
            source_id=d.source_id,
            title=d.title,
            lang=d.lang,
            excerpt=d.text[:300],
        )
        for d in docs
    ]
    return ChatResponse(answer=answer, citations=citations, model_used=model_used)


@app.post("/admin/reindex")
def reindex():
    """개발용: 인덱스 재구축."""
    n = build_index(force=True)
    return {"indexed_chunks": n}
