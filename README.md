# KU International Student RAG FAQ Chatbot

건국대 외국인 유학생용 **RAG FAQ 챗봇** (Visa Phase 1).

## 구조

- `backend/` — FastAPI + Chroma + Hugging Face LLM
- `mobile/` — Expo 챗 UI (ko/en/zh/ja)
- `docs/agentic/` — 기획·Skill 산출물
- `backend/data/sources/visa/` — 한국어 curated md (SSOT)

## 빠른 시작

```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/build_index.py
./scripts/dev_server.sh
# 또는: uvicorn app.main:app --host 0.0.0.0 --port 8001
```

```bash
cd mobile && npm install && cp .env.example .env
# EXPO_PUBLIC_API_URL=auto  (실기기: Expo가 Mac IP 자동 감지)
npm start
```

상세: [docs/RAG_SOURCES.md](docs/RAG_SOURCES.md), [docs/agentic/skill-outputs/task-breakdown.md](docs/agentic/skill-outputs/task-breakdown.md)

cicd test
cicd test22
cicde test33
