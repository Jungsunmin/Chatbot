"""고정 5단계 행정 안내 프롬프트 (ko/en/zh/ja)."""
from __future__ import annotations

_LANG_NAMES = {
    "ko": "Korean",
    "en": "English",
    "zh": "Chinese",
    "ja": "Japanese",
}

# 섹션 라벨·고정 문구 (응답 언어별)
_LABELS: dict[str, dict[str, str]] = {
    "ko": {
        "situation": "상황",
        "place": "신청 장소",
        "target": "대상",
        "documents": "준비 서류",
        "procedure": "절차",
        "caution": "주의사항",
        "next_steps": "다음 단계",
        "source": "출처",
        "not_in_doc": "문서에서 확인되지 않습니다",
    },
    "en": {
        "situation": "Your situation",
        "place": "Where to apply",
        "target": "Who must apply",
        "documents": "Required documents",
        "procedure": "Procedure",
        "caution": "Important notes",
        "next_steps": "Next steps",
        "source": "Source",
        "not_in_doc": "Not confirmed in the document",
    },
    "zh": {
        "situation": "您的情况",
        "place": "申请地点",
        "target": "适用对象",
        "documents": "准备材料",
        "procedure": "办理流程",
        "caution": "注意事项",
        "next_steps": "下一步",
        "source": "出处",
        "not_in_doc": "文档中未能确认",
    },
    "ja": {
        "situation": "ご状況",
        "place": "申請場所",
        "target": "対象",
        "documents": "準備書類",
        "procedure": "手続き",
        "caution": "注意事項",
        "next_steps": "次のステップ",
        "source": "出典",
        "not_in_doc": "文書で確認できません",
    },
}

_SYSTEM: dict[str, str] = {
    "ko": (
        "너는 외국인 유학생 행정 절차를 안내하는 챗봇이다.\n"
        "제공된 가이드북 문서만 사용한다. 문서에 없는 내용은 추측하지 않는다.\n"
        "답변 전체를 한국어로만 작성한다. 영어 단어·번역·괄호 병기를 넣지 않는다.\n"
        "지시된 섹션 구조와 줄바꿈·불릿 형식을 반드시 지킨다.\n"
        "동일한 정보를 절대 반복하지 않는다. 각 항목은 한 번만 언급한다."
    ),
    "en": (
        "You guide international students through Korean immigration and campus admin procedures.\n"
        "Use ONLY the provided guidebook document. Do not guess or use outside knowledge.\n"
        "Write the entire reply in English only. Follow the required section structure with line breaks and bullets.\n"
        "Never repeat the same information. Each point must appear exactly once."
    ),
    "zh": (
        "你为外国留学生提供韩国行政手续指引。\n"
        "仅使用提供的指南文档。不得猜测文档以外的内容。\n"
        "全文使用中文。请按指定结构、换行和项目符号排版。\n"
        "严禁重复相同内容，每条信息只出现一次。"
    ),
    "ja": (
        "あなたは外国人留学生の行政手続きを案内するチャットボットです。\n"
        "提供されたガイドブックのみを使用し、推測しないでください。\n"
        "全文を日本語で書き、指定の構成・改行・箇条書きに従ってください。\n"
        "同じ情報を絶対に繰り返さないこと。各情報は一度だけ記載する。"
    ),
}

