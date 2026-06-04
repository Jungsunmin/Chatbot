# 문서 인수인계

**마일스톤**: Agentic 기획 Skill 1–11 + 구현 가이드 완료 (2026-06-02)  
**다음 단계**: [task-breakdown.md](./task-breakdown.md) T01부터 Implementation Prompt 승인 후 코딩

---

## 문서 맵

| 대상 | 시작 문서 |
|------|-----------|
| PM / 기획 | [service-goal-definition.md](./service-goal-definition.md), [mvp-scope-planning.md](./mvp-scope-planning.md) |
| 콘텐츠 (md 작성) | [domain-modeling.md](./domain-modeling.md) frontmatter, `docs/RAG_SOURCES.md`, T01 |
| 백엔드 개발 | [architecture-planning.md](./architecture-planning.md), [backend-implementation.md](./backend-implementation.md), [implementation-prompt-writer.md](./implementation-prompt-writer.md) |
| 모바일 개발 | [frontend-implementation.md](./frontend-implementation.md), architecture API 절 |
| QA / 파일럿 | [test-strategy.md](./test-strategy.md), T20 샘플 시트 |
| 보안 검토 | [security-privacy-review.md](./security-privacy-review.md) |
| 운영 | [deployment-operations.md](./deployment-operations.md), [database-design.md](./database-design.md) |

---

## SSOT 파일

| 파일 | 역할 |
|------|------|
| [context_packet.md](../context_packet.md) | 현재 상태 요약 |
| [DECISIONS.md](../DECISIONS.md) | 확정 결정만 |
| [ASSUMPTIONS.md](../ASSUMPTIONS.md) | 미검증 가정 |
| [OPEN_QUESTIONS.md](../OPEN_QUESTIONS.md) | 미결 항목 |
| [skill-outputs/](./) | Skill별 산출물 |

---

## Skill 완료 현황

| # | Skill | 산출물 | 상태 |
|---|-------|--------|------|
| 1 | service-goal-definition | [link](./service-goal-definition.md) | 승인 |
| 2 | stakeholder-analysis | [link](./stakeholder-analysis.md) | 완료 |
| 3 | requirements-decomposition | [link](./requirements-decomposition.md) | 완료 |
| 4 | mvp-scope-planning | [link](./mvp-scope-planning.md) | 완료 (AR-1이 dual en md 대체) |
| 5 | domain-modeling | [link](./domain-modeling.md) | v2 English-first |
| 6 | architecture-planning | [link](./architecture-planning.md) | 완료 |
| 7 | database-design | [link](./database-design.md) | 완료 (SQL 없음) |
| 8 | task-breakdown | [link](./task-breakdown.md) | 완료 |
| 9 | implementation-prompt-writer | [link](./implementation-prompt-writer.md) | 샘플 Prompt |
| 10 | backend-implementation | [link](./backend-implementation.md) | 가이드 |
| 10b | frontend-implementation | [link](./frontend-implementation.md) | 가이드 |
| 11 | test-strategy | [link](./test-strategy.md) | 완료 |
| 11 | code-review | [link](./code-review.md) | 체크리스트 |
| 11 | security-privacy-review | [link](./security-privacy-review.md) | 완료 |
| 11 | deployment-operations | [link](./deployment-operations.md) | 완료 |
| 11 | documentation-handoff | 본 문서 | 완료 |

---

## 알려진 한계 (이해관계자 공유)

- 답변은 **정리된 한국어 md**에 의존, 실시간 웹 아님  
- AI 오답 가능 → citation + 국제처 연락  
- English-first 검색 브릿지는 튜닝 전 엣지 쿼리 누락 가능  
- 로그인·서버 챗 기록 없음  
- 국제처 승인 없으면 비공식 파일럿  

---

## 면책 문구 (초안 — 법무 검토 필요)

> This chatbot uses AI and official guide text curated by the project team. It is not a substitute for advice from Konkuk University international offices or Korean immigration authorities. Always verify deadlines, fees, and required documents on official sources.

(앱 About 화면용 ko/en/zh/ja 번역 — Should)

---

## 인수인계 체크리스트

- [x] 기획 Skill skill-outputs TBD 해소  
- [x] context_packet이 구현 단계를 가리킴  
- [ ] README.md 파일럿 설정과 정합 (코드 복구 시)  
- [ ] 국제처 검토 일정 (미정)  

**구현 시작**: 팀 역량에 따라 **T01**(콘텐츠) 또는 샘플 md 있으면 **T03**.
