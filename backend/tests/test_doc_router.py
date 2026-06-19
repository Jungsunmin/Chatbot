"""doc_id 라우팅 단위 테스트."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.doc_router import resolve_doc_route


def test_alien_registration_documents():
    r = resolve_doc_route("외국인 등록에 필요한 서류가 무엇인지")
    assert r is not None
    assert r.doc_id == "alien-registration"


def test_address_change_not_registration():
    r = resolve_doc_route("체류지 변경 제출 서류")
    assert r is not None
    assert r.doc_id == "address-change-report"


def test_reissue_route():
    r = resolve_doc_route("외국인등록증 재발급 서류")
    assert r is not None
    assert r.doc_id == "alien-registration-card-reissue"


def test_registration_excludes_reissue():
    r = resolve_doc_route("외국인등록증 재발급")
    assert r is not None
    assert r.doc_id == "alien-registration-card-reissue"
