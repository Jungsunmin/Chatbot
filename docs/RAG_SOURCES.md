# RAG URL 소스 (KU Guidebook)

## 등록 파일

`backend/data/sources/urls.yaml`

현재 3건 (`rag_scope: single_page_only` — 하위 링크 자동 크롤링 없음):

| label | title |
|-------|--------|
| `home` | KU Guidebook Home |
| `visa_alien_registration_card` | 체류 비자 / 외국인등록증 |
| `international_student_insurance` | 유학생 보험 |

## 갱신 절차

```bash
cd backend
source .venv/bin/activate
python scripts/ingest_urls.py   # URL → data/sources/web/*.md
python scripts/build_index.py     # Chroma 재구축
```

API 실행 중이면: `curl -X POST http://127.0.0.1:8001/admin/reindex`

## URL 추가 방법

`urls.yaml`의 `sources:` 에 동일 필드로 항목 추가 후 위 절차 반복.

## Google Sites 참고

일부 페이지는 HTML만으로 본문이 짧을 수 있음. 그 경우 해당 페이지를 브라우저에서 복사해 `data/sources/web/{label}_ko.md` 본문을 수동 보강.
