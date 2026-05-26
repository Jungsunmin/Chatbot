---
name: architecture-planning
description: Plan modules, data flow, integrations, API boundaries, failure modes, and trade-offs for iOS/Android app and backend.
---

# Architecture Planning

## When to use

- `domain-modeling` 완료 후
- 기술 스택·배포 형태 결정

## Prerequisites

- `domain-modeling`, MVP Must, NFR

## Procedure

1. 모듈(모바일 앱, API, CMS/콘텐츠, Push, FAQ/RAG)
2. 데이터 흐름(가이드북 ingest → API → 앱)
3. 외부 연동(FCM/APNs, 지도, 선택 LLM)
4. API 경계·인증
5. 실패 모드·완화
6. 트레이드오프(크로스플랫폼 vs 네이티브 등)

## Output template

`docs/agentic/skill_outputs.md` → `## architecture-planning`

```md
# Architecture Plan
## Modules
## Data Flow
## External Integrations
## API Boundaries
## Failure Modes
## Trade-offs
```

## Project hint

iOS+Android, EN/ZH/JA, 오프라인 가이드북 캐시, FAQ는 가이드북·FAQ 근거 우선.
