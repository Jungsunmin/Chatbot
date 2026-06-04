# RAG 소스 (Visa Phase 1)

## 경로

- **SSOT**: `backend/data/sources/**/*.md`
- **Visa (현재)**: `backend/data/sources/visa/*_ko.md` (10문서)
- **메모**: `docs/sources-notes/konkuk_visa_README.md` (인덱싱 제외)
- **인덱스 산출물**: `backend/data/index/` (git 제외)

## frontmatter v2 (필수)

`doc_id`, `source_url`, `source_title`, `source_language`, `curated_language`, `category`, `sensitive_topic`, `updated_at`, `curation_status`, `translation_strategy`

권장: `preserve_terms[]`, `preserve_korean_terms`

## 인덱스 구축

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/build_index.py
# force: python scripts/build_index.py --force
```

## API 확인

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
curl -s http://127.0.0.1:8001/health
```

## 갱신 절차

1. `backend/data/sources/visa/` md 수정
2. `python scripts/build_index.py --force` 또는 `POST /admin/reindex`
3. `GET /health`로 `indexed_chunks` 확인
4. 샘플 `/chat` 질의로 답변·citation 확인

## Phase 2

`enrollment/`, `housing/`, `course/` 카테고리 md 추가 후 동일 절차 reindex.
