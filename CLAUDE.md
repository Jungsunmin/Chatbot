# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

건국대학교 외국인 유학생용 RAG FAQ 챗봇 (Visa Phase 1). Korean-curated markdown files are the single source of truth (SSOT) for all visa/immigration guidance.

## Commands

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Build Chroma index from source docs (run once, then on doc changes)
python scripts/build_index.py

# Dev server (binds 0.0.0.0 — required for Expo real-device access)
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Force reindex without restart
curl -X POST http://localhost:8001/admin/reindex

# Run all tests
python -m pytest tests/

# Run a single test file
python -m pytest tests/test_doc_router.py -v
```

### Mobile

```bash
cd mobile
npm install
cp .env.example .env   # EXPO_PUBLIC_API_URL=http://<server-ip>:8001

npm start              # Expo dev server (LAN auto-detect)
npm run start:tunnel   # ngrok tunnel (cross-network)

# Internal distribution build (Android APK, no Play Store needed)
npm install -g eas-cli && eas login
eas build:configure
eas build --platform android --profile preview
```

## Architecture

### RAG Pipeline (backend)

Every `/chat` request follows this decision tree:

```
build_query()          ← language detect + intent classify + bridge keywords
       ↓
resolve_doc_route()    ← keyword rules → specific doc_id
       ↓
  doc_id match?
  ├── YES → load_source_by_doc_id() → full .md body → LLM → answer
  └── NO  → Retriever.search_with_band() → Chroma vector search
                  ↓
             relevance band
             ├── high/medium → _build_answer() → LLM → answer
             └── low/none    → "unknown" response
```

**Two answer paths:**
1. **Direct route**: `doc_router` matches query → full markdown loaded → passed to `generate_answer_from_source()`. No Chroma involved.
2. **Chunk retrieval**: Chroma cosine search → top-K chunks → `generate_answer()`. Used when no doc_id matches.

`_build_answer()` checks intent first: `document_list` queries try `verbatim_composer` (no LLM) before falling back to LLM.

### Key Modules

| Module | Role |
|---|---|
| `rag/doc_router.py` | Keyword regex → `DocRoute(doc_id, subcategory)`. More specific patterns listed first. |
| `rag/intent.py` | Classifies query as `document_list / procedure / deadline / general`. Affects reranking and chunk narrowing. |
| `rag/query_pipeline.py` | Builds `Query` dataclass: detects language, resolves `response_lang`, appends `_KO_BRIDGE` Korean admin keywords for non-Korean queries. |
| `rag/retriever.py` | Chroma query + heuristic rerank. For `document_list` intent, narrows to single submission-section chunk from the dominant `doc_id`. |
| `rag/indexer.py` | Reads `data/sources/**/*.md`, parses YAML frontmatter, calls `chunk_markdown()`, embeds, writes to Chroma. |
| `rag/chunking.py` | Splits on `##` headers and Korean subsection markers (`가./나./라.`). Produces `Chunk.text` (display) and `Chunk.embed_text` (contextual prefix + text for embedding). |
| `rag/generator.py` | Calls HuggingFace model via `model_loader`. Outputs `__UNKNOWN__` marker when query is out-of-scope. |
| `rag/model_loader.py` | Singleton LLM loader. `CHATBOT_PRELOAD_MODELS=true` loads at startup; otherwise lazy on first `/chat`. |
| `rag/prompt_templates.py` | 5-section structured prompt (ko/en/zh/ja). `build_system_prompt()` + `build_user_prompt()` used by both answer paths. |
| `rag/answer_composer.py` | Hard-coded fixed phrase: `unknown_message()`. No LLM involved. |
| `rag/verbatim_composer.py` | For `document_list` intent: extracts document lists from chunks without calling LLM. Falls back to LLM if extraction fails. |

### Answer Generation Details

`generator.py` constants that affect output quality:
- `_MAX_NEW_TOKENS = 768` — max LLM output length
- `do_sample=False` — greedy decode (deterministic)
- `torch.manual_seed(42)` — reproducibility on MPS

