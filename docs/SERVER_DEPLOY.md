# 학교 서버 배포

## 권장 사양 (RAG-only MVP)

- RAM 16GB+, SSD 30GB+
- GPU 8GB+ (선택, 추론 가속)

## 배포 절차

```bash
git clone <your-repo-url> /opt/chatbot
cd /opt/chatbot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 팀 제공 PDF/md → allowlist 폴더에 복사
# config/sources.yaml 의 allowed_roots 확인

python scripts/ingest_local.py
python scripts/build_chunks.py
python scripts/build_index.py

# API (systemd 또는 screen)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# UI
streamlit run app/streamlit_app.py --server.port 8501
```

## 재인덱스

문서 추가·수정 후:

```bash
python scripts/ingest_local.py && python scripts/build_chunks.py && python scripts/build_index.py
```

`data/index/`, `models/` 는 git에 올리지 않습니다.

## allowlist 변경

`config/sources.yaml` 수정 후 ingest부터 다시 실행.
