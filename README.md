# Exchange Student Chatbot

교환학생·유학생을 위한 **RAG 기반** 학교 안내 챗봇 (외부 LLM API 없음).

## 기능

- **allowlist** 로컬 폴더(·선택적 허용 URL)만 수집·검색
- **멀티턴**: 카테고리별 필수 정보(clarify 폼) → RAG → 답변 + 출처
- **decoder-only** 로컬 생성 (모델 미로드 시 검색 문단만 반환)

## 빠른 시작 (학교 서버·로컬)

```bash
cd Chatbot
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 1) 문서를 data/sources/official/ 에 넣기 (또는 config/sources.yaml 경로 수정)

# 2) RAG 인덱스
python scripts/ingest_local.py
python scripts/build_chunks.py
python scripts/build_index.py

# 3) API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 4) UI (다른 터미널)
streamlit run app/streamlit_app.py
```

## 설정

- [`config/sources.yaml`](config/sources.yaml) — 허용 폴더·도메인·seed URL (팀이 나중에 채움)
- [`data/schemas/`](data/schemas/) — 카테고리별 clarify 슬롯
- 선택: [`data/sources/manifest.csv`](data/sources/manifest.csv) — `filename,category,lang,verified`

## 환경 변수

| 변수 | 설명 |
|------|------|
| `CHATBOT_MODEL_ID` | 기본 `Qwen/Qwen2.5-0.5B-Instruct` |

## 문서

- [**data/status.md**](data/status.md) — **진행 현황·추후 할 일 (SSOT, 작업 전 필독)**
- [docs/RAG_PIPELINE.md](docs/RAG_PIPELINE.md)
- [docs/SOURCE_ALLOWLIST.md](docs/SOURCE_ALLOWLIST.md)
- [docs/SERVER_DEPLOY.md](docs/SERVER_DEPLOY.md)
- [docs/SLOT_SCHEMAS.md](docs/SLOT_SCHEMAS.md)

## LoRA

이번 MVP는 **RAG-only**입니다. LoRA 파인튜닝은 RAG 품질 검증 후 별도 단계입니다.
