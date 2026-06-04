# Project Skills (Agentic Coding)

건국대(KU) 외국인 유학생 앱 — **`feat/initial-ui-chatbot`** Skill 모음.

## 사용 전 (필수)

1. [`.cursor/AGENTS.md`](../AGENTS.md)
2. [`.cursor/skills/skill-contract.md`](skill-contract.md) — 시작/완료 체크리스트
3. [`docs/agentic/context_packet.md`](../../docs/agentic/context_packet.md)

## Skill 순서

| # | Skill | 절차 파일 | 선행 산출물 (`skill-outputs/`) |
|---|--------|----------|--------------------------------|
| 1 | Service Goal | [`service-goal-definition.md`](service-goal-definition.md) | — |
| 2 | Stakeholder | [`stakeholder-analysis.md`](stakeholder-analysis.md) | `service-goal-definition.md` |
| 3 | Requirements | [`requirements-decomposition.md`](requirements-decomposition.md) | `stakeholder-analysis.md` |
| 4 | MVP Scope | [`mvp-scope-planning.md`](mvp-scope-planning.md) | `requirements-decomposition.md` |
| 5 | Domain Model | [`domain-modeling.md`](domain-modeling.md) | `mvp-scope-planning.md` |
| 6 | Architecture | [`architecture-planning.md`](architecture-planning.md) | `domain-modeling.md` |
| 7 | Database Design | [`database-design.md`](database-design.md) | `architecture-planning.md` |
| 8 | Task Breakdown | [`task-breakdown.md`](task-breakdown.md) | 4, 6, 7 |
| 9 | Impl. Prompt | [`implementation-prompt-writer.md`](implementation-prompt-writer.md) | `task-breakdown.md` (해당 행) |
| 10a | Backend Impl. | [`backend-implementation.md`](backend-implementation.md) | 승인된 prompt |
| 10b | Frontend Impl. | [`frontend-implementation.md`](frontend-implementation.md) | 승인된 prompt |
| 11a | Test Strategy | [`test-strategy.md`](test-strategy.md) | 해당 기능 완료 후 |
| 11b | Code Review | [`code-review.md`](code-review.md) | 구현 task 완료 후 |
| 11c | Security/Privacy | [`security-privacy-review.md`](security-privacy-review.md) | auth/AI/Push 변경 시 |
| 11d | Deploy/Ops | [`deployment-operations.md`](deployment-operations.md) | 릴리스 전 |
| 11e | Doc Handoff | [`documentation-handoff.md`](documentation-handoff.md) | 마일스톤 종료 |

## 산출물

- **절차**: `.cursor/skills/<skill-name>.md`
- **결과**: [`docs/agentic/skill-outputs/<skill-name>.md`](../../docs/agentic/skill-outputs/), `context_packet.md`, DECISIONS, ASSUMPTIONS, OPEN_QUESTIONS

## Cursor에서 실행 예

`service-goal-definition 스킬로 context_packet 기준 갱신해줘`
