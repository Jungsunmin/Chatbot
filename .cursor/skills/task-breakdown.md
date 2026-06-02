---
name: task-breakdown
description: Break MVP into small tasks with scope, dependencies, done criteria, and tests. Use before implementation-prompt-writer.
---

# Task Breakdown

## When to use

- 구현 착수 전 스프린트·PR 단위 분할

## Prerequisites

- `mvp-scope-planning` Must, `architecture-planning`, `database-design`

## Procedure

1. Must 기능 → 작업 ID 부여
2. 의존성 순서(스키마 → API → 앱 화면 → Push → FAQ)
3. Done Criteria·검증 방법 per task
4. 1 PR = 1 task 권장

## Output template

`docs/agentic/skill_outputs.md` → `## task-breakdown`

```md
# Task Breakdown
| ID | Task | Scope | Dependencies | Done Criteria | Test |
```
