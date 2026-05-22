"""MVP: 키워드 기반 category 추정."""
from __future__ import annotations

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "course_registration": [
        "register",
        "registration",
        "course",
        "수강",
        "신청",
        "enroll",
    ],
    "housing": ["dorm", "housing", "기숙사", "숙소", "residence"],
    "visa_immigration": ["visa", "immigration", "비자", "체류", "alien"],
    "health_insurance": ["insurance", "health", "보험", "의료"],
    "arrival_orientation": ["orientation", "arrival", "오리엔테이션", "입학"],
    "scholarship_tuition": ["scholarship", "tuition", "장학", "등록금"],
    "campus_facilities": ["library", "cafeteria", "시설", "도서관"],
    "student_services": ["office", "service", "국제처", "international"],
    "emergency_contacts": ["emergency", "urgent", "긴급", "119"],
}


def detect_category(message: str) -> str:
    lower = message.lower()
    best = "general"
    best_score = 0
    for cat, keys in CATEGORY_KEYWORDS.items():
        score = sum(1 for k in keys if k in lower)
        if score > best_score:
            best_score = score
            best = cat
    return best
