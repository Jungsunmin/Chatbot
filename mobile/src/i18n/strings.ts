import type { Lang } from "../api/client";

type Strings = {
  appTitle: string;
  appSubtitle: string;
  openChat: string;
  chatTitle: string;
  placeholder: string;
  send: string;
  sources: string;
  back: string;
  langLabel: string;
  onboardingPre: string;
  onboardingStudy: string;
  onboardingLife: string;
  apiOffline: string;
  confirmYes: string;
  confirmNo: string;
};

const table: Record<Lang, Strings> = {
  ko: {
    appTitle: "건국대 유학생",
    appSubtitle: "KU 가이드북 FAQ (출처 링크 표시)",
    openChat: "챗봇 열기",
    chatTitle: "가이드북 FAQ",
    placeholder: "비자, 등록, 보험 등 질문…",
    send: "전송",
    sources: "참고 링크",
    back: "뒤로",
    langLabel: "언어",
    onboardingPre: "입학 전",
    onboardingStudy: "재학",
    onboardingLife: "생활",
    apiOffline: "API 오프라인 — 백엔드 8001 포트 확인",
    confirmYes: "예, 관련 있어요",
    confirmNo: "아니요",
  },
  en: {
    appTitle: "Konkuk Intl Student",
    appSubtitle: "Guide & FAQ assistant (prototype)",
    openChat: "Open Chatbot",
    chatTitle: "FAQ Chat",
    placeholder: "Ask about visa, registration, housing…",
    send: "Send",
    sources: "Sources",
    back: "Back",
    langLabel: "Language",
    onboardingPre: "Before arrival",
    onboardingStudy: "During studies",
    onboardingLife: "Campus life",
    apiOffline: "API offline — start backend on port 8001",
    confirmYes: "Yes, related",
    confirmNo: "No",
  },
  zh: {
    appTitle: "建国大学 留学生",
    appSubtitle: "指南与 FAQ 助手（原型）",
    openChat: "打开聊天",
    chatTitle: "FAQ 对话",
    placeholder: "咨询签证、注册、宿舍…",
    send: "发送",
    sources: "来源",
    back: "返回",
    langLabel: "语言",
    onboardingPre: "入境前",
    onboardingStudy: "在学",
    onboardingLife: "校园生活",
    apiOffline: "API 未连接 — 请启动后端 8001 端口",
    confirmYes: "是，相关",
    confirmNo: "否",
  },
  ja: {
    appTitle: "建国大学 留学生",
    appSubtitle: "ガイド・FAQ アシスタント（試作）",
    openChat: "チャットを開く",
    chatTitle: "FAQ チャット",
    placeholder: "ビザ、登録、寮について…",
    send: "送信",
    sources: "出典",
    back: "戻る",
    langLabel: "言語",
    onboardingPre: "入学前",
    onboardingStudy: "在学中",
    onboardingLife: "キャンパス生活",
    apiOffline: "API オフライン — バックエンド 8001 を起動",
    confirmYes: "はい、関連あり",
    confirmNo: "いいえ",
  },
};

export function t(lang: Lang): Strings {
  return table[lang];
}
