# ASSUMPTIONS.md

아직 검증되지 않은 가정. 최종 갱신: 2026-05-26

---

## KU 가이드북 구조화 가능

- **Assumption**: 가이드북을 **섹션·앵커 단위**로 추출해 앱·CMS에 넣을 수 있다.
- **Why it matters**: FR-3 콘텐츠 이식·3언어 번역의 기반.
- **Risk if wrong**: 수동 재작성·일정 대폭 지연.
- **How to verify**: 가이드북 원본(PDF/HTML) 포맷 확인, 파일럿 3섹션 이식.

---

## 가이드북 MVP 섹션 목록(초안)

- **Assumption**: MVP Must 섹션 = Welcome, Visa/Immigration, Enrollment, Housing, Academic Calendar, Emergency Contacts.
- **Why it matters**: 번역·개발 범위 산정.
- **Risk if wrong**: 핵심 누락 또는 번역 과부하.
- **How to verify**: 팀·국제처(추후) 우선순위 확정.

---

## Push 인프라

- **Assumption**: **FCM + APNs** 로 학사 일정 Push 구현 가능.
- **Why it matters**: FR-4.
- **Risk if wrong**: iOS만/test 환경 제한.
- **How to verify**: Apple·Google 개발자 계정, 테스트 디바이스 Push E2E.

---

## 일정 데이터 소스

- **Assumption**: 수강신청·비자 연장 일정은 **학교 공개 학사력 + 수동 템플릿**으로 MVP 채운다(API 없음).
- **Why it matters**: Push 정확도.
- **Risk if wrong**: 잘못된 마감일 알림.
- **How to verify**: 2025–2026 학사일정 PDF/웹과 대조, 국제처 확인(추후).

---

## 캠퍼스 지도 데이터

- **Assumption**: 건물·기관 데이터를 **학교 제공 목록 또는 OSM/수동 JSON**으로 확보 가능.
- **Why it matters**: FR-5; MVP Should.
- **Risk if wrong**: 길찾기 품질 저하, Should 연기.
- **How to verify**: 국제처·총무·시설팀 문의 또는 공개 캠퍼스 맵 조사.

---

## FAQ AI 구현

- **Assumption**: MVP AI는 **FAQ-only 또는 소규모 RAG**(가이드북+FAQ), 외부 API 사용 시에도 **출처 강제**.
- **Why it matters**: FR-6, 오안내 리스크.
- **Risk if wrong**: 스토어·학교 정책·비용 이슈.
- **How to verify**: PoC 50질의, 오답률·출처 누락률 측정.

---

## 인증(MVP)

- **Assumption**: MVP는 **이메일/소셜 게스트** 또는 **기기 로컬 프로필**로 시작하고, **KU SSO는 2차**.
- **Why it matters**: 일정·커뮤니티 개인화.
- **Risk if wrong**: 재설치 시 데이터 유실.
- **How to verify**: OPEN_QUESTIONS에서 인증 방식 확정.

---

## 커뮤니티·룸메이트

- **Assumption**: **MVP Non-Scope**; 신고·모더레이션·개인정보 동의 없이 오픈하지 않는다.
- **Why it matters**: FR-7.2–7.3, 안전 리스크.
- **Risk if wrong**: 초기부터 범위 팽창.
- **How to verify**: MVP 릴리스 기준에 커뮤니티 제외 유지.

---

## 한국어 UI 미포함

- **Assumption**: 사용자 명시 3언어는 **EN/ZH/JA**; 한국어 UI는 **요구 없음**(OPEN에서 재확인).
- **Why it matters**: 번역 범위.
- **Risk if wrong**: 한국어 유학생(귀화 전) 이탈.
- **How to verify**: 타깃 사용자 인터뷰 1회.

---

## 비공식 MVP 배포

- **Assumption**: 1.0은 **내부·파일럿** 배포 가능; 스토어 공개·학교 로고는 **검수 후**.
- **Why it matters**: 국제처 협업 추후 결정과 정합.
- **Risk if wrong**: 브랜드·상표 이슈.
- **How to verify**: 학교 가이드라인·국제처 사전 문의(추후).
