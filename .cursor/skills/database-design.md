---
name: database-design
description: Design tables, relationships, indexes, constraints, migration plan, and data integrity risks. Use after architecture-planning, before task-breakdown.
---

# Database Design

## When to use

- 백엔드·콘텐츠 저장 구조 확정
- 다국어 콘텐츠·일정·알림·사용자 프로필 스키마

## Prerequisites

- `architecture-planning`, `domain-modeling`

## Procedure

1. 엔티티별 테이블(또는 문서 저장소) 정의
2. 관계·FK·다국어 locale 컬럼
3. 인덱스(검색·일정·user_id)
4. 제약·감사 필드(updated_at, source)
5. 마이그레이션·시드 전략
6. PII·삭제 정책

## Output template

`docs/agentic/skill_outputs.md` → `## database-design`

```md
# Database Design
## Tables
## Relationships
## Indexes
## Constraints
## Migration Plan
## Data Integrity Risks
```