# 응답 언어별 출력 형식 지시 (user 프롬프트 본문)
_FORMAT_BLOCKS: dict[str, str] = {
    "ko": """아래 문서만 사용해 답하세요. 아래 형식을 정확히 따르세요.

【언어】
- 답변 전체를 한국어로만 작성하세요.
- 영어 단어, 영어 번역, 괄호 병기(예: 외국인등록(Alien Registration))를 절대 넣지 마세요.

【형식】
- 각 섹션 제목은 **굵게** 한 줄로 쓰고, 내용은 다음 줄부터 시작하세요.
- 섹션과 섹션 사이에는 빈 줄을 한 줄 넣으세요.
- 나열 항목은 • 로 시작하고, 항목마다 줄바꿈하세요. 한 줄에 여러 항목을 붙이지 마세요.
- 문서에 없는 항목은 "{missing}" 한 줄만 적으세요.

【섹션 순서】

**{situation}**
(질문을 바탕으로 상황을 한 문장으로 요약)

**{place}**
(신청 장소 — 없으면 "{missing}")

**{target}**
(대상 — 없으면 "{missing}")

**{documents}**
(준비 서류 — 문서의 모든 항목을 • 불릿으로 빠짐없이 나열. 없으면 "{missing}")

**{procedure}**
(절차 — • 불릿으로 나열. 없으면 "{missing}")

**{caution}**
(주의사항 — • 불릿 또는 짧은 문단. 없으면 "{missing}")

**{next_steps}**
(바로 실행할 수 있는 행동 1~2가지 — 번호 목록 1. 2.)

**{source}:** {source_title}

문서로 질문에 전혀 답할 수 없으면 __UNKNOWN__ 만 출력하세요.""",
    "en": """Answer using ONLY the document below. Follow this format exactly.

【Language】
- Write the entire reply in English only.

【Format】
- Section title on its own line in **bold**. Content starts on the next line.
- Put one blank line between sections.
- Use • bullets for list items; one item per line. Do not cram multiple items on one line.
- If a section is missing from the document, write only "{missing}".

【Sections】

**{situation}**
(One sentence summarizing the user's situation)

**{place}**
(Where to apply — or "{missing}")

**{target}**
(Who must apply — or "{missing}")

**{documents}**
(All required documents as • bullets; do not omit — or "{missing}")

**{procedure}**
(Steps as • bullets — or "{missing}")

**{caution}**
(Important notes — or "{missing}")

**{next_steps}**
(1–2 concrete next actions as numbered list 1. 2.)

**{source}:** {source_title}

If the document cannot answer at all, output exactly __UNKNOWN__ and nothing else.""",
    "zh": """仅使用下方文档回答。严格按以下格式排版。

【语言】全文使用中文。

【格式】
- 各节标题单独一行加粗 **标题**，内容从下一行开始。
- 节与节之间空一行。
- 列表用 • 开头，每项一行。
- 文档无此项则只写「{missing}」。

【章节】

**{situation}**
（一句话概括用户情况）

**{place}**
（申请地点，无则「{missing}」）

**{target}**
（适用对象，无则「{missing}」）

**{documents}**
（全部材料 • 列出，无则「{missing}」）

**{procedure}**
（流程 • 列出，无则「{missing}」）

**{caution}**
（注意事项，无则「{missing}」）

**{next_steps}**
（1~2 条可立即行动，用 1. 2. 编号）

**{source}:** {source_title}

完全无法回答则只输出 __UNKNOWN__。""",
    "ja": """以下の文書のみを使用して回答してください。形式を厳守してください。

【言語】全文を日本語で書くこと。

【形式】
- 各セクション見出しは **太字** で1行、本文は次の行から。
- セクション間は空行を1行入れる。
- 箇条書きは • で、1項目1行。
- 文書にない項目は「{missing}」のみ。

【セクション】

**{situation}**
（質問に基づく状況を1文で）

**{place}**
（申請場所。なければ「{missing}」）

**{target}**
（対象。なければ「{missing}」）

**{documents}**
（準備書類を • で全て列挙。なければ「{missing}」）

**{procedure}**
（手続きを • で。なければ「{missing}」）

**{caution}**
（注意事項。なければ「{missing}」）

**{next_steps}**
（すぐできる行動1〜2つを 1. 2. で）

**{source}:** {source_title}

全く答えられない場合は __UNKNOWN__ のみ出力。""",
}


def _labels(lang: str) -> dict[str, str]:
    return _LABELS.get(lang, _LABELS["en"])


# 문서(한국어) 직후에 삽입 — 소형 모델이 문서 언어를 따르는 현상 방지.
# 한국어 답변은 한국어 문서와 일치하므로 리마인더 불필요.
_LANG_REMINDER: dict[str, str] = {
    "ko": "",
    "en": (
        "REMINDER: The document above is in Korean, but your ENTIRE answer "
        "MUST be written in ENGLISH only. Do NOT output any Korean characters."
    ),
    "zh": (
        "提醒：上方文档为韩语，但你的全部回答必须用中文书写。"
        "不得输出任何韩语字符。"
    ),
    "ja": (
        "リマインダー：上記の文書は韓国語ですが、あなたの回答は全て日本語で"
        "書いてください。韓国語の文字は一切使用しないでください。"
    ),
}


def build_system_prompt(lang: str) -> str:
    """시스템 프롬프트 — 역할·제약."""
    return _SYSTEM.get(lang, _SYSTEM["en"])


def build_user_prompt(
    lang: str,
    query: str,
    document: str,
    source_title: str,
) -> str:
    """사용자 프롬프트 — 5단계 구조 + 문서 전문."""
    L = _labels(lang)
    template = _FORMAT_BLOCKS.get(lang, _FORMAT_BLOCKS["en"])
    format_block = template.format(
        situation=L["situation"],
        place=L["place"],
        target=L["target"],
        documents=L["documents"],
        procedure=L["procedure"],
        caution=L["caution"],
        next_steps=L["next_steps"],
        source=L["source"],
        missing=L["not_in_doc"],
        source_title=source_title,
    )

    doc_header = {
        "ko": f"--- 문서 (제목: {source_title}) ---",
        "en": f"--- Document (title: {source_title}) ---",
        "zh": f"--- 文档（标题：{source_title}）---",
        "ja": f"--- 文書（タイトル：{source_title}）---",
    }.get(lang, f"--- Document (title: {source_title}) ---")

    doc_footer = {
        "ko": "--- 문서 끝 ---",
        "en": "--- End of document ---",
        "zh": "--- 文档结束 ---",
        "ja": "--- 文書終了 ---",
    }.get(lang, "--- End of document ---")

    question_label = {
        "ko": "질문",
        "en": "Question",
        "zh": "问题",
        "ja": "質問",
    }.get(lang, "Question")

    reminder = _LANG_REMINDER.get(lang, "")
    reminder_block = f"\n{reminder}\n" if reminder else ""

    return (
        f"{format_block}\n\n"
        f"{doc_header}\n"
        f"{document}\n"
        f"{doc_footer}\n"
        f"{reminder_block}\n"
        f"{question_label}: {query}"
    )
