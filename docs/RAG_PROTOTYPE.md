# RAG + LLM 프로토타입 (`feat/initial-ui-chatbot`)

## 파이프라인

```text
sources/*.md → chunking → multilingual embeddings → Chroma
User query → retrieve top-k → HF instruct LLM (context + question) → answer + citations
```

## 모델 (기본)

| 역할 | Hugging Face |
|------|----------------|
| 임베딩 | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| 생성 | `Qwen/Qwen2.5-0.5B-Instruct` (`CHATBOT_MODEL_ID`) |

파인튜닝은 **이후** 단계. 현재는 공개 가중치 + RAG만 사용.

## API

- `GET /health`
- `POST /chat` — `{ "message", "lang": "en"|"zh"|"ja" }`
- `POST /admin/reindex` — 개발용

## 정책

- 컨텍스트 없으면 국제처 문의 유도
- LLM 실패 시 검색 문단 fallback (`model_used: false`)
