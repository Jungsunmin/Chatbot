# 보안·프라이버시 검토

**범위**: RAG FAQ 챗봇 MVP (무로그인, 커뮤니티 없음)  
**기준**: NFR-4/5, Domain DR-6, [architecture-planning.md](./architecture-planning.md)

---

## 수집 데이터 (MVP)

| 데이터 | 수집? | 목적 | 저장 |
|--------|-------|------|------|
| 계정 / 학번 | **아니오** | — | — |
| 챗 메시지 | 일시적 | RAG 답변 | 요청 RAM; **영구 로그 지양** |
| UI 언어 설정 | 클라이언트 로컬 | UX | 기기 |
| IP / 기기 | 서버 접근 로그 | 운영 | 서버 정책 |

---

## PII 최소화

- 챗에서 이름·학번·여권번호 요구하지 않음  
- Should: 전송 전 UI 경고 (“개인 식별번호를 입력하지 마세요”)  
- 백엔드: 운영에서 `query_id` + hash, 원문 message 로그 금지  
- MVP 서버 챗 기록 DB 없음  

---

## AI / FAQ 안전

| 통제 | 구현 |
|------|------|
| 소스 기반 답변만 | RAG + unknown |
| Citations | 공식 페이지 `source_url` |
| 면책 | SafetyNotice + 앱 About (Should) |
| 민감 주제 | immigration, medical, legal, … → 비단정 + 연락처 |
| 금지 생성 | 청크 없이 수수료·기한·서류 목록 생성 금지 |
| 오용 | off-topic → unknown; 일반 ChatGPT 모드 없음 |

---

## 인증·접근

| 표면 | MVP |
|------|-----|
| `/chat` | 공개 (파일럿: 네트워크 제한) |
| `/admin/reindex` | **개발 전용** — 방화벽 또는 API 키 Should |
| Chroma / md 디스크 | 서버 파일시스템 ACL |

---

## 제3자

| 서비스 | 전송 데이터 |
|--------|-------------|
| Hugging Face Hub | 모델 다운로드만 (사용자 콘텐츠 없음) |
| 학교 공식 URL | citation으로 사용자 브라우저에서 열기 |

---

## 보존·삭제

| 자산 | 보존 |
|------|------|
| PendingSession | RAM 600s |
| 서버 로그 | 수집 시 ≤30일; message 본문 지양 |
| md 소스 | Git 이력 |
| 기기 챗 UI | 앱 캐시 없으면 일시적 (MVP 캐시 지양) |

---

## 커뮤니티 / 인증 (Non-Scope)

- 커뮤니티 없음 → UGC 검수 MVP 없음  
- SSO 보류 → 포털 비밀번호 처리 없음  

---

## 파일럿 전 블로커

| ID | 항목 | 상태 |
|----|------|------|
| S-1 | 앱에 AI/FAQ 면책 표시 | Should |
| S-2 | 인터넷 공개 `/admin/reindex` 금지 | prod 유사 배포 Must |
| S-3 | message 전문 로그 금지 | Must |

---

## OPEN_QUESTIONS (보안)

- 파일럿 DPA 필요? → 담당: 팀 + 국제처  
- 백엔드 온프레미만 vs 클라우드 GPU? → deploy skill  

**다음 검토**: 인증, 챗 기록, 외부 LLM API 추가 시.
