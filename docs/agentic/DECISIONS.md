# DECISIONS.md

확정된 결정만 기록. 최종 갱신: 2026-05-26

---

## 2026-05-26 - 대상 기관·사용자

- **Decision**: **건국대학교(KU) 외국인 유학생** 전용 앱. 학부·대학원·어학당·교환 포함.
- **Reason**: 사용자 기획 및 벤치마크(건국대 앱·가이드북) 명시.
- **Alternatives considered**: 타교 공통 앱, 교환학생만 대상.
- **Impact**: 콘텐츠·일정·지도·브랜딩 모두 KU 기준.

---

## 2026-05-26 - 플랫폼

- **Decision**: **iOS + Android** 동시 지원.
- **Reason**: 유학생 단말기 분산, Push·앱스토어 배포 필요.
- **Alternatives considered**: PWA만, 단일 OS 우선.
- **Impact**: 크로스플랫폼(Flutter/React Native 등) 또는 이중 네이티브 검토.

---

## 2026-05-26 - UI 언어

- **Decision**: 앱 UI·가이드북 MVP 번역 언어 **영어·중국어·일본어**.
- **Reason**: 핵심 기능 요구사항 #1.
- **Alternatives considered**: 한국어 포함 4언어, 영어만 MVP.
- **Impact**: i18n 키·번역 파이프라인 3벌 관리.

---

## 2026-05-26 - 홈 경험(대시보드)

- **Decision**: **온보딩 상태별 홈 분기** — 입학 전 / 재학 / 생활.
- **Reason**: 핵심 기능 #2, 단계별 “다음 할 일” 제공.
- **Alternatives considered**: 단일 홈, 역할만 분기(학생/교직원).
- **Impact**: 사용자 프로필·상태 필드, 홈 카드 구성 테이블 필요.

---

## 2026-05-26 - 콘텐츠 원천

- **Decision**: **KU 가이드북 섹션**을 앱 구조로 이식하고 **3개 언어** 제공.
- **Reason**: 핵심 기능 #3, 공식 안내 신뢰도.
- **Alternatives considered**: 웹뷰만, 신규 FAQ만 작성.
- **Impact**: 섹션 매핑·버전·갱신 프로세스 정의 필요.

---

## 2026-05-26 - 국제처 협업 시점

- **Decision**: **MVP 개발 우선**; 국제처 **공식 검수·협업은 추후** 검토.
- **Reason**: 사용자 명시(개발 선행).
- **Alternatives considered**: 협업 후 개발 시작.
- **Impact**: 초기 콘텐츠는 팀 수집·비공식; 공식 배포 전 검수 게이트 필요.

---

## 2026-05-26 - FAQ·AI 정책(방향)

- **Decision**: FAQ **키워드 검색** + AI는 **가이드북·FAQ 근거·출처 표시**; 불확실 시 국제처 문의 유도.
- **Reason**: 행정 오안내 리스크 완화.
- **Alternatives considered**: 무제한 생성형 챗, 챗봇 MVP 제외.
- **Impact**: RAG 또는 FAQ-only 구현; MVP에서 무출처 답변 금지.

---

## 2026-05-26 - MVP vs 전체 기능

- **Decision**: **Must**: 다국어, 3상태 대시보드, 가이드북 핵심 섹션, Push(수강·비자), FAQ+제한 AI, 알림 센터. **Should**: 지도·수강 가이드. **Could**: 커뮤니티·룸메이트. **Non-Scope MVP**: 커뮤니티 오픈(모더레이션 없음), 포털 대체.
- **Reason**: `mvp-scope-planning` 범위 통제.
- **Alternatives considered**: 사용자 제시 7개 기능 전부 Must.
- **Impact**: 1.0 일정·인력 현실화; 1.x/2.0 로드맵 분리.

---

## 2026-05-26 - Agentic 문서 SSOT

- **Decision**: 기획·범위 SSOT는 **`docs/agentic/`** (`context_packet.md` + `skill_outputs.md`). 레거시 RAG `data/status.md`는 `application` 브랜치에서 제거됨.
- **Reason**: 브랜치 `application`에서 신규 앱 기획만 유지.
- **Alternatives considered**: `data/status.md` 복원.
- **Impact**: Cursor `chatbot-status.mdc`와 불일치 — 규칙·status 파일 추후 정리 필요.

