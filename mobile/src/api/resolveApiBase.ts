/**
 * 개발 중 API 베이스 URL — Expo Metro가 쓰는 Mac IP를 재사용해 Wi‑Fi 변경 시 .env 수정 불필요.
 */
import Constants from "expo-constants";
import { Platform } from "react-native";

const BACKEND_PORT = 8001;

/** hostUri / debuggerHost 에서 IP·호스트만 추출 (예: 192.168.54.250:8081 → 192.168.54.250) */
function hostFromDevUri(uri: string): string | null {
  const host = uri.split(":")[0]?.trim();
  return host || null;
}

/** exp://192.168.x.x:8081 형태 URL에서 호스트 추출 */
function hostFromExperienceUrl(url: string): string | null {
  const normalized = url.replace(/^exp:\/\//, "http://");
  try {
    return new URL(normalized).hostname || null;
  } catch {
    return hostFromDevUri(url);
  }
}

/** @expo/cli 가 주입하는 개발 머신 주소 (Wi‑Fi 바뀌면 Expo 재시작 시 갱신됨) */
function getDevMachineHost(): string | null {
  const hostUri = Constants.expoConfig?.hostUri;
  if (hostUri) {
    return hostFromDevUri(hostUri);
  }

  const expoGo = Constants.expoGoConfig as { debuggerHost?: string } | null;
  if (expoGo?.debuggerHost) {
    return hostFromDevUri(expoGo.debuggerHost);
  }

  const legacy = Constants.manifest as { debuggerHost?: string } | null;
  if (legacy?.debuggerHost) {
    return hostFromDevUri(legacy.debuggerHost);
  }

  if (Constants.experienceUrl) {
    const h = hostFromExperienceUrl(Constants.experienceUrl);
    if (h) return h;
  }

  if (Constants.linkingUri) {
    const h = hostFromExperienceUrl(Constants.linkingUri);
    if (h) return h;
  }

  return null;
}

function fallbackDevBase(): string {
  if (Platform.OS === "android") {
    return `http://10.0.2.2:${BACKEND_PORT}`;
  }
  return `http://127.0.0.1:${BACKEND_PORT}`;
}

/**
 * API 베이스 URL.
 * - EXPO_PUBLIC_API_URL 이 `auto` 또는 비어 있으면: 개발 시 Expo host 자동 감지
 * - 그 외 명시 URL: 배포·스테이징용 고정 주소
 */
export function resolveApiBase(): string {
  const raw = process.env.EXPO_PUBLIC_API_URL?.trim();
  const useAuto = !raw || raw === "auto";

  if (!useAuto) {
    return raw.replace(/\/$/, "");
  }

  if (__DEV__) {
    const host = getDevMachineHost();
    if (host) {
      if (
        Platform.OS === "android" &&
        (host === "localhost" || host === "127.0.0.1")
      ) {
        return `http://10.0.2.2:${BACKEND_PORT}`;
      }
      return `http://${host}:${BACKEND_PORT}`;
    }
  }

  return fallbackDevBase();
}
