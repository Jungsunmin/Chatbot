# Konkuk University — International Student App (Prototype)

건국대 외국인 유학생용 앱 **초기 구현** 브랜치: Expo UI + RAG FAQ 챗봇 (Hugging Face 로컬 LLM).

## 구조

| 경로 | 설명 |
|------|------|
| `backend/` | FastAPI, Chroma RAG, HF `transformers` 생성 |
| `mobile/` | Expo (React Native) — 홈·언어·챗 화면 |
| `docs/agentic/` | 기획·Skill 산출물 |

## 빠른 시작

### 1. 백엔드

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/build_index.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

> **포트 8000** 이 Docker 등에 점유된 경우 **8001** 사용. 모바일 `.env`의 `EXPO_PUBLIC_API_URL`도 맞춰 주세요.

```bash
# (참고) 8000이 비어 있으면 8000 사용 가능
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

첫 `/chat` 요청 시 HF 모델 다운로드·로드가 발생할 수 있습니다. GPU 없으면 CPU로 동작(느릴 수 있음).

### 2. 모바일 (Expo)

```bash
cd mobile
npm install
cp .env.example .env
# 실제 기기: .env 에 Mac LAN IP (127.0.0.1 사용 금지)
# EXPO_PUBLIC_API_URL=http://192.168.x.x:8001
npm start
# QR/LAN 실패 시: npm run start:tunnel
```

**QR이 안 되면** → [docs/EXPO_DEVICE.md](docs/EXPO_DEVICE.md) (Expo Go로 스캔, Tunnel 모드, API URL)

## RAG 데이터

- URL 목록: `backend/data/sources/urls.yaml`
- URL 가져오기: `python scripts/ingest_urls.py` → `data/sources/web/*.md`
- 인덱스: `python scripts/build_index.py` 또는 `POST /admin/reindex`

## 기획 문서

- [`docs/agentic/context_packet.md`](docs/agentic/context_packet.md)

## 브랜치

- `main` — 기획·Agentic 문서
- `feat/initial-ui-chatbot` — UI + RAG 챗봇 스파이크
