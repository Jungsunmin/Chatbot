# 구현 프롬프트 작성 (Implementation Prompt Writer)

**용도**: [task-breakdown.md](./task-breakdown.md)의 각 ID마다 **한 번에 한 task**만 구현. 승인 후 코딩.

---

## 프롬프트 목록

| Task ID | 제목 | 상태 |
|---------|------|------|
| [T03](#prompt-t03-index-health) | 인덱스 구축 및 health | 준비됨 |
| [T07–T09](#prompt-t07-t09-retrieval-spine) | Query + 검색 파이프라인 | 준비됨 |
| [T13](#prompt-t13-chat-api) | `/chat` API E2E | 준비됨 |
| T01 | 한국어 md 콘텐츠 | 콘텐츠 팀 |
| T16 | Expo 챗 UI | T13 이후 |

---

## 프롬프트: T03 — 인덱스 및 health

### 목표

한국어 md 소스를 Chroma에 인덱싱하고 `/health`·`build_index`로 청크 수를 확인한다.

### 맥락

- 브랜치: `feat/initial-ui-chatbot`
- [database-design.md](./database-design.md), [architecture-planning.md](./architecture-planning.md)
- 경로: `backend/data/sources/`, `backend/data/index/`

### 파일

- 생성·수정: `backend/rag/frontmatter.py`, `chunking.py`, `indexer.py`, `scripts/build_index.py`, `backend/app/main.py` (`/health`)
- 문서: `docs/RAG_SOURCES.md` (누락 섹션 시)

### 제약

- 인덱서에서 실시간 URL fetch 금지
- frontmatter v2 필드는 Chroma 메타데이터에 저장
- Non-Scope: query 파이프라인, LLM

### 인터페이스

- `GET /health` → `{ "status": "ok", "indexed_chunks": number }`
- CLI: `python scripts/build_index.py` 실행 시 청크 수 출력

### 완료 기준

- 한국어 md ≥1건 인덱싱; `indexed_chunks` > 0
- force reindex 시 컬렉션 교체

### 검증

```bash
cd backend && source .venv/bin/activate
python scripts/build_index.py
curl -s http://127.0.0.1:8001/health
```

---

## 프롬프트: T07–T09 — 검색 파이프라인

### 목표

`Query` → embed(`normalized_query_en` + `expanded_terms`) → Chroma top-k → 휴리스틱 rerank → `SelectedContext` + `RelevanceBand`.

### 맥락

- 선행: T03
- [domain-modeling.md](./domain-modeling.md) 검색 흐름

### 파일

- `backend/rag/query/` (detect, normalizer, intent, expander, builder)
- `backend/rag/retrieval/` (embedder, chroma, rerank, banding, selector)
- `backend/rag/types.py`, `config.py` (`LANG_DETECT_MIN_CONFIDENCE=0.7`)

### 제약

- 검색 경로에 LLM 없음 (normalizer만 별도 소형 호출 가능 — PR에 명시)
- `document_list`: `제출서류` 포함 청크 가중
- low band → 사용 가능 청크 없음

### 인터페이스

```python
def build_query(message: str, ui_lang: str) -> Query: ...
def retrieve(query: Query) -> RetrievalResult: ...
```

### 완료 기준

- 영어 질문 시 한국어 비자 청크가 top-4에 포함
- 무관 질문 → band low/none

### 검증

```bash
cd backend && pytest tests/ -k retrieval -q
```

---

## 프롬프트: T13 — Chat API

### 목표

`POST /chat`이 initial·confirm을 지원하고 `answered` | `confirm_needed` | `unknown` + citations를 반환한다.

### 맥락

- 선행: T07–T12
- [requirements-decomposition.md](./requirements-decomposition.md) FR-1

### 파일

- `backend/app/main.py`
- `backend/rag/generation/generator.py`, `session/pending_sessions.py`, `answer_composer.py`

### 제약

- 익명; 챗 기록 서버 저장 없음
- faithfulness: context 비면 unknown
- citation은 `source_url` 기준 dedupe

### 인터페이스

[architecture-planning.md](./architecture-planning.md) API 절 참고.

### 완료 기준

- curl initial → answered + citations (high band 샘플)
- medium band → confirm → yes → answered
- confirm no → unknown

### 검증

```bash
uvicorn app.main:app --port 8001
curl -X POST http://127.0.0.1:8001/chat -H 'Content-Type: application/json' \
  -d '{"message":"What documents for alien registration?","lang":"en"}'
```

---

## 규칙

- PR당 승인된 프롬프트 하나
- 범위 확대 → 새 task ID + 새 프롬프트
- 동작·정책 변경 시에만 `DECISIONS.md` 갱신
