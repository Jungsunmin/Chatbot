# DECISIONS.md

확정된 결정만 기록. 최종 갱신: 2026-06-02

---

## 2026-06-02 - Agentic Skills 7–11 완료 (구현 전 기획 마감)

- **Decision**: `database-design`~(no SQL), `task-breakdown` T01–T20, `implementation-prompt-writer` 샘플, backend/frontend 구현 가이드, `test-strategy`, `code-review`, `security-privacy-review`, `deployment-operations`, `documentation-handoff` 작성 완료.
- **Reason**: 사용자 요청 — architecture 이후 Skill 일괄 산출.
- **Alternatives considered**: 구현과 병행하며 Skill 생략.
- **Impact**: [`skill-outputs/README.md`](./skill-outputs/README.md); 다음은 task별 Implementation Prompt 승인 + 코드.

---

## 2026-06-02 - Architecture Plan (MVP RAG pipeline)

- **Decision**: **3-tier** Expo → FastAPI → Query pipeline + Retrieval + Generation. **인덱스 = Korean curated md only** (AR-1, Domain v2). 검색: `langdetect` + `normalized_query_en` + `expanded_terms` → multilingual embed → Chroma → **heuristic rerank** → SelectedContext(≤4) → LLM. **무로그인**; **SQL 없음**; PendingSession in-memory TTL.
- **Reason**: Skill 6 `architecture-planning`; OPEN_QUESTIONS 해소(소스 전략, rerank, detect threshold).
- **Alternatives considered**: ko+en dual index; cross-encoder rerank; external LLM API.
- **Impact**: [`skill-outputs/architecture-planning.md`](./skill-outputs/architecture-planning.md); 구현 시 `backend/rag/{query,retrieval,generation}/` 분리 권장.

---

## 2026-06-02 - MVP 소스 전략 정합 (Architecture가 MoSCoW 보완)

- **Decision**: MVP 인덱스는 **한국어 human-curated `.md`만**. 영어/중/일 답변은 **answer-time LLM** + `preserve_terms`. Skill 4「ko+en dual md Must」는 **콘텐츠 작성 부담 절감**을 위해 Architecture에서 **Korean-only index**로 대체.
- **Reason**: Domain v2 + 운영 현실(공식 페이지가 한국어).
- **Alternatives considered**: Must마다 en md 병행 유지.
- **Impact**: `docs/RAG_SOURCES.md`·콘텐츠 runbook; 선택 en md는 Should.

---

## 2026-06-02 - Domain Model 보강 (English-first · Korean curated source)

- **Decision**: **LanguagePolicy** — `default_response_language=en`, `search_normalization_language=en`, `response_lang` = UI 선택 > detected > en. **RAG SSOT** = 공식 한국어 웹을 사람이 정리한 **한국어 `.md`** (`translation_strategy=answer_time_translation`). 답변 시 **preserve_terms** — English (한국어) 병기. 검색 파이프라인: Query → vector top-k → **RerankResult** → **SelectedContext** → LLM. **SensitiveTopic** + **SafetyNotice** / **SuggestedContact** 규칙 추가.
- **Reason**: Skill 5 보강 — 외국인 유학생 English-first, 공식 문서는 한국어 원천.
- **Alternatives considered**: MVP Must **ko+en dual md files** ([mvp-scope-planning](./skill-outputs/mvp-scope-planning.md)); 실시간 크롤.
- **Impact**: [`skill-outputs/domain-modeling.md`](./skill-outputs/domain-modeling.md) v2; Skill 4 MoSCoW **소스 전략**은 architecture/MVP 재정합 권장.

---

## 2026-06-02 - Domain Model (챗봇 · 초안)

- **Decision**: 핵심 개념 **SourceDocument → Chunk → Query/Retrieval → ChatResponse**. 무로그인, confirm, unknown, citation 유지.
- **Reason**: Skill 5 초안.
- **Impact**: superseded by English-first 보강 항목(위).

---

## 2026-06-02 - MVP Scope 확정 (MoSCoW · 챗봇 1.0)

