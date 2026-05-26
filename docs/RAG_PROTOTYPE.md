# RAG + LLM 프로토타입 (`feat/initial-ui-chatbot`)

## 파이프라인

```text
urls.yaml → ingest_urls.py → data/sources/web/*.md
→ section-aware chunking (section_title 메타) → embeddings → Chroma
질문 → classify_intent (검색 보강만) → expand_query → search_with_band
  → high: generate_answer (검색 청크만 LLM) | medium: confirm_needed | low/none: unknown
```

기본 답변 모드: **`llm_rag`** — 모든 질문에 대해 **검색 top-k 청크 → Qwen2.5-7B**가 context-only로 답변.

URL 목록: [`RAG_SOURCES.md`](RAG_SOURCES.md)

## 질문 의도 (`rag/intent.py`)

| 의도 | 검색 | LLM 답변 힌트 |
|------|------|----------------|
| `document_list` | 쿼리 확장 + `제출서류` 청크 우선 | 제출 서류 bullet만 |
| `procedure` | 절차·방법 확장 | 방법·절차만 |
| `deadline` | 기한 확장 | 기한·시기만 |
| `general` | 원문 쿼리 | 질문에 직접 답하는 bullet 2~5개 |

의도는 **답변 경로를 나누지 않음** — [`generator.py`](../backend/rag/generator.py) 프롬프트 지시만 바뀜.

## LLM RAG 답변 (`rag/generator.py`)

1. 검색된 청크(`title`, `section_title`, 본문)를 context로 전달.
2. **컨텍스트 밖 사실 금지**; 부족하면 `__UNKNOWN__` → API `unknown` 문구.
3. 출력 형식: 헤더 1줄 + bullet + `출처: {title}` (URL은 `citations`).
4. LLM 실패 시 `unknown` 고정 문구 ([`answer_composer.unknown_message`](../backend/rag/answer_composer.py)).

## Source-only 정책 (파인튜닝 불필요)

| 규칙 | 구현 |
|------|------|
| 출처에 없는 내용 답 금지 | LLM context-only 프롬프트 |
| 관련 없으면 모른다 | `band=low/none` 또는 LLM `__UNKNOWN__` |
| 애매하면 먼저 확인 | `band=medium` → `confirm_needed` |
| 참고 링크 중복 금지 | `source_url` 기준 citation dedupe |

임계값: `CHATBOT_DISTANCE_HIGH_MAX`, `CHATBOT_DISTANCE_LOW_MAX` (cosine distance).

**인덱스 갱신**: 청킹·메타 변경 후 `POST /admin/reindex` 또는 `build_index(force=True)`.

## API

### `POST /chat`

```json
{ "message": "외국인 등록에 필요한 서류가 뭐야?", "lang": "ko" }
```

| 필드 | 설명 |
|------|------|
| `status` | `answered` \| `confirm_needed` \| `unknown` |
| `answer` | LLM 생성 본문 (또는 unknown) |
| `citations` | 검색 청크 출처 (URL dedupe) |
| `model_used` | LLM 답변 사용 여부 |

- `GET /health`
- `POST /admin/reindex`

## 환경 변수

| 변수 | 기본 | 설명 |
|------|------|------|
| `CHATBOT_ANSWER_MODE` | `llm_rag` | 검색 청크 → LLM (고정) |
| `CHATBOT_TOP_K` | `4` | 검색 청크 수 |

## 검증 시나리오

| 질문 | 기대 |
|------|------|
| 외국인 등록에 필요한 서류 | 서류 bullet + 출처 |
| 재입국 허가 필요해? | 재입국 관련 bullet |
| 완전 무관 | `unknown` |

## 모델

| 역할 | 기본 |
|------|------|
| 임베딩 | `paraphrase-multilingual-MiniLM-L12-v2` |
| 답변 | `Qwen2.5-7B-Instruct` + `CHATBOT_LOAD_IN_4BIT` (CUDA NF4 / Mac fp16 MPS) |

파인튜닝 없음. faithfulness는 RAG·프롬프트·unknown 정책으로 처리.
