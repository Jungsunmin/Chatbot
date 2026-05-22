# 프로젝트 진행 현황

교환학생·유학생 학교 안내 **RAG 챗봇** (외부 LLM API 없음, LoRA 보류)

**최종 갱신**: 2026-05-22

> 이 파일(`data/status.md`)이 프로젝트 상태의 **단일 기준(SSOT)** 입니다.  
> 에이전트·개발자는 작업 전에 반드시 읽고, 코드·설정 변경 시 **즉시** 이 파일을 갱신합니다.

---

## 1. 현재 진행 사항 (완료)

### 1.1 아키텍처·기능

| 항목 | 상태 | 비고 |
|------|------|------|
| RAG-only MVP | 완료 | LoRA 파인튜닝은 범위 외 |
| allowlist 로컬 수집 | 완료 | `config/sources.yaml` + `ingest_local.py` |
| allowlist 웹 수집 (선택) | 완료 | `ingest_web.py` — `web.enabled: false` 기본 |
| 청킹·Chroma 인덱스 | 완료 | `build_chunks.py`, `build_index.py` |
| 멀티턴 clarify (슬롯 폼) | 완료 | `data/schemas/` 3카테고리 |
| RAG 검색 + 답 생성 | 완료 | `retriever.py`, `generator.py` (Qwen2.5-0.5B) |
| FastAPI `/chat` | 완료 | `clarify` / `answer` / `fallback` |
| Streamlit UI | 완료 | 채팅 + 폼 + 출처(citations) |
| 로컬 검증 | 완료 | 샘플 문서 2건 인덱스·대화 테스트 |
| GitHub | 완료 | https://github.com/Jungsunmin/Chatbot |
| `data/status.md` + Cursor rule | 완료 | 작업 전 읽기·변경 시 즉시 반영 규칙 |

### 1.2 저장소 구조

```
Chatbot/
├── data/status.md           # ← 진행 현황 SSOT (이 파일)
├── config/sources.yaml
├── data/sources/official/
├── data/schemas/
├── scripts/
├── src/
├── app/streamlit_app.py
└── docs/
```

### 1.3 참고 문서

| 파일 | 내용 |
|------|------|
| [README.md](../README.md) | 빠른 시작 |
| [docs/RAG_PIPELINE.md](../docs/RAG_PIPELINE.md) | 인덱스 파이프라인 |
| [docs/SOURCE_ALLOWLIST.md](../docs/SOURCE_ALLOWLIST.md) | 폴더·도메인 제한 |
| [docs/SERVER_DEPLOY.md](../docs/SERVER_DEPLOY.md) | 학교 서버 배포 |
| [docs/SLOT_SCHEMAS.md](../docs/SLOT_SCHEMAS.md) | clarify 스키마 |
| [docs/EVAL_CHECKLIST.md](../docs/EVAL_CHECKLIST.md) | RAG 품질 평가 |

### 1.4 아직 비어 있거나 placeholder

- `config/sources.yaml` — **학교 폴더 경로·URL** (팀 입력 예정)
- `data/sources/international_office/` — 폴더 미생성
- 실제 학교 FAQ PDF/대량 문서 — **팀 제공 예정**

---

## 2. 추후 해야 할 사항

### 2.1 우선순위 높음 (운영 전 필수)

- [ ] **`config/sources.yaml` 작성** — `allowed_roots`, `allowed_domains`, `seed_urls`
- [ ] **공식 문서 업로드** — allowlist 폴더
- [ ] (권장) **`data/sources/manifest.csv`**
- [ ] **학교 서버 배포** — [SERVER_DEPLOY.md](../docs/SERVER_DEPLOY.md)
- [ ] **재인덱스 절차** 문서화·실습
- [ ] **EVAL_CHECKLIST** 실행

### 2.2 품질·기능 개선

- [ ] FAQ 청크 80~150+
- [ ] `intent_rules.py` 보강
- [ ] 슬롯 스키마 추가 카테고리
- [ ] retrieval threshold·BM25 hybrid
- [ ] overlap 검증 → fallback
- [ ] 연락처·URL 템플릿 변수화

### 2.3 인프라·협업

- [ ] 팀 collaborator · PR 규칙
- [ ] 서버 index/모델 캐시 운영
- [ ] systemd/docker (필요 시)
- [ ] 다국어 (`lang: zh` 등)

### 2.4 보류 (RAG 검증 후)

- [ ] LoRA 파인튜닝
- [ ] clarify LM 생성

---

## 3. 실행 명령 요약

```bash
python scripts/ingest_local.py
python scripts/build_chunks.py
python scripts/build_index.py
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
streamlit run app/streamlit_app.py
```

---

## 4. 의사결정 기록

| 결정 | 내용 |
|------|------|
| 상태 문서 | **`data/status.md`** SSOT |
| 생성 | decoder-only + RAG |
| 학습 | MVP 인덱스만; LoRA 보류 |
| 검색 | allowlist만 |
| 대화 | clarify → RAG → 답변 |

---

## 5. 변경 이력

| 날짜 | 변경 요약 |
|------|-----------|
| 2026-05-22 | RAG MVP 초기 구현, GitHub push, `docs/PROJECT_STATUS.md` 작성 |
| 2026-05-22 | `data/status.md` SSOT화, `.cursor/rules/chatbot-status.mdc` 추가 (작업 전 읽기·변경 즉시 반영) |

---

## 6. 다음 스프린트

1. `sources.yaml` · 문서 폴더 확정  
2. 문서 ingest/index  
3. EVAL_CHECKLIST 데모  
4. PR 시 `data/status.md` 갱신 포함  
