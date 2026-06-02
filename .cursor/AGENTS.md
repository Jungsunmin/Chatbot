# AGENTS.md

## Purpose

This project uses an **Agentic Coding** workflow.

Do not jump directly from a vague request to code. Work through structured stages:

1. Define the service goal.
2. Identify stakeholders.
3. Decompose requirements.
4. Decide MVP scope.
5. Model the domain.
6. Plan the architecture.
7. Design the database.
8. Break work into small tasks.
9. Write implementation prompts.
10. Implement frontend/backend/database changes.
11. Test, review, check security/privacy.
12. Prepare deployment and documentation handoff.

A Skill is treated as:

> structured prompt + procedure + constraints + output format

The output of one Skill becomes the input to the next Skill.

---

## Core operating rule

Before implementing, check whether the request already has enough context.

If context is missing, do not invent product goals, requirements, architecture, security policy, or scope. Record assumptions in `docs/agentic/ASSUMPTIONS.md` and open questions in `docs/agentic/OPEN_QUESTIONS.md`.

Human approval is required for:

- service goal
- MVP scope
- non-scope
- privacy/security policy
- architecture direction
- deployment responsibility
- success criteria

---

## Required context files

Maintain the following files:

- `docs/agentic/context_packet.md`
- `docs/agentic/DECISIONS.md`
- `docs/agentic/ASSUMPTIONS.md`
- `docs/agentic/OPEN_QUESTIONS.md`
- `docs/agentic/skill_outputs.md`

### `context_packet.md`

Keep this short and current. It should contain confirmed goal, target users, MVP scope, non-scope, key decisions, active assumptions, open questions, current architecture summary, and current next task.

Use it as the main compact context before starting a new Skill.

### `DECISIONS.md`

Record confirmed decisions only.

```md
## YYYY-MM-DD - Decision title
- Decision:
- Reason:
- Alternatives considered:
- Impact:
```

### `ASSUMPTIONS.md`

Record unverified assumptions.

```md
## Assumption
- Assumption:
- Why it matters:
- Risk if wrong:
- How to verify:
```

### `OPEN_QUESTIONS.md`

Record unresolved questions.

```md
## Question
- Question:
- Owner:
- Needed by:
- Impact if unresolved:
```

---

## Skill sequence

Use this sequence unless the user explicitly asks for a focused implementation task.

**Skill 정의(절차·출력 템플릿)**: [`.cursor/skills/README.md`](.cursor/skills/README.md) — 각 Skill은 `.cursor/skills/<skill-name>.md`.

**Skill 산출물(프로젝트 결과)**: `docs/agentic/skill_outputs.md` 및 `context_packet.md` 등.

| # | Skill file | 산출물 섹션 (`skill_outputs.md`) |
|---|------------|----------------------------------|
| 1 | `service-goal-definition` | `service_goal_definition` |
| 2 | `stakeholder-analysis` | `stakeholder-analysis` |
| 3 | `requirements-decomposition` | `requirements-decomposition` |
| 4 | `mvp-scope-planning` | `mvp-scope-planning` |
| 5 | `domain-modeling` | `domain-modeling` |
| 6 | `architecture-planning` | `architecture-planning` |
| 7 | `database-design` | `database-design` |
| 8 | `task-breakdown` | `task-breakdown` |
| 9 | `implementation-prompt-writer` | `implementation-prompt-writer` |
| 10 | `backend-implementation`, `frontend-implementation` | implementation |
| 11 | `test-strategy`, `code-review`, `security-privacy-review`, `deployment-operations`, `documentation-handoff` | 각 동명 섹션 |

공통 계약: [`.cursor/skills/skill-contract.md`](.cursor/skills/skill-contract.md)

Implementation order: database schema → backend API → frontend UI → integration → edge cases → tests.

---

## Coding behavior

When writing code:

- Make the smallest safe change that satisfies the task.
- Do not broaden scope.
- Preserve existing architecture unless a change is explicitly approved.
- Add tests when behavior changes.
- Avoid hidden assumptions.
- Explain trade-offs briefly.
- Do not silently introduce new dependencies.
- Do not hardcode secrets.
- Do not log personal or sensitive data.
- Keep public interfaces stable unless the task says otherwise.

---

## Security and privacy defaults

Before implementing features involving user data, files, authentication, payments, video, logs, or external APIs, run a security/privacy check.

Check what personal data is stored, where it is stored, who can access it, whether logs contain sensitive data, whether environment variables are used for secrets, whether deletion/export is needed, and whether permissions are enforced server-side.

---

## Completion criteria

A task is not complete until code is implemented, tests or manual verification steps are provided, edge cases are considered, docs/context files are updated if the decision changed, and assumptions/open questions are recorded.
