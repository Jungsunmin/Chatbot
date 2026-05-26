---
name: domain-modeling
description: Define core concepts, entities, relationships, domain rules, and glossary before architecture or database design.
---

# Domain Modeling

## When to use

- `mvp-scope-planning` 확정 후
- API·DB 설계 전 공통 언어 필요

## Prerequisites

- MVP Must 기능 목록
- `OPEN_QUESTIONS` P0 해소 권장(온보딩 상태, 인증 등)

## Procedure

1. 핵심 개념( User, OnboardingState, GuideSection, Schedule, Notification, FAQ …)
2. 엔티티·속성·관계(ER 수준)
3. 도메인 규칙(상태 전환, 다국어 폴백, AI 출처 필수)
4. 용어집(한/영 병기)

## Output template

`docs/agentic/skill_outputs.md` → `## domain-modeling`

```md
# Domain Model
## Core Concepts
## Entities
## Relationships
## Domain Rules
## Glossary
```
