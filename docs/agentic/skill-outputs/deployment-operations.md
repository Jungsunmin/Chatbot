# 배포·운영

**범위**: 챗봇 MVP 파일럿 — Expo 빌드 + backend LAN/VPS (스토어 풀앱 Non-Scope)

---

## 환경

| 환경 | 백엔드 | 모바일 | 데이터 |
|------|--------|--------|--------|
| **local** | `uvicorn :8001` | Expo 시뮬레이터 / 기기 LAN | `backend/data/` |
| **pilot** | VM 1대 또는 Mac 상시 | TestFlight / 내부 APK | 동기화 md + index |
| **prod** | TBD | 스토어 | MVP 범위 외 |

---

## 릴리스 단계 (파일럿)

1. 콘텐츠: 한국어 md PR 머지 → 파일럿 서버에서 `build_index`  
2. 백엔드: FastAPI + venv + `.env` (MODEL_ID, paths) 배포  
3. 스모크: `GET /health`, 샘플 `/chat` curl  
4. 모바일: `EXPO_PUBLIC_API_URL`을 파일럿 HTTPS/LAN으로 설정  
5. 테스터(10명+)에 빌드 배포  
6. 모니터링: 오류율, unknown 비율, 수동 피드백 폼  

---

## 비밀 정보

| 비밀 | 위치 |
|------|------|
| `CHATBOT_MODEL_ID`, `CHATBOT_*` 임계값 | `backend/.env` (git 제외) |
| HF token (rate limit 시) | `HF_TOKEN` env 선택 |
| Reindex admin | `ADMIN_API_KEY` Should |

---

## 콘텐츠 갱신 (runbook)

```bash
# 1. backend/data/sources/ 하위 한국어 md 편집
# 2. 서버에서:
cd backend && source .venv/bin/activate
python scripts/build_index.py
# 또는: curl -X POST https://pilot-host/admin/reindex -H "X-Admin-Key: ..."
# 3. 확인:
curl -s https://pilot-host/health
```

문서: `docs/RAG_SOURCES.md`  
담당: 콘텐츠 팀 + dev reindex  

---

## 롤백

| 실패 | 조치 |
|------|------|
| 잘못된 md 머지 | git revert + reindex |
| 잘못된 index | `data/index/` 백업 tarball 복원 |
| 잘못된 모델 배포 | `.env` MODEL_ID 되돌리기 + 재시작 |
| 앱 API URL 오류 | `EXPO_PUBLIC_API_URL` 수정 + 재빌드 |

---

## 모니터링 (파일럿 최소)

- `/health` uptime (cron)  
- 디스크: Chroma + 모델 캐시 크기  
- 프로세스 메모리 (LLM OOM 알림)  

PII 대시보드 없음.

---

## 국제처 게이트

- MVP = **비공식** 파일럿; 국제처 승인 없이 공식 KU 브랜딩 금지  
- 공식 협력 시 → [DECISIONS.md](../DECISIONS.md) 갱신  

---

## 하드웨어 참고

- Mac dev: 1.5B fp16 MPS ~3GB+  
- Linux NVIDIA: 4bit 선택  
- CPU-only: 느림; 파일럿 비권장  

[architecture-planning.md](./architecture-planning.md) 트레이드오프 참고.
