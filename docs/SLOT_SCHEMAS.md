# 슬롯 스키마 (clarify)

`data/schemas/{category}.yaml` 하나당 카테고리.

## 필드

- `required_slots` — 비어 있으면 `clarify` 응답, RAG 미호출
- `optional_slots` — 있으면 검색 품질 보조
- `clarify_message` — `en` / `ko` 안내 문구

## 새 카테고리 추가

1. `data/schemas/my_category.yaml` 작성
2. `src/dialog/intent_rules.py` 에 키워드 추가 (MVP)
3. FAQ 문서·manifest에 `category` 일치

## MVP 포함 카테고리

- `course_registration`
- `housing`
- `visa_immigration`
