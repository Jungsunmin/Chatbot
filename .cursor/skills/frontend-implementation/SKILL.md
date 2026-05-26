---
name: frontend-implementation
description: Implement iOS/Android (or cross-platform) UI for onboarding dashboard, i18n, guidebook, notifications. Use after backend API contract exists or with mocked API.
---

# Frontend Implementation

## When to use

- 모바일 화면·네비게이션·i18n·로컬 캐시
- 단일 Implementation Prompt task

## Prerequisites

- API 계약(또는 mock) 확정
- `requirements-decomposition` FR-1, FR-2 관련

## Procedure

1. 디자인 시스템·라우팅 최소 구조
2. EN/ZH/JA 리소스·폴백
3. 온보딩 상태별 홈 분기
4. API 연동·에러·오프라인
5. 플랫폼별 Push 권한 UX
6. 수동·자동 테스트

## Constraints

- 접근성(동적 타입)·다국어 깨짐 방지
- 커뮤니티·룸메이트는 MVP Non-Scope unless scope approved