- **Decision**: MVP 1.0 **Must** = RAG 챗 전 경로(FR-1~3, 5) + 4언어 UI/API + **소스 ko+en** 4섹션(Visa, Enrollment, Housing, Course). **zh/ja 소스** = Should. 풀앱·Push·지도·커뮤니티·SSO = Non-Scope/Could.
- **Reason**: Skill 4 `mvp-scope-planning` — 일정·번역 부담과 Skill 3 FR 정합.
- **Alternatives considered**: 4언어 소스 전부 Must; 영어만 Must.
- **Impact**: [`skill-outputs/mvp-scope-planning.md`](./skill-outputs/mvp-scope-planning.md), `context_packet` MVP, 구현·소스 우선순위.

---

## 2026-06-02 - Requirements Decomposition (챗봇 FR/NFR)

- **Decision**: 기능 요구사항을 **FR-1~6**(챗 API, 소스·인덱스, faithfulness, 4언어, Expo UI, 운영)으로 분해. 풀앱 FR(대시보드·Push·지도·커뮤니티)은 **Out of Scope** 표로 제외.
- **Reason**: Skill 3 `requirements-decomposition` — Skill 1·2 산출물 정합.
- **Alternatives considered**: 기존 7영역 풀앱 FR 표 유지.
- **Impact**: [`skill-outputs/requirements-decomposition.md`](./skill-outputs/requirements-decomposition.md); AC-1~7; 다음 `mvp-scope-planning`.

---

## 2026-06-02 - Stakeholder Analysis (챗봇·4언어)

- **Decision**: MVP 이해관계자를 **챗봇·RAG·소스·4언어(i18n)** 중심으로 정리. 풀앱 역할(커뮤니티·Push·지도·SSO)은 Non-Scope 표로 분리.
- **Reason**: Skill 2 `stakeholder-analysis` — Skill 1 챗봇 범위·**ko/en/zh/ja** 사용자 요청 반영.
- **Alternatives considered**: 기존 풀앱 이해관계자 표 유지.
- **Impact**: [`skill-outputs/stakeholder-analysis.md`](./skill-outputs/stakeholder-analysis.md); 다음 Skill `requirements-decomposition`.

---

## 2026-06-02 - 다국어 4개 (ko / en / zh / ja)

- **Decision**: 챗봇 **UI·질의·응답·소스** 대상 언어는 **한국어·영어·중국어·일본어**.
- **Reason**: 사용자 확정(기존 EN/ZH/JA 3언어 가정 대체).
- **Alternatives considered**: EN/ZH/JA만; 영어만 MVP.
- **Impact**: i18n·소스 `lang`·QA·번역 범위; `OPEN_QUESTIONS` 한국어 UI 항목 해소.

---

## 2026-06-02 - Service Goal 승인 (챗봇 범위)

- **Decision**: 서비스 목표를 KU **가이드북·FAQ 기반 RAG 챗봇**(출처 필수)으로 확정. **풀앱**(대시보드·Push·지도·커뮤니티)은 Non-Goals.
- **Reason**: Skill 1 `service-goal-definition` 사용자 승인 — 프로젝트 스코프는 **챗봇만**.
- **Alternatives considered**: 통합 유학생 앱(대시보드·Push·지도 포함)을 서비스 목표로 유지.
- **Impact**: 후속 Skill·MVP·구현은 챗봇·RAG·출처 UX 중심.

---

## 2026-06-02 - Skill 파일 평탄화

- **Decision**: Skill **절차**는 **`.cursor/skills/<skill-name>.md`** (폴더·`SKILL.md` 제거). 공통 계약은 **`skill-contract.md`** (루트).
- **Reason**: 탐색·경로 단순화.
- **Alternatives considered**: `*/SKILL.md` 폴더 구조 유지.
- **Impact**: AGENTS·rules·README 링크 갱신.

---

## 2026-06-02 - Skill 산출물 폴더 구조

- **Decision**: Skill **산출물**은 **`docs/agentic/skill-outputs/<skill-name>.md`** (스킬당 파일). 인덱스는 [`skill-outputs/README.md`](./skill-outputs/README.md).
- **Reason**: 단일 `skill_outputs.md` 대신 스킬별 파일로 탐색·갱신 단순화.
- **Alternatives considered**: `skill_outputs.md` 섹션 유지.
- **Impact**: skill-contract·AGENTS·각 Skill 절차 파일 경로 갱신.