---

## 2026-05-26 - Source-only 답변 + 확인 턴 (파인튜닝 보류)

- **Decision**: 답변은 **가이드북 청크 인용만** (`citation_first`). 검색 `low`/`none` → **모른다**. `medium` → **관련 있나요?** 확인 후 yes=인용, no=모른다. **LoRA/파인튜닝은 하지 않음.**
- **Reason**: 사용자 요구(출처 밖 답 금지·확인 후 응답). 소형 LLM 환각 위험.
- **Alternatives considered**: 프롬프트만 LLM, 파인튜닝 우선.
- **Impact**: [`backend/rag/retriever.py`](../backend/rag/retriever.py) 밴드, [`pending_sessions.py`](../backend/rag/pending_sessions.py), API `status`·`confirm` 필드.

---

## 2026-05-26 - 초기 구현 스택 (스파이크 브랜치)

- **Decision**: `feat/initial-ui-chatbot`에서 **Expo** UI + **FastAPI** + **Chroma RAG** + **Hugging Face 공개 LLM**(`Qwen2.5-0.5B-Instruct` 기본). 파인튜닝은 보류.
- **Reason**: 사용자 승인(Expo, RAG+HF). 빠른 E2E 검증.
- **Alternatives considered**: FAQ-only, OpenAI API, Vite 웹만.
- **Impact**: `backend/`, `mobile/` 추가; main 기획 Must 전체와 분리.

---

## 2026-05-26 - Skill 파일 위치

- **Decision**: Skill **절차**는 **`.cursor/skills/<skill-name>/SKILL.md`**; Skill **산출물**은 **`docs/agentic/skill_outputs.md`**.
- **Reason**: Cursor 프로젝트 Skill 규칙·절차/결과 분리.
- **Alternatives considered**: Skill 본문만 `skill_outputs`, 절차는 `AGENTS.md` 단일 파일.
- **Impact**: 에이전트는 Skill 실행 시 `.cursor/skills/` 먼저 읽고, 완료 후 `docs/agentic/` 갱신.

---

## 2026-05-26 - 서류 질문: 의도 라우팅 + 제한 LLM 추출

- **Decision**: `document_list` 의도는 검색 청크 안에서만 제출서류 목록 추출. **규칙 파싱 우선**, 부족 시 `CHATBOT_ANSWER_MODE=llm_document_extract`일 때만 HF 소형 LLM. LLM 출력은 **컨텍스트 부분 문자열 검증**; 0건이면 `unknown`. 일반 질문은 `citation_first` 문장 인용 유지.
- **Reason**: 「필요 서류」 질문에 재입국·전입신고 문장이 섞이는 문제(넓은 토큰 매칭·청크 혼합). 파인튜닝 없이 faithfulness 확보.
- **Alternatives considered**: 파인튜닝/LoRA, cross-encoder reranker만, LLM 전체 요약.
- **Impact**: `rag/intent.py`, `document_extractor.py`, section `chunking` + `section_title` 메타, citation URL dedupe, 인덱스 재구축 필요.

---

## 2026-05-26 - 통합 LLM RAG 답변 (검색 → LLM)

- **Decision**: 기본 `CHATBOT_ANSWER_MODE=llm_rag`. **모든 질문**은 Chroma 검색 후 **검색 청크만** HF instruct에 넣어 답변. `intent`는 검색 확장·프롬프트 힌트만. `citation_first`·`document_extractor` 기본 경로는 제거(실패 시 문장 인용 fallback만). 링크 실시간 fetch 없음.
- **Reason**: 검색은 되나 규칙·문장 5개 추출이 질문 의도와 어긋남. 사용자 요청(통합 LLM 이해·답변).
- **Alternatives considered**: 서류만 규칙 유지, 전 질문 `citation_first`, 더 큰 API 모델.
- **Impact**: [`generator.py`](../backend/rag/generator.py), [`main.py`](../backend/app/main.py) `_build_answer`, [`config.py`](../backend/rag/config.py) `uses_llm_rag()`.
