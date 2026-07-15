/**
 * 백엔드 RAG 챗 API 클라이언트
 */
import { resolveApiBase } from "./resolveApiBase";

export type Lang = "ko" | "en" | "zh" | "ja";
export type AnswerStatus = "answered" | "unknown";

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
}

export interface ChatPayload {
  message: string;
  lang: Lang;
}

async function postChatBody(body: ChatPayload): Promise<ChatResponse> {
  const res = await fetch(`${resolveApiBase()}/chat`, {
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

/** health 체크에 쓰는 URL (오프라인 안내용) */
export function getApiBaseUrl(): string {
  return resolveApiBase();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${getApiBaseUrl()}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

/** 서버가 허용하는 최대 메시지 길이. 조회 실패 시 null(호출부에서 폴백값 사용). */
export async function fetchMaxQueryLength(): Promise<number | null> {
  try {
    const res = await fetch(`${getApiBaseUrl()}/health`);
    if (!res.ok) return null;
    const data = await res.json();
    return typeof data.max_query_length === "number" ? data.max_query_length : null;
  } catch {
    return null;
  }
}
