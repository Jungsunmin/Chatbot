"""source_loader 단위 테스트."""
from rag.source_loader import load_source_by_doc_id


def test_load_alien_registration_includes_key_sections():
    src = load_source_by_doc_id("alien-registration")
    assert src is not None
    assert src.doc_id == "alien-registration"
    assert "기본 제출서류" in src.body
    assert "신청 방법" in src.body
    assert src.title
