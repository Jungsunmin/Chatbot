# 코드 리뷰

**용도**: PR 머지 전 체크리스트 — KU RAG 챗봇 MVP

---

## 범위 정합

- [ ] [task-breakdown](./task-breakdown.md) **한 개** ID 및 Implementation Prompt와 일치  
- [ ] 대시보드, Push, SSO, 실시간 크롤, 커뮤니티 미포함 (승인 없이)  
- [ ] 동작·API 계약 변경 시 agentic 문서 갱신  

---

## 백엔드

- [ ] `/chat`이 외부 URL로 본문 fetch 하지 않음  
- [ ] SelectedContext만 사용; unknown 경로 정확  
- [ ] `preserve_terms` / SensitiveTopic 프롬프트 반영  
- [ ] 청크 밖 수수료·기한·서류 목록 생성 없음  
- [ ] citation `source_url` 기준 dedupe  
- [ ] Pending session TTL; 메모리 무한 증가 없음  
- [ ] 비밀은 env만; repo에 API 키 없음  

---

## 프론트엔드

- [ ] 모든 `/chat` 호출에 `lang` 전달  
- [ ] confirm 흐름에서 `pending_id` 처리  
- [ ] i18n: ko/en/zh/ja 키 누락 없음  
- [ ] 오류: 네트워크 vs unknown 구분  

---

## 데이터 / 콘텐츠

- [ ] 신규 소스 frontmatter v2 유효  
- [ ] 청크 변경 시 reindex 문서화  
- [ ] 한국어 본문이 공식 소스와 일치 (스팟 체크)  

---

## 품질

- [ ] 테스트 추가 또는 PR에 수동 검증 기록  
- [ ] 로그에 PII 없음  
- [ ] 비즈니스 로직이 뻔하지 않으면 한국어 주석  

---

## 리뷰 결과 템플릿

```md
## 요약
(1–2문장)

## 블로커
- ...

## 권장 사항
- ...

## 수행한 검증
- [ ] pytest / 수동 단계
```

**상태**: 체크리스트 준비됨 — 구현 시작 후 PR마다 적용.
