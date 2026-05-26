# OPEN_QUESTIONS.md

미해결 질문. 최종 갱신: 2026-05-26

---

## P0 — domain-modeling 전에 필요

### 가이드북 MVP 섹션 최종 목록

- **Question**: Must에 넣을 **가이드북 섹션** 최종 목록은? (초안 6개: Welcome, Visa, Enrollment, Housing, Calendar, Emergency)
- **Owner**: 기획·개발 팀
- **Needed by**: `domain-modeling`, 번역 견적
- **Impact if unresolved**: 범위·일정 불명확

### 1차 사용자·상태 전환 규칙

- **Question**: “입학 전/재학/생활” **자동 전환**(일정 기반) vs **사용자 수동**만?
- **Owner**: 기획
- **Needed by**: FR-2 상세 설계
- **Impact if unresolved**: 대시보드 로직 중복·혼란

### 인증·계정

- **Question**: MVP 로그인 — **게스트/이메일** / **학번+비밀번호(포털)** / **소셜** 중 무엇?
- **Owner**: 기획 + (추후) 학교 IT
- **Needed by**: architecture-planning
- **Impact if unresolved**: Push·알림·커뮤니티 설계 불가

---

## P1 — architecture·구현 전

### 한국어 UI

- **Question**: UI에 **한국어** 포함 여부? (현재 결정: EN/ZH/JA만)
- **Owner**: 기획
- **Needed by**: i18n 설계
- **Impact if unresolved**: 번역 비용·QA 범위

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
