# 테스트 전략

**기준**: [requirements-decomposition.md](./requirements-decomposition.md) AC-1~7, [mvp-scope-planning.md](./mvp-scope-planning.md) 릴리스 기준

---

## 테스트 수준

| 수준 | 범위 | 도구 |
|------|------|------|
| **단위** | intent, expander, banding, citation dedupe, frontmatter parse | `pytest` |
| **통합** | retrieve(query), 모바일 없이 `/chat` | `pytest` + TestClient |
| **E2E** | LAN에서 Expo → backend | 수동 + 체크리스트 |
| **파일럿** | 유학생 10명+, 2주 | 스프레드시트 + AC 지표 |

---

## 핵심 경로

1. 인덱스 존재 → health OK  
2. EN document_list 질문 → answered + citation + 괄호 안 한국어 용어  
3. 무관 질문 → unknown (환각 없음)  
4. Medium relevance → confirm → yes → answered  
5. confirm no → unknown  
6. zh/ja UI 문자열 표시; API `lang` zh/ja  
7. md 수정 → reindex → 답변 변경  

---

## i18n / FAQ / RAG

| 케이스 | 기대 결과 |
|--------|-----------|
| UI lang en, 질문 en | `response_lang` en; 답변 en |
| UI lang ko, 질문 ko | 필요 시 (한국어) 병기 포함 ko 답변 |
| 청크 없음 | unknown, 목록 임의 생성 없음 |
| immigration 주제 | SafetyNotice 포함 (Should) |
| citation | `source_url`로 공식 페이지 열림 |

---

## 샘플 Q&A 매트릭스 (T20) — Visa Phase 1

| # | 언어 | 카테고리 | 예시 질문 | 통과? |
|---|------|----------|-----------|-------|
| 1 | en | visa | What documents for alien registration? | |
| 2 | ko | visa | 외국인등록 제출 서류? | |
| 3 | en | visa | How to extend stay period? | |
| 4 | ko | visa | 체류기간 연장 방법? | |
| 5 | en | visa | Part-time work permit for students? | |
| 6 | zh | visa | 外国人登录需要什么材料？ | |
| 7 | ja | visa | 再入国許可の申請方法は？ | |
| 8 | en | visa | Address change report procedure | |
| 9 | ko | visa | 외국인등록증 재발급 서류? | |
| 10 | en | off-topic | Weather in Seoul today? | unknown |
| … | | | ≥10 total (visa 위주) | |

상세 시트: [docs/QA_VISA_PILOT.md](../../QA_VISA_PILOT.md)

---

## 자동 스모크 (CI Should)

```bash
cd backend && pip install -r requirements.txt && pytest tests/ -q
# 추후: data/sources/**/*.md frontmatter lint
```

---

## 파일럿 계획

| 항목 | 내용 |
|------|------|
| 대상 | 건국대 유학생 10명+ |
| 기간 | 2주 |
| 지표 | citation 비율, unknown 비율, 오답 신고 |
| 피드백 | Google form; PII 불필요 |

---

## 릴리스 게이트 (MVP 1.0)

- [ ] 요구사항 문서 AC-1~7  
- [ ] 핵심 경로 수동 통과  
- [ ] main 브랜치 `pytest` green  
- [ ] 프라이버시: [security-privacy-review.md](./security-privacy-review.md) 블로커 해소  
- [ ] 앱 AI 고지/면책 (Should)  
- [ ] Reindex runbook 게시 ([deployment-operations.md](./deployment-operations.md))
