/**
 * 백엔드 RAG 챗 API 클라이언트
 */
const API_BASE =
  process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8001";

export type Lang = "ko" | "en" | "zh" | "ja";
export type AnswerStatus = "answered" | "confirm_needed" | "unknown";

export interface Citation {
  source_id: string;
  title: string;
  lang: string;
  excerpt: string;
  source_url?: string;
  label?: string;
  doc_type?: string;
}

export interface ChatResponse {
  status: AnswerStatus;
  answer: string;
  citations: Citation[];
  model_used: boolean;
  pending_id?: string | null;
  confirm_prompt?: string | null;
}

export interface ChatPayload {
  message?: string;
  lang: Lang;
  confirm?: "yes" | "no";
  pending_id?: string;
}

async function postChatBody(body: ChatPayload): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

/** 1차 질문 */
export async function sendChat(message: string, lang: Lang): Promise<ChatResponse> {
  return postChatBody({ message, lang });
}

/** 2차 확인 (예/아니오) */
export async function sendChatConfirm(
  pendingId: string,
  confirm: "yes" | "no",
  lang: Lang
): Promise<ChatResponse> {
  return postChatBody({
    message: "",
    lang,
    confirm,
    pending_id: pendingId,
  });
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
