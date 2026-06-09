"""FastAPI — RAG 챗봇 API (검색 → LLM RAG + confirm 턴)."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator

from rag.answer_composer import (
    compose_confirm_preview,
    confirm_prompt_text,
    unknown_message,
)
from rag.config import PRELOAD_MODELS
from rag.generator import generate_answer
from rag.indexer import build_index
from rag.model_loader import clear_models, get_model_and_tokenizer, is_ready as llm_is_ready
from rag.intent import classify_intent
from rag.pending_sessions import create as create_pending, pop as pop_pending
from rag.query_pipeline import build_query
from rag.retriever import Retriever
from rag.safety import safety_notice_for_docs
from rag.types import RetrievedDoc

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

retriever: Retriever | None = None

AnswerStatus = Literal["answered", "confirm_needed", "unknown"]


def _release_ml_resources() -> None:
    """종료 시 모델 참조·MPS 캐시 정리 (kill 시 semaphore 경고 완화)."""
    global retriever
    clear_models()
    if retriever is not None:
        retriever.shutdown()
    try:
        import torch

        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    except Exception as e:
        logger.debug("MPS cache clear skipped: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global retriever
    count = build_index()
    logger.info("RAG index chunks: %s", count)
    retriever = Retriever()

    if PRELOAD_MODELS:
        logger.info("모델 preload 시작 (임베딩 → LLM, 첫 실행은 수 분 걸릴 수 있음)")
        retriever.warmup()
        get_model_and_tokenizer()
        logger.info("모델 preload 완료 — /chat 요청 가능")

    try:
        yield
    finally:
        logger.info("서버 종료 — ML 리소스 정리 중")
        _release_ml_resources()


app = FastAPI(title="KU International Student Chat API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(default="", max_length=2000)
    lang: Literal["ko", "en", "zh", "ja"] = "ko"
    confirm: Literal["yes", "no"] | None = None
    pending_id: str | None = None

    @model_validator(mode="after")
    def require_message_on_first_turn(self):
        if self.confirm is None and not self.message.strip():
            raise ValueError("message is required on first turn")
        if self.confirm is not None and not self.pending_id:
            raise ValueError("pending_id is required when confirm is set")
        return self


class Citation(BaseModel):
    source_id: str
    title: str
    lang: str
    excerpt: str
    source_url: str = ""
    label: str = ""
    doc_type: str = ""


class ChatResponse(BaseModel):
    status: AnswerStatus
    answer: str
    citations: list[Citation]
    model_used: bool = False
    pending_id: str | None = None
    confirm_prompt: str | None = None
    safety_notice: str | None = None


def _to_citations(docs: list[RetrievedDoc]) -> list[Citation]:
    """source_url 기준 중복 제거 — 참고 링크 1개."""
    seen_urls: set[str] = set()
    out: list[Citation] = []
    for d in docs:
        url_key = d.source_url or d.source_id
        if url_key in seen_urls:
            continue
        seen_urls.add(url_key)
        out.append(
            Citation(
                source_id=d.source_id,
                title=d.title,
                lang=d.lang,
                excerpt=d.text[:300],
                source_url=d.source_url,
                label=d.label,
                doc_type=d.doc_type,
            )
        )
    return out


def _unknown_response(lang: str) -> ChatResponse:
    return ChatResponse(
        status="unknown",
        answer=unknown_message(lang),
        citations=[],
        model_used=False,
    )


@app.get("/health")
def health():
    n = retriever._collection.count() if retriever else 0
    embedder_ready = retriever.embedder_is_ready() if retriever else False
    llm_ready = llm_is_ready()
    return {
        "status": "ok",
        "indexed_chunks": n,
        "embedder_ready": embedder_ready,
        "llm_ready": llm_ready,
        "models_ready": embedder_ready and llm_ready,
        "preload_enabled": PRELOAD_MODELS,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if retriever is None:
        raise HTTPException(503, "Retriever not ready")

    if req.confirm is not None:
        session = pop_pending(req.pending_id or "")
        if session is None:
            raise HTTPException(404, "pending session expired or not found")
        if req.confirm == "no":
            return _unknown_response(session.lang)
        answer, used_docs, model_used = _build_answer(
            session.docs, session.lang, session.query, user_confirmed=True
        )
        if answer == unknown_message(session.lang):
            return _unknown_response(session.lang)
        return ChatResponse(
            status="answered",
            answer=answer,
            citations=_to_citations(used_docs or session.docs),
            model_used=model_used,
        )

    q = build_query(req.message.strip(), req.lang)
    retrieval = retriever.search_with_band(q)
    response_lang = q.response_lang
    notice = safety_notice_for_docs(response_lang, retrieval.docs)

    if retrieval.band in ("none", "low") or not retrieval.docs:
        return _unknown_response(response_lang)

    if retrieval.band == "high":
        answer, used_docs, model_used = _build_answer(
            retrieval.docs, response_lang, q.message
        )
        if answer == unknown_message(response_lang):
            return _unknown_response(response_lang)
        return ChatResponse(
            status="answered",
            answer=answer,
            citations=_to_citations(used_docs or retrieval.docs),
            model_used=model_used,
            safety_notice=notice,
        )

    pending_id = create_pending(q.message, response_lang, retrieval.docs)
    preview = compose_confirm_preview(retrieval.docs, response_lang)
    prompt = confirm_prompt_text(response_lang)
    return ChatResponse(
        status="confirm_needed",
        answer=preview,
        citations=_to_citations(retrieval.docs[:1]),
        pending_id=pending_id,
        confirm_prompt=prompt,
        model_used=False,
        safety_notice=notice,
    )


def _build_answer(
    docs: list[RetrievedDoc],
    lang: str,
    query: str = "",
    user_confirmed: bool = False,
) -> tuple[str, list[RetrievedDoc], bool]:
    """(answer_text, citations용 청크, model_used). intent는 검색에만 쓰고 답은 통합 LLM."""
    intent = classify_intent(query)
    answer, model_used = generate_answer(
        query, docs, lang, intent=intent, user_confirmed=user_confirmed
    )
    if answer == unknown_message(lang):
        return answer, [], model_used

    return answer, docs, model_used


@app.post("/admin/reindex")
def reindex():
    """개발용: 인덱스 재구축."""
    n = build_index(force=True)
    return {"indexed_chunks": n}
