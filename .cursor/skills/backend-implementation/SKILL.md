---
name: backend-implementation
description: Implement backend API, content pipeline, push scheduling, and FAQ/RAG with minimal scope. Use after implementation-prompt-writer for a backend task only.
---

# Backend Implementation

## When to use

- API·DB·Push·콘텐츠 ingest 작업
- `implementation-prompt-writer` 산출물이 있는 단일 task

## Prerequisites

- 승인된 Implementation Prompt
- `database-design`, `architecture-planning`

## Procedure

1. 스키마·마이그레이션(해당 task 범위만)
2. API 엔드포인트·검증
3. 비밀·키는 환경 변수
4. 민감 로그 금지
5. 검증 명령 실행·결과 기록
6. `context_packet`·DECISIONS 갱신(동작 변경 시)

## Order

DB schema → API → Push/FAQ 연동 → edge cases → tests

## Constraints

- MVP Must 밖 기능 추가 금지
- FAQ AI: 출처 없는 행정 답변 금지