`prompt_templates.py` defines the 5-section format per language:
**상황 → 신청 장소 → 대상 → 준비 서류 → 절차 → 주의사항 → 다음 단계 → 출처**

- Korean answers use formal polite sentence form (존댓말, ~습니다/~세요)
- Sections with no document content are omitted entirely (not flagged as missing)
- Other languages still use bullet-list format
- If the document cannot answer at all, the LLM outputs `__UNKNOWN__` which `_finalize_answer()` converts to the `unknown_message()` fixed phrase

### Source Documents

All source docs live in `backend/data/sources/visa/` as `<doc_id>_ko.md`.

Frontmatter fields that matter:
- `doc_id` — must match the `doc_id` string used in `_ROUTE_RULES` in `doc_router.py`
- `source_title` / `title` — displayed in citations
- `source_url` — canonical HiKorea/immigration URL
- `preserve_terms` — list of Korean admin terms the LLM must not translate
- `sensitive_topic` — controls `safety_notice` in response

### Relevance Bands

| Band | Cosine distance | Behavior |
|---|---|---|
| high | ≤ 0.35 | Answer returned |
| medium | ≤ 0.55 | Answer returned |
| low / none | > 0.55 | "Unknown" response (no hallucination) |

Thresholds are tunable via `CHATBOT_DISTANCE_HIGH_MAX` / `CHATBOT_DISTANCE_LOW_MAX` env vars.

### Cross-lingual Retrieval

Since all source docs are Korean, non-Korean queries are augmented with Korean admin keywords before embedding (`_KO_BRIDGE` table in `query_pipeline.py`). This bridges the cross-lingual gap of the multilingual MiniLM embedder.

### Mobile

Single-file app (`mobile/App.tsx`) + `src/api/client.ts` (fetch wrapper) + `src/i18n/strings.ts` (4-language UI strings). No router — `Screen` state drives `"home" | "chat"` views. `EXPO_PUBLIC_API_URL=auto` lets Expo detect the Mac LAN IP automatically for real-device testing; set to an explicit URL for server deployments.

## Environment Variables (backend)

| Variable | Default | Purpose |
|---|---|---|
| `CHATBOT_MODEL_ID` | `Qwen/Qwen2.5-1.5B-Instruct` | HuggingFace model |
| `CHATBOT_EMBEDDING_MODEL` | `paraphrase-multilingual-MiniLM-L12-v2` | Sentence-transformers embedder |
| `CHATBOT_LOAD_IN_4BIT` | `true` | 4-bit NF4 quant (CUDA). Mac uses fp16 MPS automatically |
| `CHATBOT_PRELOAD_MODELS` | `true` | Load models at startup vs. first request |
| `CHATBOT_TOP_K` | `4` | Chunks retrieved per query |
| `CHATBOT_MAX_QUERY_LENGTH` | `300` | Max characters accepted in `ChatRequest.message` |
| `CHATBOT_DISTANCE_HIGH_MAX` | `0.35` | High-band ceiling |
| `CHATBOT_DISTANCE_LOW_MAX` | `0.55` | Medium-band ceiling (above = no answer) |

## Adding a New Document

1. Create `backend/data/sources/visa/<doc_id>_ko.md` with YAML frontmatter (`doc_id`, `source_title`, `source_url`, `type`).
2. Add a routing rule to `_ROUTE_RULES` in `rag/doc_router.py` — more specific patterns must go above general ones.
3. Re-run `python scripts/build_index.py` (or `POST /admin/reindex`).
4. Add tests in `tests/test_doc_router.py` and `tests/test_retriever_routing.py`.

## Agentic Workflow

Implementation changes should follow the stages in `.cursor/AGENTS.md`. Before implementing, consult `docs/agentic/context_packet.md`, `DECISIONS.md`, `ASSUMPTIONS.md`, and `OPEN_QUESTIONS.md`. Record new decisions or assumptions in those files when behavior changes.
