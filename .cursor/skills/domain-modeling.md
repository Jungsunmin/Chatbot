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

1. 핵심 개념 (SourceDocument, Chunk, Query, LanguagePolicy, Retrieval pipeline, ChatResponse …)
2. 엔티티·속성·관계(ER 수준)
3. 도메인 규칙 (faithfulness, LanguagePolicy, SensitiveTopic, confirm/unknown)
4. 용어집(한/영 병기)

## 프로젝트 힌트 (KU RAG 챗봇)

- **English-first** 다국어: `default_response_language=en`, 검색 정규화는 영어.
- **RAG SSOT**: 공식 한국어 웹을 사람이 정리한 **한국어** `.md` (`/chat` 실시간 크롤 없음).
- `response_lang`으로 답변; 한국어 행정 용어는 **English (한국어)** 병기.
- LLM 입력은 **vector top-k**와 **SelectedContext** 구분; **RerankResult** 선택.
- 산출물에 **LanguagePolicy**, 확장 **Query**, **SensitiveTopic** / **SafetyNotice** 포함.

## Output template

`docs/agentic/skill-outputs/domain-modeling.md`

```md
# Domain Model
## Core Concepts
## Entities
## Relationships
## Domain Rules
## Glossary
```
