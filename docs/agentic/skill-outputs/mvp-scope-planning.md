# MVP 범위

**승인 기준일**: 2026-06-02  
**기준**: [requirements-decomposition.md](./requirements-decomposition.md), Skill 1·2  
**제품**: KU **RAG FAQ 챗봇** (Expo + FastAPI + Chroma) — **풀앱 아님**

---

## Must (MVP 1.0 — 파일럿·내부 테스트 최소)

### 핵심 기능 (FR 매핑)

| 영역 | 포함 내용 | FR |
|------|-----------|-----|
| **RAG 챗 API** | `POST /chat`, `answered` / `confirm_needed` / `unknown`, citations, confirm yes/no | FR-1.1~1.4 |
| **인덱스·운영** | `GET /health`, `build_index` / `POST /admin/reindex`, Chroma + 섹션 청크 | FR-1.5~1.6, FR-2.2~2.3 |
| **소스 SSOT** | `data/sources/**/*.md`, frontmatter, **실시간 크롤 없음** | FR-2.1, FR-2.4 |
| **Faithfulness** | context-only LLM, low/none → unknown, `__UNKNOWN__`, citation URL dedupe | FR-3.1~3.4 |
| **모바일 챗** | Expo 챗 UI, confirm 턴, **무로그인**, citation 링크 열기 | FR-5.1~2, FR-5.5, FR-3.5 |
| **다국어 API·UI** | `lang` **ko/en/zh/ja** — UI 문자열 **4언어 전부** Must | FR-4.1, FR-4.2, FR-4.4(빈 UI 금지) |
| **소스 언어 (Must)** | 아래 **MVP 섹션**에 대해 **한국어(ko) + 영어(en)** 본문 인덱스 | FR-2.5, FR-4.3 |
| **의도 검색 보강** | 서류·절차·기한 intent + `제출서류` 우선(이미 구현 방향) | FR-4.5 |
| **운영 문서** | md → reindex runbook (`RAG_SOURCES` 등) | FR-6.1 |
| **플랫폼** | iOS·Android (Expo), FastAPI 백엔드 | NFR-1 |

### MVP 가이드북·FAQ 소스 섹션 (Must — ko + en 각 1세트)

| # | 섹션 | 비고 |
|---|------|------|
| 1 | **Visa / Immigration** (비자·외국인등록) | 서류 질의 핵심 |
| 2 | **Enrollment / Registration** (등록·신입) | |
| 3 | **Housing / Dormitory** (기숙사) | |
| 4 | **Course / Academic** (수강·학사 FAQ) | 수강신청 안내 포함 |

> Welcome, Emergency, Academic Calendar 전체는 **Should**(아래).

### 다국어 Must 정책 (확정)

| 항목 | Must |
|------|------|
| **UI** | ko / en / zh / ja 전환·고정 문구(unknown, confirm) |
| **API `lang`** | 4종 모두 지원 — 답변은 요청 `lang`으로 생성 |
| **소스 본문** | MVP Must는 **ko + en** 만 (4섹션). zh/ja 소스 없어도 **앱·API는 4언어 동작** |
| **소스 없을 때** | 해당 lang 질의 → 검색은 다언어 임베딩·다른 lang 청크 가능; 답 없으면 **unknown** + 국제처 안내 (무출처 답 금지) |

### Must에서 제외 (이미 Non-Scope)

대시보드 3상태, Push, 지도, 커뮤니티, SSO, 키워드 FAQ 목록-only, 국제처 공식 검수 워크플로, 스토어 공개 홍보

---

## Should (MVP 1.x — Must 직후 1~2스프린트)

| 영역 | 포함 내용 | FR |
|------|-----------|-----|
| **소스 zh / ja** | Must 4섹션과 동일 주제의 **중국어·일본어** `.md` | FR-4.3 |
| **추가 섹션** | Welcome, **Emergency Contacts** ko+en(+zh/ja) | FR-2.5 |
| **샘플 Q&A QA** | 카테고리별 ≥10질의, AC-1~3 측정 | AC-1~3 |
| **소스 폴백 UX** | 미번역 시 “영문 소스 기준” 등 **배지/안내** (정책 문구 4언어) | FR-4.4 |
| **갱신일·출처 메타** | frontmatter `updated` 또는 UI 표시 | FR-6.2 |
| **PII 경고** | 챗 입력 시 학번·전화 등 경고 copy | FR edge |
| **성능·모델** | 1.5B 등 Mac 친화 모델 기본값 문서화 | NFR-2 |

---

## Could (2차 · 풀앱·고도화)

| 영역 | 내용 |
|------|------|
| **풀앱** | 3상태 대시보드, Push, 지도, 알림 센터, 커뮤니티·룸메이트 |
| **인증** | KU SSO, 학번 로그인 |
| **국제처** | 공식 검수·승인·브랜딩, 공지 API 연동 |
| **FAQ UX** | 키워드 FAQ 목록·하이라이트(챗 병행) |
| **AI** | 외부 API, STT, 대화 히스토리·계정 |
| **Academic Calendar** | 학사력 전체 소스·일정 연동 |
| **오프라인** | 가이드북 캐시, 오프라인 챗 불가 안내 |

---

## 범위 외 (명시적 제외)

- 타 대학·범용 플랫폼
- **공식 성적·수강신청·포털** 대체
- **실시간 URL 크롤** on `/chat`
- **출처 없는** 행정 AI 답변
- **모더레이션 없는** 커뮤니티 오픈
- MVP 단계 **국제처 공식 운영·대외 스토어 홍보** 전제
- 무제한 OpenAI식 자유 채팅

---

## FR → MoSCoW 요약

| FR 그룹 | Must | Should | Could |
|---------|------|--------|-------|
| FR-1 챗 API | 1.1~1.6 | — | — |
| FR-2 소스 | 2.1~2.4, 2.5(ko+en 4섹션) | 2.5 확장 섹션·zh/ja | 전 섹션·전 언어 |
| FR-3 faithfulness | 3.1~3.4 | 3.5 UX polish | — |
| FR-4 i18n | 4.1~4.2, 4.4(크래시 없음), 4.5 | 4.3 zh/ja 소스, 4.4 배지 | — |
| FR-5 Expo | 5.1~2, 5.4~5.5 | 5.3 문구 다듬기 | — |
| FR-6 운영 | 6.1 | 6.2 | 6.3 |

---

## 릴리스 기준 (MVP 1.0 챗봇)

- [ ] **AC-1~7** ([requirements-decomposition](./requirements-decomposition.md)) — 파일럿 전 샘플 QA 통과
- [ ] Must **4섹션** ko+en 소스 인덱스, `indexed_chunks` > 0
- [ ] **4언어 UI** 전환 크래시 없음 (AC-4)
- [ ] 내부·파일럿 **10+ 유학생** 2주 (또는 팀 정의 n)
- [ ] 소스 **reindex runbook** + AI/FAQ **면책·개인정보** 초안(질문만 전송, 무로그인)
- [ ] iOS·Android **TestFlight/내부 빌드** E2E 1회 (AC-7)
- [ ] (선택) 국제처 비공식 리뷰 1회

---

## MVP 이후 로드맵 (한 줄)

`1.0 RAG 챗(ko+en 소스, 4언어 UI)` → `1.x zh/ja 소스·QA 세트` → `2.0 풀앱·SSO·국제처 연동`

---

**다음 Skill**: `domain-modeling` — 챗·소스·세션·Citation 개념 모델
