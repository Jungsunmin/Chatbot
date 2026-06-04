# 프론트엔드 구현 (Frontend Implementation)

**범위**: Expo (React Native) — **챗 + i18n + citation 링크**만  
**상태**: 기획 완료 · T13 API 이후 T16–T18

---

## 기술 스택

| 계층 | 선택 |
|------|------|
| 프레임워크 | Expo SDK, React Native |
| API | `fetch` → `EXPO_PUBLIC_API_URL` |
| i18n | `src/i18n/strings.ts` (ko/en/zh/ja) |
| 링크 | `citation.source_url` → `openSourceLink` |

---

## 화면 (MVP)

| 화면 | FR | Task |
|------|-----|------|
| 언어 선택 / 설정 | FR-4.2, FR-5.4 | T18 |
| 챗 | FR-5.1 | T16 |
| 확인 다이얼로그 | FR-5.2 | T17 |
| unknown / 오류 | FR-5.3 | T12, T16 |

**범위 외**: 온보딩 대시보드 3상태, Push, 지도, 커뮤니티, 가이드북 리더 앱

---

## API 연동

- `sendChat(message, lang)` → 1차 턴  
- `sendChatConfirm(pendingId, confirm, lang)` → 2차 턴  
- 모든 요청에 **`lang`** 전달 (사용자 선택)  
- `status`에 따라: 답변 표시, 예/아니오, unknown 템플릿  

```typescript
// 계약: mobile/src/api/client.ts
export type AnswerStatus = "answered" | "confirm_needed" | "unknown";
```

---

## i18n 규칙

- 사용자 노출 문자열은 `strings.ts`에만 — 4언어  
- 컴포넌트에 한국어만 하드코딩 금지  
- `lang` 상태와 API payload 동기화  

---

## 기기 테스트

- 시뮬레이터: `127.0.0.1`은 실기기에서 실패 → `.env`에 LAN IP  
- `docs/EXPO_DEVICE.md` 참고  
- QR 실패 시 Tunnel 모드  

---

## 검증

```bash
cd mobile && npm install && cp .env.example .env
# EXPO_PUBLIC_API_URL=http://<LAN-IP>:8001
npm start
```

수동: 영어 질문 → 답변 + citation 링크 → URL 열기 확인.

---

## 제약

- 클라이언트에서 RAG·임베딩 없음  
- MVP에서 서버에 챗 기록 저장 없음  
- 의존성 최소; 기존 `App.tsx` 스타일 유지  

**선행**: [backend-implementation.md](./backend-implementation.md) `/chat` 안정화
