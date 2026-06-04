import { StatusBar } from "expo-status-bar";
import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  AppState,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";
import {
  checkHealth,
  sendChat,
  sendChatConfirm,
  type ChatResponse,
  type Lang,
} from "./src/api/client";
import { t } from "./src/i18n/strings";
import { openSourceLink } from "./src/openSourceLink";

type Screen = "home" | "chat";
type Onboarding = "pre" | "study" | "life";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
  citations?: ChatResponse["citations"];
  status?: ChatResponse["status"];
  pendingId?: string;
  confirmPrompt?: string;
  confirmResolved?: boolean;
};

const LANGS: { code: Lang; label: string }[] = [
  { code: "ko", label: "한국어" },
  { code: "en", label: "EN" },
  { code: "zh", label: "中文" },
  { code: "ja", label: "日本語" },
];

export default function App() {
  return (
    <SafeAreaProvider>
      <AppContent />
    </SafeAreaProvider>
  );
}

function AppContent() {
  const [screen, setScreen] = useState<Screen>("home");
  const [lang, setLang] = useState<Lang>("ko");
  const [onboarding, setOnboarding] = useState<Onboarding>("pre");
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const s = t(lang);

  useEffect(() => {
    checkHealth().then(setApiOk);
  }, [screen]);

  // Safari 복귀 후 API 상태만 다시 확인 (화면은 유지)
  useEffect(() => {
    const sub = AppState.addEventListener("change", (state) => {
      if (state === "active") {
        checkHealth().then(setApiOk);
      }
    });
    return () => sub.remove();
  }, []);

  const appendAssistant = (res: ChatResponse) => {
    const showCitations = res.status === "answered" && res.citations.length > 0;
    setMessages((m) => [
      ...m,
      {
        id: `${Date.now()}-a`,
        role: "assistant",
        text:
          res.status === "confirm_needed" && res.confirm_prompt
            ? `${res.confirm_prompt}\n\n${res.answer}`
            : res.answer,
        citations: showCitations ? res.citations : res.status === "confirm_needed" ? res.citations : [],
        status: res.status,
        pendingId: res.pending_id ?? undefined,
        confirmPrompt: res.confirm_prompt ?? undefined,
        confirmResolved: res.status !== "confirm_needed",
      },
    ]);
  };

  const postChat = async () => {
    const q = input.trim();
    if (!q || loading) return;
    setInput("");
    const userMsg: ChatMessage = { id: Date.now().toString(), role: "user", text: q };
    setMessages((m) => [...m, userMsg]);
    setLoading(true);
    try {
      const res = await sendChat(q, lang);
      appendAssistant(res);
    } catch (e) {
      setMessages((m) => [
        ...m,
        {
          id: `${Date.now()}-err`,
          role: "assistant",
          text: e instanceof Error ? e.message : "Request failed",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const postConfirm = async (pendingId: string, confirm: "yes" | "no", msgId: string) => {
    if (loading) return;
    setLoading(true);
    setMessages((m) =>
      m.map((item) => (item.id === msgId ? { ...item, confirmResolved: true } : item))
    );
    try {
      const res = await sendChatConfirm(pendingId, confirm, lang);
      appendAssistant(res);
    } catch (e) {
      setMessages((m) => [
        ...m,
        {
          id: `${Date.now()}-err`,
          role: "assistant",
          text: e instanceof Error ? e.message : "Request failed",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (screen === "home") {
    return (
      <SafeAreaView style={styles.safe} edges={["top", "left", "right", "bottom"]}>
        <StatusBar style="light" />
        <View style={styles.header}>
          <Text style={styles.title}>{s.appTitle}</Text>
          <Text style={styles.sub}>{s.appSubtitle}</Text>
        </View>
        <Text style={styles.section}>{s.langLabel}</Text>
        <View style={styles.row}>
          {LANGS.map((l) => (
            <Pressable
              key={l.code}
              style={[styles.chip, lang === l.code && styles.chipActive]}
              onPress={() => setLang(l.code)}
            >
              <Text style={[styles.chipText, lang === l.code && styles.chipTextActive]}>
                {l.label}
              </Text>
            </Pressable>
          ))}
        </View>
        <Text style={styles.section}>Onboarding</Text>
        <View style={styles.row}>
          {(
            [
              ["pre", s.onboardingPre],
              ["study", s.onboardingStudy],
              ["life", s.onboardingLife],
            ] as const
          ).map(([key, label]) => (
            <Pressable
              key={key}
              style={[styles.chip, onboarding === key && styles.chipActive]}
              onPress={() => setOnboarding(key)}
            >
              <Text
                style={[styles.chipText, onboarding === key && styles.chipTextActive]}
              >
                {label}
              </Text>
            </Pressable>
          ))}
        </View>
        {apiOk === false && <Text style={styles.warn}>{s.apiOffline}</Text>}
        <Pressable style={styles.primaryBtn} onPress={() => setScreen("chat")}>
          <Text style={styles.primaryBtnText}>{s.openChat}</Text>
        </Pressable>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safe} edges={["top", "left", "right"]}>
      <StatusBar style="light" />
      <View style={styles.chatHeader}>
        <Pressable onPress={() => setScreen("home")}>
          <Text style={styles.back}>{s.back}</Text>
        </Pressable>
        <Text style={styles.chatTitle}>{s.chatTitle}</Text>
      </View>
      <KeyboardAvoidingView
        style={styles.chatBody}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        keyboardVerticalOffset={Platform.OS === "ios" ? 8 : 0}
      >
        <FlatList
          style={styles.list}
          contentContainerStyle={styles.listContent}
          data={messages}
          keyExtractor={(item) => item.id}
          keyboardShouldPersistTaps="handled"
          renderItem={({ item }) => (
            <View
              style={[
                styles.bubble,
                item.role === "user" ? styles.bubbleUser : styles.bubbleBot,
              ]}
            >
              <Text style={styles.bubbleText}>{item.text}</Text>
              {item.citations && item.citations.length > 0 && (
                <Text style={styles.citeHeader}>{s.sources}</Text>
              )}
              {item.status !== "unknown" &&
                item.citations?.map((c, i) =>
                  c.source_url ? (
                    <Pressable
                      key={i}
                      style={styles.citeLinkWrap}
                      onPress={() => openSourceLink(c.source_url!)}
                    >
                      <Text style={styles.citeLink}>• {c.title}</Text>
                    </Pressable>
                  ) : (
                    <Text key={i} style={styles.cite}>
                      • {c.title} ({c.source_id})
                    </Text>
                  )
                )}
              {item.status === "confirm_needed" &&
                item.pendingId &&
                !item.confirmResolved && (
                  <View style={styles.confirmRow}>
                    <Pressable
                      style={styles.confirmBtn}
                      onPress={() => postConfirm(item.pendingId!, "yes", item.id)}
                    >
                      <Text style={styles.confirmBtnText}>{s.confirmYes}</Text>
                    </Pressable>
                    <Pressable
                      style={[styles.confirmBtn, styles.confirmBtnNo]}
                      onPress={() => postConfirm(item.pendingId!, "no", item.id)}
                    >
                      <Text style={styles.confirmBtnText}>{s.confirmNo}</Text>
                    </Pressable>
                  </View>
                )}
            </View>
          )}
          ListEmptyComponent={<Text style={styles.empty}>{s.placeholder}</Text>}
        />
        <View style={styles.inputRow}>
          <TextInput
            style={styles.input}
            placeholder={s.placeholder}
            placeholderTextColor="#94a3b8"
            value={input}
            onChangeText={setInput}
            editable={!loading}
          />
          <Pressable style={styles.sendBtn} onPress={postChat} disabled={loading}>
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.sendText}>{s.send}</Text>
            )}
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#0f172a" },
  header: { padding: 20, paddingTop: 12 },
  title: { fontSize: 24, fontWeight: "700", color: "#f8fafc" },
  sub: { fontSize: 14, color: "#94a3b8", marginTop: 6 },
  section: {
    color: "#94a3b8",
    fontSize: 12,
    marginLeft: 20,
    marginTop: 16,
    textTransform: "uppercase",
  },
  row: { flexDirection: "row", flexWrap: "wrap", padding: 12, gap: 8 },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: "#1e293b",
  },
  chipActive: { backgroundColor: "#2563eb" },
  chipText: { color: "#cbd5e1", fontSize: 14 },
  chipTextActive: { color: "#fff", fontWeight: "600" },
  warn: { color: "#fbbf24", marginHorizontal: 20, marginTop: 8 },
  primaryBtn: {
    margin: 20,
    backgroundColor: "#2563eb",
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
  },
  primaryBtnText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  chatHeader: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    gap: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#1e293b",
  },
  back: { color: "#60a5fa", fontSize: 16 },
  chatTitle: { color: "#f8fafc", fontSize: 18, fontWeight: "600" },
  chatBody: { flex: 1 },
  list: { flex: 1 },
  listContent: { padding: 12, paddingBottom: 8 },
  bubble: {
    maxWidth: "90%",
    padding: 12,
    borderRadius: 12,
    marginBottom: 10,
  },
  bubbleUser: { alignSelf: "flex-end", backgroundColor: "#2563eb" },
  bubbleBot: { alignSelf: "flex-start", backgroundColor: "#1e293b" },
  bubbleText: { color: "#f8fafc", fontSize: 15, lineHeight: 22 },
  citeHeader: { color: "#94a3b8", fontSize: 11, marginTop: 8 },
  cite: { color: "#64748b", fontSize: 11, marginTop: 2 },
  citeLinkWrap: { marginTop: 6 },
  citeLink: { color: "#93c5fd", fontSize: 11, textDecorationLine: "underline" },
  empty: { color: "#64748b", textAlign: "center", marginTop: 40 },
  inputRow: {
    flexDirection: "row",
    padding: 12,
    gap: 8,
    borderTopWidth: 1,
    borderTopColor: "#1e293b",
  },
  input: {
    flex: 1,
    backgroundColor: "#1e293b",
    color: "#f8fafc",
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 15,
  },
  sendBtn: {
    backgroundColor: "#2563eb",
    borderRadius: 10,
    paddingHorizontal: 16,
    justifyContent: "center",
    minWidth: 64,
  },
  sendText: { color: "#fff", fontWeight: "600" },
  confirmRow: { flexDirection: "row", gap: 8, marginTop: 12 },
  confirmBtn: {
    flex: 1,
    backgroundColor: "#2563eb",
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: "center",
  },
  confirmBtnNo: { backgroundColor: "#475569" },
  confirmBtnText: { color: "#fff", fontSize: 13, fontWeight: "600" },
});
