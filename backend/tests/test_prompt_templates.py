"""prompt_templates 단위 테스트."""
from rag.prompt_templates import build_system_prompt, build_user_prompt


def test_ko_user_prompt_has_section_labels():
    user = build_user_prompt("ko", "외국인 등록 서류", "문서 본문", "외국인 등록 안내")
    assert "신청 장소" in user
    assert "준비 서류" in user
    assert "절차" in user
    assert "주의사항" in user
    assert "다음 단계" in user
    assert "문서에서 확인되지 않습니다" in user
    assert "외국인 등록 안내" in user
    # 한국어 전용·형식 지시
    assert "한국어로만" in user
    assert "영어" in user and "넣지 마세요" in user
    assert "•" in user
    assert "질문:" in user


def test_en_user_prompt_has_section_labels():
    user = build_user_prompt("en", "What documents?", "body", "Alien Registration")
    assert "Where to apply" in user
    assert "Required documents" in user
    assert "Not confirmed in the document" in user
    assert "English only" in user


def test_system_prompt_ko_monolingual():
    system = build_system_prompt("ko")
    assert "한국어로만" in system
    assert "영어" in system
