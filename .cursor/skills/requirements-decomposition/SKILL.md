---
name: requirements-decomposition
description: Decompose functional/non-functional requirements, user scenarios, edge cases, and acceptance criteria. Use after mvp-scope-planning draft or in parallel with scope refinement.
---

# Requirements Decomposition

## When to use

- MVP 범위가 대략 잡힌 뒤 상세 FR/NFR 정의
- 기능 번호(다국어, 대시보드, 가이드북, Push, 지도, FAQ 등)를 요구사항 ID로 분해

## Prerequisites

- `service-goal-definition`, `stakeholder-analysis` 권장
- `mvp-scope-planning` Must 목록

## Procedure

1. 기능 영역별 FR 표(ID, 설명, 수용 기준)
2. NFR(플랫폼, 성능, 보안, i18n, 운영)
3. 사용자 시나리오 5~10개
4. 엣지 케이스(언어 폴백, Push 거부, AI 무출처 등)
5. 통합 Acceptance Criteria

## Output template

`docs/agentic/skill_outputs.md` → `## requirements-decomposition`

```md
# Requirements Decomposition
## Functional Requirements
## Non-Functional Requirements
## User Scenarios
## Edge Cases
## Acceptance Criteria
```
