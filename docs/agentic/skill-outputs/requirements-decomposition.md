# 요구사항 분해

**기준**: [service-goal-definition.md](./service-goal-definition.md), [stakeholder-analysis.md](./stakeholder-analysis.md) (2026-06-02)  
**범위**: KU **RAG FAQ 챗봇**만 — 풀앱(FR 대시보드·Push·지도·커뮤니티) **제외**  
**다국어**: **ko / en / zh / ja**

---

## 기능 요구사항

### FR-1 챗·RAG API

| ID | 요구사항 | 수용 기준(초안) |
|----|----------|-----------------|
| FR-1.1 | `POST /chat` — 자연어 질의·`lang`(ko\|en\|zh\|ja) 수신 | 유효 JSON·빈 1차 메시지 거부 |
| FR-1.2 | 응답 `status`: `answered` \| `confirm_needed` \| `unknown` | 클라이언트가 UI 분기 가능 |
| FR-1.3 | `answered` 시 **본문 + citations[]** (`title`, `source_url`, `excerpt` 등) | 샘플 질의에서 citation ≥1 (high 밴드) |
| FR-1.4 | 검색 **관련도 medium** 시 **확인 턴** (`pending_id`, `confirm` yes/no) | no → unknown; yes → LLM 답변 |
| FR-1.5 | `GET /health` — `indexed_chunks` 등 인덱스 상태 | chunks=0이면 운영자 인지 가능 |
| FR-1.6 | `POST /admin/reindex` (개발·운영) — 소스 변경 후 인덱스 재구축 | reindex 후 검색·답변 반영 |

### FR-2 소스·인덱싱

| ID | 요구사항 | 수용 기준(초안) |
|----|----------|-----------------|
| FR-2.1 | KU 가이드북·FAQ를 **`backend/data/sources/**/*.md`** 로 관리 | frontmatter: `title`, `source_url`, `lang` 권장 |
| FR-2.2 | 마크다운 **섹션 단위 청크** + 메타(`section_title`) | `##`, `다./나.` 등 절 경계 인식 |
| FR-2.3 | Chroma **벡터 인덱스** (cosine), 다국어 임베딩 | `build_index` 후 `indexed_chunks` > 0 |
| FR-2.4 | 질문 시 **실시간 URL 크롤 없음** — 인덱스된 본문만 사용 | `/chat`이 외부 fetch 하지 않음 |
| FR-2.5 | MVP **핵심 FAQ 카테고리** 소스 포함(비자·등록·수강·기숙사 등) | 카테고리별 샘플 Q&A 1건 이상 통과(초안) |

### FR-3 답변 신뢰·출처 (faithfulness)

| ID | 요구사항 | 수용 기준(초안) |
|----|----------|-----------------|
| FR-3.1 | 답변은 **검색 청크·소스만** 근거 (LLM context-only) | 프롬프트·정책 문서화 |
| FR-3.2 | 소스에 없거나 관련도 **low/none** → **unknown** 고정 문구 | 무관 질의에서 환각 답변 없음 |
| FR-3.3 | LLM이 근거 부족 시 **`__UNKNOWN__`** → API unknown | “확인” 등 일반 한글과 혼동 없는 판별 |
| FR-3.4 | citation **URL 중복 제거** (`source_url` 기준) | 동일 링크 1회만 노출 |
| FR-3.5 | 앱에서 citation **원문 링크** 열기(있을 때) | `source_url` 탭 시 브라우저/인앱 |

### FR-4 다국어 (ko / en / zh / ja)

| ID | 요구사항 | 수용 기준(초안) |
|----|----------|-----------------|
| FR-4.1 | API `lang` 4종 — **질의·답변 언어** 힌트 | 각 lang으로 샘플 1질의 응답 가능 |
| FR-4.2 | Expo **UI 문자열** 4언어 전환 | 홈·챗·unknown/confirm 문구 ko/en/zh/ja |
| FR-4.3 | 소스 **`lang` frontmatter** 또는 파일명 규칙 | 언어별 `.md` 또는 동일 섹션 4파일 관리 가능 |
| FR-4.4 | 미번역 UI·소스 처리 — UI 4언어 Must; 소스 Must ko+en; zh/ja Should; 없으면 unknown | 빈 UI·크래시 없음 ([mvp-scope-planning](./mvp-scope-planning.md)) |
| FR-4.5 | (선택) 의도별 검색 보강(서류·절차·기한) | “필요 서류” 질의 시 제출서류 청크 우선 |

### FR-5 모바일 챗 UI (Expo)

| ID | 요구사항 | 수용 기준(초안) |
|----|----------|-----------------|
| FR-5.1 | 챗 화면 — 메시지 입력·전송·응답 표시 | LAN/에뮬레이터에서 `/chat` 연동 |
| FR-5.2 | `confirm_needed` — 예/아니오 + `pending_id` 2차 호출 | 사용자 확인 후 answered 또는 unknown |
| FR-5.3 | `unknown`·오류 시 **국제처 문의 유도** 문구(4언어) | 고정 템플릿 i18n |
| FR-5.4 | 언어 선택(설정 또는 진입 시) — **4언어** | 선택 lang이 API에 전달 |
| FR-5.5 | **로그인 없이** 챗 사용 가능 (MVP) | 계정·SSO 불필요 |

### FR-6 운영·콘텐츠 (비개발 사용자 관점)

