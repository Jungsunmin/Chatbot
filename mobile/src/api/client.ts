/**
 * 백엔드 RAG 챗 API 클라이언트
 * 실기기: .env EXPO_PUBLIC_API_URL=http://<PC_LAN_IP>:8000
 */
const API_BASE =
  process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

export type Lang = "en" | "zh" | "ja";

export interface Citation {
  source_id: string;
  title: string;
  lang: string;
  excerpt: string;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  model_used: boolean;
}

export async function sendChat(
  message: string,
  lang: Lang
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, lang }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
