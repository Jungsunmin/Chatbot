"""Streamlit 챗봇 UI — clarify 폼 + 출처 표시."""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dialog.manager import ChatSession, DialogManager


def _render_response(resp):
    if resp.type == "clarify":
        st.session_state.messages.append(
            {"role": "assistant", "content": resp.message or ""}
        )
        st.session_state.pending_fields = resp.fields
        st.rerun()
    elif resp.type == "answer":
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": resp.text or "",
                "citations": resp.citations,
            }
        )
        st.rerun()
    else:
        st.session_state.messages.append(
            {"role": "assistant", "content": resp.text or resp.message or ""}
        )
        st.rerun()


st.set_page_config(page_title="Exchange Student Chatbot", page_icon="🎓")
st.title("Exchange Student Guide Chatbot")
st.caption("RAG-only MVP · Official documents only")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "manager" not in st.session_state:
    st.session_state.manager = DialogManager()
if "chat_session" not in st.session_state:
    st.session_state.chat_session = ChatSession()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_fields" not in st.session_state:
    st.session_state.pending_fields = None

lang = st.sidebar.selectbox("Language / 언어", ["en", "ko"], index=0)
st.session_state.chat_session.lang = lang

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("citations"):
            with st.expander("Sources"):
                for c in msg["citations"]:
                    st.text(c.get("source_uri", ""))

if st.session_state.pending_fields:
    st.subheader("Additional information / 추가 정보")
    fields = st.session_state.pending_fields
    with st.form("slot_form"):
        values = {}
        for f in fields:
            name = f["name"]
            if f.get("type") == "enum" and f.get("options"):
                values[name] = st.selectbox(f["label"], f["options"])
            else:
                values[name] = st.text_input(f["label"])
        submitted = st.form_submit_button("Submit")
    if submitted:
        st.session_state.pending_fields = None
        resp = st.session_state.manager.handle(
            session=st.session_state.chat_session,
            slots_update=values,
        )
        _render_response(resp)

if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    resp = st.session_state.manager.handle(
        session=st.session_state.chat_session,
        message=prompt,
    )
    _render_response(resp)
