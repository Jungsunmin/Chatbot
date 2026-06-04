/**
 * 가이드북 링크 열기 — Safari 전환 대신 인앱 브라우저 사용 (Expo Go 복귀 시 흰 화면 완화)
 */
import * as WebBrowser from "expo-web-browser";
import { Alert, Linking } from "react-native";

export async function openSourceLink(url: string): Promise<void> {
  const trimmed = url?.trim();
  if (!trimmed) return;

  try {
    const canOpen = await Linking.canOpenURL(trimmed);
    if (!canOpen) {
      Alert.alert("링크 오류", "이 주소를 열 수 없습니다.");
      return;
    }
    // iOS: SFSafariViewController — 앱으로 돌아올 때 Expo Go가 덜 죽음
    await WebBrowser.openBrowserAsync(trimmed, {
      presentationStyle: WebBrowser.WebBrowserPresentationStyle.AUTOMATIC,
      dismissButtonStyle: "done",
      enableBarCollapsing: true,
    });
  } catch {
    Alert.alert("링크 오류", "브라우저를 열지 못했습니다.");
  }
}