| ID | 요구사항 | 수용 기준(초안) |
|----|----------|-----------------|
| FR-6.1 | 소스 갱신 절차 문서화 (md 추가·수정 → reindex) | runbook 1페이지 이상 |
| FR-6.2 | (Could) 소스 **갱신일·출처** UI/API 노출 | frontmatter 또는 메타 필드 |
| FR-6.3 | (추후) 국제처 **검수·승인** 워크플로 | MVP Non-Scope |

---

## 범위 외 (요구사항에 넣지 않음)

| 구 영역 | 이유 |
|---------|------|
| 맞춤 대시보드·온보딩 상태 홈 | Skill 1 Non-Goals |
| Push·학사 일정·캘린더 | 동일 |
| 캠퍼스 지도·길찾기 | 동일 |
| 커뮤니티·룸메이트 | 동일 |
| 포털 SSO·성적 API | 동일 |
| 키워드 FAQ 목록만(검색 UI) without RAG | 본 서비스는 **RAG 챗** 중심; 목록-only는 2차 |

---

## 비기능 요구사항

| ID | 영역 | 요구사항 |
|----|------|----------|
| NFR-1 | 플랫폼 | iOS·Android (Expo); 백엔드 FastAPI |
| NFR-2 | 성능 | 챗 1턴 응답 — 로컬 LLM 기준 수십 초 이내 목표(환경 의존); 첫 요청 모델 로드 예외 |
| NFR-3 | 가용성 | 백엔드·인덱스 없을 때 503/unknown — 앱 크래시 없음 |
| NFR-4 | 보안 | HTTPS(배포 시); API 키·비밀 `.env`; 챗 로그에 **PII 최소·마스킹** |
| NFR-5 | 개인정보 | MVP **계정·이름·학번 수집 없음**; 질문 텍스트만 전송 |
| NFR-6 | i18n | ko/en/zh/ja UI·API; 다국어 임베딩·LLM 지원 |
| NFR-7 | 신뢰성 | RAG + unknown·confirm 정책; **무출처 행정 답변 금지** |
| NFR-8 | 운영 | `.md` 소스 + `build_index` / reindex; 버전 관리(git) |
| NFR-9 | 유지보수 | Skill·agentic 문서와 구현 범위 정합 |

---

## 사용자 시나리오

1. **입학 전·비자**: 앱 설치 → **한국어** 선택 → “외국인 등록 필요 서류?” → bullet 답변 + **출처 링크** → 원문 가이드북 확인.
2. **영어 질의**: 언어 **en** → “What documents for alien registration?” → en 답변 + citation `title` en/ko 소스 정합.
3. **애매한 질의**: 관련 청크 medium → “이 내용이 맞나요?” **confirm** → 예 → 답변 / 아니오 → unknown + 국제처 안내.
4. **무관 질의**: “오늘 날씨?” → **unknown** (소스 밖).
5. **교환학생**: “exchange student course registration” → 해당 소스 없으면 unknown; 있으면 출처와 함께 답변.
6. **운영자**: 가이드북 md 수정 → `build_index` → `/health` chunks 증가 → 동일 질의 답변 갱신 확인.
7. **중국어·일본어**: zh/ja UI 전환 후 confirm·unknown 문구가 해당 언어로 표시.

---

## 엣지 케이스

| 케이스 | 기대 동작 |
|--------|-----------|
| `indexed_chunks = 0` | unknown 또는 503; 운영자 reindex 안내 |
| 동일 `source_url` 다중 청크 | citation 1건으로 dedupe |
| 질문 언어 ≠ 소스 `lang` | 다국어 임베딩·LLM으로 답 시도; 실패 시 unknown (폴백 정책은 Skill 4) |
| 소스 일부 언어만 존재 | 해당 lang 질의 시 unknown 또는 en 폴백(정책 미정) |
| LLM OOM·타임아웃 | unknown + `model_used=false`; 앱 오류 메시지 |
| `pending` 만료 | 2차 confirm 404 → 사용자에게 재질문 안내 |
| 개인정보·학번 전체 입력 | (Should) UI 경고; 로그 저장 최소화 |
| “확인해 주세요” 등 본문 한글 | `__UNKNOWN__` 오탐 없음 |
| 매우 긴 질문 | `max_length` 검증·거부 |

---

## 수용 기준 (통합)

| ID | 기준 | Skill 1 SC 연결 |
|----|------|-----------------|
| AC-1 | 샘플 질의 세트(≥10)에서 **answered + citation** 비율 목표(팀 정의, 예: ≥80% high 관련) | SC-1 |
| AC-2 | 비자·등록·수강·기숙사 **카테고리별** 샘플 Q&A 각 1건 이상 통과 | SC-2 |
| AC-3 | 고의 무관·소스 밖 질의에서 **unknown** (환각 답 없음) | SC-3 |
| AC-4 | ko/en/zh/ja 각각 UI 핵심 화면·챗 1회 **크래시 없음** | SC-4 |
| AC-5 | `confirm_needed` → yes/no 플로우 E2E 1회 통과 | FR-1.4 |
| AC-6 | md 수정 → reindex → 답변/인용 **변경 반영** | FR-2, FR-6 |
| AC-7 | 실기기 또는 에뮬레이터에서 Expo → API **E2E** 1회 | FR-5 |

---

**다음 Skill**: `mvp-scope-planning` — 위 FR/NFR을 **Must / Should / Could / Non-Scope** 로 확정
