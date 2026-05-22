# 프로젝트 진행 현황

교환학생·유학생 학교 안내 **RAG 챗봇** (외부 LLM API 없음, LoRA 보류)

**최종 갱신**: 2026-05-22

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

### 1.2 저장소 구조

```
Chatbot/
├── config/sources.yaml      # 허용 폴더·URL (팀이 추후 채움)
├── data/sources/official/   # 팀 제공 문서
├── data/schemas/            # 슬롯·clarify YAML
├── scripts/                 # ingest → chunks → index
├── src/dialog|rag|inference|api/
├── app/streamlit_app.py
└── docs/                    # 운영·배포 가이드
```

### 1.3 문서

| 파일 | 내용 |
|------|------|
| [README.md](../README.md) | 빠른 시작 |
| [RAG_PIPELINE.md](RAG_PIPELINE.md) | 인덱스 파이프라인 |
| [SOURCE_ALLOWLIST.md](SOURCE_ALLOWLIST.md) | 폴더·도메인 제한 |
| [SERVER_DEPLOY.md](SERVER_DEPLOY.md) | 학교 서버 배포 |
| [SLOT_SCHEMAS.md](SLOT_SCHEMAS.md) | clarify 스키마 |
| [EVAL_CHECKLIST.md](EVAL_CHECKLIST.md) | RAG 품질 평가 |

### 1.4 아직 비어 있거나 placeholder

- `config/sources.yaml` — **학교 폴더 경로·URL** (팀 입력 예정)
- `data/sources/international_office/` — 폴더 미생성 (설정만 존재)
- 실제 학교 FAQ PDF/대량 문서 — **팀 제공 예정** (샘플 md 2개만 포함)
- GitHub remote — 첫 push 시 연결

---

## 2. 추후 해야 할 사항

### 2.1 우선순위 높음 (운영 전 필수)

- [ ] **`config/sources.yaml` 작성** — `allowed_roots`, 필요 시 `allowed_domains`, `seed_urls`
- [ ] **공식 문서 업로드** — allowlist 폴더에 PDF/md 등 배치
- [ ] (권장) **`data/sources/manifest.csv`** — 파일별 `category`, `lang`, `verified`
- [ ] **학교 서버 배포** — clone → venv → ingest → index → API/Streamlit ([SERVER_DEPLOY.md](SERVER_DEPLOY.md))
- [ ] **재인덱스 절차** — 문서 변경 시 `ingest_local` → `build_chunks` → `build_index`
- [ ] **EVAL_CHECKLIST** — 테스트 질문 10~50개로 환각·사실 오류 점검

### 2.2 품질·기능 개선

- [ ] FAQ 청크 확장 (목표 80~150+ verified chunks)
- [ ] `intent_rules.py` 키워드 보강 또는 소형 의도 분류기
- [ ] 슬롯 스키마 추가 카테고리 (`arrival_orientation`, `health_insurance` 등)
- [ ] retrieval score threshold·BM25 hybrid 튜닝
- [ ] 생성 답 ↔ 청크 overlap 검증 강화 → fallback
- [ ] 연락처·URL 템플릿 변수화 (`{{intl_office_phone}}`)

### 2.3 인프라·협업

- [ ] GitHub 저장소 remote 연결 및 팀 collaborator
- [ ] `data/index/`, Hugging Face 모델 캐시 — 서버 로컬만 (Release/tarball 선택)
- [ ] systemd/docker로 API·Streamlit 상시 실행 (필요 시)
- [ ] 다국어 확장 (`lang: zh` 등) — 동일 allowlist·인덱스 파이프라인

### 2.4 보류 (RAG 검증 후)

- [ ] **LoRA 파인튜닝** — 말투·지시 따름만; 지식은 RAG 유지
- [ ] clarify 문구 LM 생성 (현재 YAML 고정이 SSOT)

---

## 3. 실행 명령 요약

```bash
# 문서 반영 후 (서버·로컬 공통)
python scripts/ingest_local.py
python scripts/build_chunks.py
python scripts/build_index.py

# 서비스
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
streamlit run app/streamlit_app.py
```

---

## 4. 의사결정 기록

| 결정 | 내용 |
|------|------|
| 생성 방식 | decoder-only + **RAG** (mT5 seq2seq 미사용) |
| 학습 | MVP는 **인덱스만**; LoRA 보류 |
| 검색 범위 | **allowlist** 폴더·도메인만 |
| 대화 | 슬롯 **clarify** 후 답변 |
| 언어 | 1차 한·영, 다국어는 코퍼스 확장 후 재인덱스 |

---

## 5. 담당자 체크리스트 (다음 스프린트)

1. 학교 URL·문서 폴더 확정 → `sources.yaml` 업데이트  
2. 문서 제출 → 서버에 복사 → ingest/index  
3. 국제처·팀 내부 데모 → EVAL_CHECKLIST  
4. 이슈·PR로 FAQ diff 관리  

문의·수정 제안은 GitHub Issues 또는 팀 채널로 정리하면 됩니다.
