"""전문(verbatim) 답변 추출 단위 테스트."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.intent import classify_intent
from rag.section_matcher import select_docs_for_intent
from rag.types import RetrievedDoc
from rag.verbatim_composer import compose_verbatim_answer, extract_content_lines

_ALIEN_REG_DOCS = """- 외국인등록신청서
- 여권
- 여권 인적면 및 비자면 사본 각 1부
- 사진 1매: 3.5cm x 4.5cm, 6개월 이내 촬영
- 재학증명서 또는 등록금 납입 증명서
- 체류지 입증 서류: 계약서, 거주확인서, 기숙사 입주 확인증 등
- 발급수수료: 35,000원"""


def _doc(text: str, section: str = "기본 제출서류", title: str = "외국인 등록 안내") -> RetrievedDoc:
    return RetrievedDoc(
        text=text,
        source_id="visa/alien-registration_ko.md",
        title=title,
        lang="ko",
        distance=0.2,
        section_title=section,
        doc_id="alien-registration",
    )


def test_extract_document_list_excludes_fee():
    lines = extract_content_lines(_ALIEN_REG_DOCS, "document_list")
    assert len(lines) == 6
    assert "외국인등록신청서" in lines[0]
    assert "재학증명서 또는 등록금 납입 증명서" in lines
    assert not any("수수료" in ln for ln in lines)


def test_compose_alien_registration_full_list():
    docs = [_doc(_ALIEN_REG_DOCS)]
    answer = compose_verbatim_answer(docs, "document_list", "ko")
    assert answer is not None
    assert "외국인등록신청서" in answer
    assert "여권 인적면 및 비자면 사본 각 1부" in answer
    assert "사진 1매" in answer
    assert "재학증명서 또는 등록금 납입 증명서" in answer
    assert "체류지 입증 서류" in answer
    assert "35,000원" not in answer
    assert "출처: 외국인 등록 안내" in answer


def test_select_document_section_over_other():
    reg = _doc(_ALIEN_REG_DOCS, section="기본 제출서류")
    other = RetrievedDoc(
        text="- 신고서\n- 여권\n- 외국인등록증",
        source_id="visa/address-change-report_ko.md",
        title="체류지 변경 신청",
        lang="ko",
        distance=0.1,
        section_title="제출서류",
        doc_id="address-change-report",
    )
    selected = select_docs_for_intent([other, reg], "document_list")
    assert selected[0].doc_id == "alien-registration"


def test_procedure_verbatim():
    text = "- 개인이 출입국사무소에 방문하여 직접 신청\n- 학교 협력 업체를 통한 단체 신청 가능"
    docs = [_doc(text, section="신청 방법")]
    answer = compose_verbatim_answer(docs, "procedure", "ko")
    assert answer is not None
    assert "출입국사무소" in answer
    assert "단체 신청" in answer


def test_intent_classify_registration_documents():
    assert classify_intent("외국인 등록에 필요한 서류가 무엇인지") == "document_list"
