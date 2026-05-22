"""FastAPI 챗봇 API."""
from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.dialog.manager import ChatSession, DialogManager

app = FastAPI(title="Exchange Student Chatbot", version="0.1.0")
manager = DialogManager()
sessions: dict[str, ChatSession] = {}


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str | None = None
    lang: str = "en"
    slots: dict[str, Any] | None = None


class ChatResponseModel(BaseModel):
    session_id: str
    type: str
    message: str | None = None
    text: str | None = None
    fields: list[dict] | None = None
    citations: list[dict] | None = None
    category: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponseModel)
def chat(req: ChatRequest):
    sid = req.session_id or str(uuid.uuid4())
    if sid not in sessions:
        sessions[sid] = ChatSession(lang=req.lang)
    session = sessions[sid]
    if req.lang:
        session.lang = req.lang

    resp = manager.handle(
        session=session,
        message=req.message,
        slots_update=req.slots,
    )
    return ChatResponseModel(
        session_id=sid,
        type=resp.type,
        message=resp.message,
        text=resp.text,
        fields=resp.fields,
        citations=resp.citations,
        category=resp.category,
    )
