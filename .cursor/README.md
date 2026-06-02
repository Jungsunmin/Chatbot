# Cursor — 건국대 유학생 앱 (`application`)

## 구조

| 경로 | 역할 |
|------|------|
| [`AGENTS.md`](AGENTS.md) | 에이전트 워크플로·승인 규칙 |
| [`skills/`](skills/README.md) | **Skill 절차** (`<name>.md`) |
| [`rules/`](rules/) | Cursor rules (agentic-coding, workspace-sync) |
| [`hooks/`](hooks.json) | 파일 트리 스냅샷 갱신 등 |

## Skill vs 산출물

- **How (절차)**: `.cursor/skills/`
- **What (결과)**: `docs/agentic/` — especially `skill_outputs.md`, `context_packet.md`

## 사용 예

```
domain-modeling 스킬로 skill_outputs 갱신해줘
```

## Agentic 문서

- [`docs/agentic/context_packet.md`](../docs/agentic/context_packet.md)
