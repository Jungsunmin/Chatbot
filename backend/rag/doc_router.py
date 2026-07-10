"""질문 → doc_id/subcategory 라우팅 (규칙 기반, 구체적 패턴 우선)."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class DocRoute:
    doc_id: str
    subcategory: str


# (정규식, {언어: doc_id}, subcategory) — 위에서부터 먼저 매칭
# 구체적·예외 패턴을 상위에, 일반 패턴을 하위에 배치
# doc_id가 한 언어로만 큐레이션된 토픽은 dict에 그 언어 하나만 넣으면 됨
_ROUTE_RULES: list[tuple[str, dict[str, str], str]] = [
    # 재발급 / 분실 / 훼손 — 변경보다 먼저 매칭해야 함
    (
        r"재발급|분실|훼손|재\s*발급"
        r"|reissue|re[-\s]*issue|lost.*card|card.*lost|damaged.*card",
        {"ko": "alien-registration-card-reissue"},
        "arc_reissue",
    ),
    # 체류지/주소 변경 신고
    (
        r"체류지\s*변경|주소\s*변경|주소\s*신고"
        r"|address\s*change|change.*address|notify.*address|update.*address"
        r"|new\s*address|move.*address",
        {"ko": "address-change-report"},
        "address_change",
    ),
    # 인적사항/정보 변경 신고
    (
        r"정보\s*변경|인적\s*사항|성명\s*변경|체류자격\s*변경"
        r"|name\s*change|information\s*change|update\s*registration\s*info"
        r"|change.*registration.*info|update.*alien.*regist",
        {"ko": "alien-registration-change-report"},
        "arc_information_change",
    ),
    # 체류 연장 — "체류지 연장"(구어체), "extend my stay / stay renewal / visa extension" 등 포함
    (
        r"체류\s*연장|체류기간\s*연장|체류지\s*연장"
        r"|stay\s*extension|extend.*stay|stay.*extend"
        r"|extend.*period|stay.*period.*extend|visa.*extens"
        r"|stay.*renew|renewal.*stay|renew.*stay",
        {"ko": "stay-extension"},
        "stay_extension",
    ),
    # 시간제 취업 허가
    (
        r"시간제|아르바이트"
        r"|part[-\s]*time|work\s*permit|campus\s*job|student\s*work",
        {"ko": "part-time-work-permit"},
        "part_time_work",
    ),
    # 재입국 허가
    (
        r"재입국|re[-\s]*entry|reentry",
        {"ko": "re-entry-permit"},
        "re_entry_permit",
    ),
    # 하이코리아 방문 예약
    (
        r"방문\s*예약|visit\s*reservation"
        r"|hikorea.*visit|visit.*hikorea|book.*hikorea|hikorea.*book"
        r"|hikorea.*appointment|make.*appointment.*hikorea"
        r"|schedule.*hikorea|hikorea.*reserv",
        {"ko": "hikorea-visit-reservation"},
        "hikorea_visit_reservation",
    ),
    # 하이코리아 온라인 전자민원
    (
        r"전자\s*민원|온라인\s*신청|online\s*civil"
        r"|hikorea.*online|online.*hikorea|electronic.*application"
        r"|e[-\s]*application|online.*civil.*application",
        {"ko": "hikorea-online-civil-application"},
        "hikorea_online_civil_application",
    ),
    # 건강보험
    (
        r"건강보험|국민건강보험|보험료|보험"
        r"|health\s*insurance|national\s*health\s*insurance|\bnhi\b|insurance\s*premium"
        r"|健康保险|国民健康保险|保险费"
        r"|健康保険|国民健康保険|保険料",
        {
            "ko": "health-insurance-for-international-students",
            "en": "health-insurance-for-international-students",
            "zh": "health-insurance-for-international-students",
            "ja": "health-insurance-for-international-students",
        },
        "health_insurance",
    ),
    # 기숙사 신청
    (
        r"기숙사|생활관|숙소\s*신청|기숙사\s*신청"
        r"|dormitory|dorm\s*application|housing\s*application|kul?\s*house"
        r"|宿舍|宿舍申请|住宿申请"
        r"|寮|学生寮|寮申請|宿舎",
        {
            "ko": "dormitory-application",
            "en": "dormitory-application",
            "zh": "dormitory-application",
            "ja": "dormitory-application",
        },
        "dormitory_application",
    ),
   # 국제처 외국인학생센터 홈페이지 활용법
    (
        r"국제처.*홈페이지|외국인학생센터.*홈페이지|외국인학생센터|포털|홈페이지\s*사용"
        r"|international\s*student\s*center.*website|isc.*website|portal.*log.?in"
        r"|国际处.*网站|外国人学生中心.*网站|留学生中心.*网站|门户"
        r"|国際処.*ホームページ|外国人学生センター.*ホームページ|留学生センター.*サイト|ポータル",
        {
            "ko": "international-student-center-website-user-guide",
            "en": "international-student-center-website-user-guide",
            "zh": "international-student-center-website-user-guide",
            "ja": "international-student-center-website-user-guide",
        },
        "isc_website_guide",
    ),
    ]

# 외국인 등록(최초) — 변경·재발급 질문은 위 규칙에서 먼저 걸러짐
# 접두사 매칭으로 "registeration / registrant" 등 오타·변형 허용
# foreign(er) 모두 포함
_ALIEN_REGISTRATION_RE = re.compile(
    r"외국인\s*등록|외국인등록|alien\s*regist|foreign(?:er)?\s*regist",
    re.I,
)
_ALIEN_REGISTRATION_EXCLUDE_RE = re.compile(
    r"재발급|변경|재발행|reissue|change|lost|damaged",
    re.I,
)
_ALIEN_REGISTRATION_DOC_IDS: dict[str, str] = {
    "ko": "alien-registration",
    "en": "stay-visa-alien-registration-card",
}


def _pick_doc_id(doc_ids: dict[str, str], lang: str) -> str | None:
    """요청 언어의 doc_id 우선, 없으면 큐레이션된 다른 언어로 폴백."""
    if lang in doc_ids:
        return doc_ids[lang]
    return next(iter(doc_ids.values()), None)


def resolve_doc_route(query: str, lang: str = "ko") -> DocRoute | None:
    """질문 + 응답 언어에서 가장 적합한 가이드북 doc_id 추정. 없으면 None."""
    q = query.strip()
    if not q:
        return None

    for pattern, doc_ids, subcategory in _ROUTE_RULES:
        if re.search(pattern, q, re.I):
            doc_id = _pick_doc_id(doc_ids, lang)
            if doc_id:
                return DocRoute(doc_id=doc_id, subcategory=subcategory)

    if _ALIEN_REGISTRATION_RE.search(q) and not _ALIEN_REGISTRATION_EXCLUDE_RE.search(q):
        doc_id = _pick_doc_id(_ALIEN_REGISTRATION_DOC_IDS, lang)
        if doc_id:
            return DocRoute(doc_id=doc_id, subcategory="alien_registration")

    return None
