# context_packet.md

**최종 갱신**: 2026-05-26  
**브랜치**: `feat/initial-ui-chatbot` (초기 UI·RAG 챗 스파이크)  
**다음 Skill**: `domain-modeling` · `architecture-planning` (스파이크 검증 후)

---

## Confirmed Goal

건국대학교(KU) **외국인 유학생**을 위한 **다국어 모바일 앱**. 분산된 가이드북·학사 정보를 **입학 전~재학~생활** 단계별로 통합하고, 일정 알림·지도·FAQ로 **국제처 접근성**을 높인다.

## Target Users

- **1차**: KU 외국인 유학생(학부·대학원·어학당·교환)
- **온보딩 상태**: 입학 전 / 재학 / 생활 — 홈 대시보드 분기
- **2차(추후)**: 국제처·외국인학생센터(콘텐츠 검수·공지)

## MVP Scope

### Must

다국어(EN/ZH/JA), 3상태 대시보드, 가이드북 핵심 섹션 이식·번역, 수강신청·비자 등 Push, FAQ 검색·출처 있는 AI/FAQ-only, 통합 알림 센터(수동 피드), iOS+Android, 백엔드·콘텐츠 API

### Should

캠퍼스 지도(검색·기관 카드), 수강신청 스크린샷 가이드, 가이드북 전체·오프라인, 국제처 검수 워크플로

### Could

커뮤니티(국적별), 룸메이트 매칭, 포털 SSO, 고급 지도·AI

### Non-Scope (MVP)

타 대학, 성적·수강 시스템 대체, 무검증 커뮤니티 오픈, 국제처 공식 운영 전제, 출처 없는 AI 행정 답변

## Key Decisions

- 대상: **건국대학교** 외국인 유학생 앱
- 플랫폼: **iOS + Android**
- 언어: **영어·중국어·일본어**
- 국제처: **MVP 개발 우선**, 공식 협업·검수는 추후
- FAQ AI: **가이드북·FAQ 근거 + 출처** (환각 완화)
- 상세: [DECISIONS.md](./DECISIONS.md)

## Active Assumptions

- KU 가이드북을 섹션 단위로 구조화·이식 가능
- Push는 FCM/APNs 등 표준 스택 사용
- 지도·길찾기 데이터 소스는 별도 확보 필요
- 상세: [ASSUMPTIONS.md](./ASSUMPTIONS.md)

## Open Questions

- 가이드북 MVP 섹션 최종 목록, 한국어 UI 필요 여부, 인증 방식, AI/지도 데이터 소스
- 상세: [OPEN_QUESTIONS.md](./OPEN_QUESTIONS.md)

## Current Architecture Summary

**프로토타입 (구현 중)**  
`mobile/` Expo → `POST /chat` → `backend/` FastAPI → Chroma RAG → HF `transformers` (Qwen2.5-0.5B 기본).  
소스 문서: `backend/data/sources/*.md`. 상세: [`docs/RAG_PROTOTYPE.md`](../RAG_PROTOTYPE.md).

## Current Next Task

1. 로컬에서 백엔드·Expo 연동 테스트  
2. KU 가이드북 실제 섹션을 `data/sources`에 확장  
3. Skill **`domain-modeling`** → 전체 MVP 아키텍처 정리

## References

- Skill **절차**: [`.cursor/skills/README.md`](../../.cursor/skills/README.md)
- Skill **산출물**: [skill_outputs.md](./skill_outputs.md)
- 워크플로: [`.cursor/AGENTS.md`](../../.cursor/AGENTS.md)
