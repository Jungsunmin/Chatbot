"""검색 라우팅·document_list 좁히기 통합 테스트 (Chroma 인덱스 필요)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.query_pipeline import build_query
from rag.retriever import Retriever


def test_registration_documents_retrieves_correct_doc():
    retriever = Retriever()
    if retriever._collection.count() == 0:
        return

    q = build_query("외국인 등록에 필요한 서류가 무엇인지", "ko")
    res = retriever.search_with_band(q)
    assert res.docs, "검색 결과가 있어야 함"
    top = res.docs[0]
    assert top.doc_id == "stay-visa-alien-registration-card"
    assert "Required Document" in (top.section_title or "") or "Alien Registration Application Form" in top.text


def test_address_change_query_same_merged_doc():
    """주소 변경 신고는 외국인등록 문서에 병합돼 동일 doc_id로 라우팅됨."""
    retriever = Retriever()
    if retriever._collection.count() == 0:
        return

    q = build_query("체류지 변경할 때 필요한 서류", "ko")
    res = retriever.search_with_band(q)
    assert res.docs
    assert res.docs[0].doc_id == "stay-visa-alien-registration-card"
