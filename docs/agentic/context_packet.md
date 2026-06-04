# context_packet.md

**최종 갱신**: 2026-06-04  
**브랜치**: `feat/initial-ui-chatbot`  
**단계**: **Visa Phase 1 구현** (T01 visa 10건 배치 완료 → T02–T20)

---

## Confirmed Goal

KU **외국인 유학생** RAG FAQ 챗봇 — Korean curated md → 검색 → **English-first** 다국어 답변 + 출처.

## Languages

- 인덱스: **Korean human-curated `.md`**
- 검색: `normalized_query_en` + `expanded_terms`
- 응답: ko/en/zh/ja; default fallback **en**; **preserve_terms** English (한국어)

## MVP Must (요약)

`/chat` + confirm + unknown + citations | Chroma | **visa 10 Korean md** (Phase 1) | Expo 4-lang UI | 무로그인

상세: [mvp-scope-planning.md](./skill-outputs/mvp-scope-planning.md) · 인덱스: [architecture AR-1](./skill-outputs/architecture-planning.md)

## Key Decisions

- Skills 1–6 + 7–11 문서화 완료 — [documentation-handoff.md](./skill-outputs/documentation-handoff.md)
- [DECISIONS.md](./DECISIONS.md)

## Open Questions

- `query_normalizer` 구현 방식 (1.5B 1-shot vs embed-only)
- 국제처 협업·파일럿 DPA
- [OPEN_QUESTIONS.md](./OPEN_QUESTIONS.md)

## Architecture (one line)

```text
Expo → POST /chat → Query pipeline → Chroma(KO chunks) → rerank → LLM(response_lang)
```

[architecture-planning.md](./skill-outputs/architecture-planning.md)

## Current Next Task

1. **T01 (visa)**: 10× `backend/data/sources/visa/*_ko.md` — 검수 후 `human_curated` (선택)  
2. **T02–T03**: 인덱스 + `/health`  
3. **T04–T20**: [task-breakdown.md](./skill-outputs/task-breakdown.md) PR 순서

## References

- [skill-outputs/README.md](./skill-outputs/README.md)
- [`.cursor/AGENTS.md`](../../.cursor/AGENTS.md)
