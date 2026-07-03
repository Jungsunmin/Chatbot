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


def test_alien_registration_english_routes_to_english_doc():
    r = resolve_doc_route("What documents are required for alien registration", "en")
    assert r is not None
    assert r.doc_id == "stay-visa-alien-registration-card"


def test_alien_registration_default_lang_still_korean():
    r = resolve_doc_route("외국인 등록에 필요한 서류가 무엇인지")
    assert r is not None
    assert r.doc_id == "alien-registration"


def test_dormitory_application_routes_english_only_doc():
    r = resolve_doc_route("What documents do I need for dormitory application?", "en")
    assert r is not None
    assert r.doc_id == "dormitory-application"


def test_dormitory_application_falls_back_when_no_korean_variant():
    r = resolve_doc_route("기숙사 신청 서류")
    assert r is not None
    assert r.doc_id == "dormitory-application"


def test_health_insurance_routes_english_only_doc():
    r = resolve_doc_route("How do I apply for national health insurance?", "en")
    assert r is not None
    assert r.doc_id == "health-insurance-for-international-students"
