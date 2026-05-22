# RAG 파이프라인

## 순서

1. `config/sources.yaml` — allowlist 확인
2. 문서 배치 → `data/sources/official/` (또는 허용 루트)
3. `python scripts/ingest_local.py` → `data/processed/ingest_manifest.jsonl`
4. (선택) `python scripts/ingest_web.py` — `web.enabled: true` 및 도메인·seed URL 설정 후
5. `python scripts/build_chunks.py` → `data/processed/chunks.jsonl`
6. `python scripts/build_index.py` → `data/index/` (Chroma)

FAQ 변경 시 3~6만 반복 (재학습 불필요).

## 청킹

- 약 450자, overlap 50자
- `verified: true` 만 인덱스

## 추론

- `RagRetriever` → top-k 청크
- `AnswerGenerator` → 프롬프트 + (선택) Qwen2.5-0.5B
- 모델 없음 → 검색 문단 bullet 반환
