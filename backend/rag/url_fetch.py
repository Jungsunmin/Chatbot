"""Google Sites 등 단일 URL 본문 추출 (single_page_only)."""
from __future__ import annotations

import re

import httpx
from bs4 import BeautifulSoup

# 사이트 공통 네비(본문에서 제외할 짧은 메뉴 라벨)
_NAV_NOISE = re.compile(
    r"^(HOME|Search this site|Skip to .+|학부 유학생 KU 가이드북)$",
    re.I,
)


def fetch_page_text(url: str, timeout: float = 30.0) -> str:
    """URL HTML → 플레인 텍스트(마크다운 유사)."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ko,en;q=0.9",
    }
    with httpx.Client(follow_redirects=True, timeout=timeout) as client:
        resp = client.get(url.split("?")[0], headers=headers)  # authuser 쿼리 제거
        resp.raise_for_status()
        html = resp.text

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Google Sites: 텍스트가 많은 div 선택
    root = soup.body or soup
    candidates = [root] + soup.find_all("div", class_=lambda c: c and "sites-" in str(c))
    content_el = max(candidates, key=lambda el: len(el.get_text(strip=True)))

    lines: list[str] = []
    for el in content_el.find_all(["h1", "h2", "h3", "h4", "p", "li", "td"]):
        t = el.get_text(" ", strip=True)
        if not t or len(t) < 2 or _NAV_NOISE.match(t):
            continue
        if el.name.startswith("h"):
            level = min(int(el.name[1]), 4)
            lines.append("#" * level + " " + t)
        elif el.name == "li":
            lines.append(f"- {t}")
        else:
            lines.append(t)

    text = "\n\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    # 구조 태그에 내용이 거의 없으면 본문 전체 텍스트에서 블록 추출
    if len(text) < 200:
        raw_lines = [ln.strip() for ln in content_el.get_text("\n", strip=True).splitlines()]
        raw_lines = [ln for ln in raw_lines if ln and len(ln) > 3 and not _NAV_NOISE.match(ln)]
        # 연속 중복·순수 메뉴 나열 완화: 길이 8자 이상 또는 문장 부호 포함
        kept = [ln for ln in raw_lines if len(ln) >= 8 or re.search(r"[.!?。]", ln)]
        text = "\n\n".join(kept)

    return text
