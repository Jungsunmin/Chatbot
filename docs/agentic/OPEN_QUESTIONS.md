# OPEN_QUESTIONS.md

미해결 질문. 최종 갱신: 2026-06-02

---

## P0 — domain-modeling 전에 필요

### 가이드북 MVP 섹션 (Must vs Should)

- **Must (Korean curated `.md`)**: Visa/Immigration, Enrollment, Housing, Course/Academic — 각 `doc_id` + `preserve_terms`
- **Should**: Welcome, Emergency
- **Could**: Academic Calendar 전체
- **Owner**: 기획·개발 · **근거**: [domain-modeling.md](./skill-outputs/domain-modeling.md), [mvp-scope-planning.md](./skill-outputs/mvp-scope-planning.md)

### ~~MoSCoW vs Domain Model — 소스 언어~~ → **해소 (Architecture AR-1)**

- **결정**: MVP 인덱스 = **Korean curated md only**; 다국어 답변 = answer-time + `preserve_terms`.
- **근거**: [architecture-planning.md](./skill-outputs/architecture-planning.md) AR-1, [DECISIONS.md](./DECISIONS.md)

### ~~대시보드 상태·MVP 인증~~ → **챗봇 MVP Non-Scope (보류)**

- 입학 전/재학/생활 홈, 로그인/SSO — **풀앱 2차**. 챗봇 MVP는 **무로그인 Must** ([mvp-scope-planning](./skill-outputs/mvp-scope-planning.md)).

---

## P1 — architecture·구현 전

### ~~4언어 우선순위·폴백~~ → **부분 해소 (Skill 5 보강)**

- **확정**: **English-first** — `default_response_language=en`; `response_lang` = UI > detected > en; **4언어 응답** 지원.
- **미정**: dual en md vs answer-time only — 위 **MoSCoW 정합** 항목 참고.
- **근거**: [domain-modeling.md](./skill-outputs/domain-modeling.md) LanguagePolicy

### ~~입력 언어 감지 confidence~~ → **해소 (Architecture AR-5)**

- **결정**: `langdetect`(동급); **confidence ≥ 0.70**일 때만 detected를 `response_lang` 후보로; UI `lang` 항상 우선.
- **근거**: [architecture-planning.md](./skill-outputs/architecture-planning.md)

### ~~Reranker 방식~~ → **해소 (Architecture AR-4)**

- **결정**: MVP **heuristic rerank** (distance + `expanded_terms` 매칭 + `document_list` 시 제출서류 boost). Cross-encoder = 1.x.
- **근거**: [architecture-planning.md](./skill-outputs/architecture-planning.md)

### `normalized_query_en` 구현 방식

- **Question**: 비영어 입력 시 검색 전용 en 변환 — **동일 1.5B 1-shot** vs **소형 번역 API** vs **multilingual embed only**(필드는 query 조합으로 대체)?
- **Owner**: 개발
- **Needed by**: `backend-implementation` (query_normalizer)
- **Impact**: 검색 recall vs 지연

### 소스·갱신 책임

- **Question**: `data/sources` **작성·갱신·reindex** 책임 — 개발 팀 단독 vs 국제처 제공·검수?
- **Owner**: 기획 + (추후) 국제처
- **Needed by**: `requirements-decomposition`, 운영 runbook
- **Impact if unresolved**: 소스 품질·공식성 리스크

### FAQ AI 스택

- **Question**: **FAQ-only** vs **온디바이스 RAG** vs **외부 API** — 학교·비용·개인정보 정책?
- **Owner**: 개발 + (추후) 국제처
- **Needed by**: FR-6 구현, security-privacy-review
- **Impact if unresolved**: 아키텍처·면책 문구

### 지도·길찾기 데이터

- **Question**: 건물 좌표·경로 **공식 데이터** 존재 여부? 없으면 OSM·수동·외부 맵 딥링크?
- **Owner**: 개발
- **Needed by**: FR-5 Should 일정
- **Impact if unresolved**: 지도 MVP 연기

### 공지·행사 피드

- **Question**: 알림 센터 공지 — **수동 입력** / **국제처 RSS·API** / **크롤링**?
- **Owner**: 기획·국제처(추후)
- **Needed by**: FR-7.4
- **Impact if unresolved**: 운영 부담·정확도

### 학사 일정 권위

- **Question**: 수강신청·비자 마감 **공식 일정표 URL/PDF** 단일 소스?
- **Owner**: 기획
- **Needed by**: FR-4
- **Impact if unresolved**: Push 신뢰도

---

## P2 — 2차 기능·운영

### 커뮤니티·룸메이트

- **Question**: 국적별 그룹 **실명/익명**, **신고·차단**, **매칭 알고리즘** 정책?
- **Owner**: 기획·법무(학교)
- **Needed by**: Could 단계 착수 전
- **Impact if unresolved**: 출시 불가·법적 리스크

### 국제처 공식 협업

- **Question**: 검수·로고·공식 링크 게시 **타임라인**?
- **Owner**: 국제처 + 팀
- **Needed by**: 스토어 공개·공식 홍보
- **Impact if unresolved**: 브랜드 리스크

### 레거시 RAG repo

- **Question**: `main` 브랜치 RAG 챗봇 코드 — **보관** / **별 repo** / **본 앱 FAQ에 통합**?
- **Owner**: 개발
- **Needed by**: FAQ 모듈 재사용 여부
- **Impact if unresolved**: 중복 개발

### Cursor status 규칙

- **Question**: `data/status.md` SSOT **복원** vs `docs/agentic`만 사용?
- **Owner**: 개발
- **Needed by**: Cursor rule 정리
- **Impact if unresolved**: 에이전트 규칙 충돌

---

## P3 — 성공 지표 수치

### 파일럿 KPI

- **Question**: SC-1~4의 **구체 수치**(예: 파일럿 n명, 완료율 x%)?
- **Owner**: 기획
- **Needed by**: 릴리스·데모
- **Impact if unresolved**: 성과 측정 어려움
