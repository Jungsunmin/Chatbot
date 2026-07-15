"""source_loader 단위 테스트."""
from rag.source_loader import load_source_by_doc_id


def test_load_alien_registration_includes_key_sections():
    src = load_source_by_doc_id("stay-visa-alien-registration-card")
    assert src is not None
    assert src.doc_id == "stay-visa-alien-registration-card"
    assert "Required Documents" in src.body
    assert "Application Method" in src.body
    assert src.title
