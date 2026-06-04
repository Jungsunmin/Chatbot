---
name: implementation-prompt-writer
description: Write a single-task implementation prompt with goal, context, files, constraints, interface, done criteria, and verification before coding.
---

# Implementation Prompt Writer

## When to use

- `task-breakdown`의 **한 행**을 구현하기 직전
- 범위 넓은 "전부 구현해줘" 요청을 거절하고 쪼갤 때

## Prerequisites

- 해당 task ID의 Done Criteria
- `context_packet`, 관련 `skill-outputs/*.md`

## Procedure

1. Goal 한 문장
2. Context(브랜치 `application`, 기존 파일)
3. Files to modify/create (명시적 경로)
4. Constraints(Non-Scope, i18n, 보안)
5. Interface(API/컴포넌트 계약)
6. Done Criteria·Verification 명령

## Output template

`docs/agentic/skill-outputs/implementation-prompt-writer.md` (또는 작업별 별도 md 링크)

```md
# Implementation Prompt
## Goal
## Context
## Files
## Constraints
## Interface
## Done Criteria
## Verification
```

## Rule

승인 없이 범위 확장 금지 — [code-change-approval](https://cursor.com) 프로젝트 규칙 준수.
