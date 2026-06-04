# 백엔드 구현 (Backend Implementation)

**범위**: KU RAG FAQ 챗봇 MVP — FastAPI + RAG 파이프라인 (Push/SSO 없음)  
**상태**: 기획 완료 · 구현 순서는 [task-breakdown.md](./task-breakdown.md)

---

## 기술 스택

| 계층 | 선택 |
|------|------|
| API | FastAPI, Pydantic v2, uvicorn |
| RAG | Chroma, sentence-transformers, HF transformers |
| LLM | Qwen2.5-1.5B-Instruct (기본), 4bit CUDA / MPS fp16 |
| 설정 | `backend/rag/config.py` + `.env` |

---

## 구현 순서

1. **인덱스** (T02–T03): frontmatter v2 → chunk → Chroma  
2. **Query** (T04–T07): detect, normalizer, intent, expander  
3. **검색** (T08–T09): search, rerank, band, context 선택  
4. **생성** (T10–T12): generator, safety, 고정 문구  
5. **API** (T13–T15): `/chat`, pending, CORS, health, reindex  

---

## 코딩 규칙

- 비즈니스 로직이 뻔하지 않으면 **한국어 주석**  
- 비밀은 코드에 넣지 않음; `.env`만 사용  
- 운영 환경에서 `message` 전문 로그 금지 (PII)  
- `/chat`이 `url_fetch` 등 외부 HTTP로 본문 fetch 하지 않음  
- 모듈 구조는 [architecture-planning.md](./architecture-planning.md) 따름  

---

## API 계약 (SSOT)

| 경로 | 메서드 | 비고 |
|------|--------|------|
| `/chat` | POST | `message`, `lang`, 선택 `confirm`, `pending_id` |
| `/health` | GET | `indexed_chunks` |
| `/admin/reindex` | POST | 개발/파일럿; 운영 시 보호 |

---

## Faithfulness 체크리스트 (생성 관련 PR마다)

- [ ] 프롬프트: context-only  
- [ ] `__UNKNOWN__` 처리  
- [ ] 수수료·기한·서류 목록 임의 생성 금지 (DR-1.5)  
- [ ] 청크에 `preserve_terms` 있으면 프롬프트에 반영  
- [ ] SensitiveTopic → 비단정 톤 + SafetyNotice  

---

## 검증 (백엔드)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/build_index.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
pytest tests/ -q
```

---

## 범위 외

- PostgreSQL, Redis (task 승인 시만)  
- OAuth, 운영 rate limit (Should)  
- 챗 경로에서 실시간 웹 ingest 자동화  

**프롬프트**: [implementation-prompt-writer.md](./implementation-prompt-writer.md)
