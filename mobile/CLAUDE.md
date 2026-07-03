# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This is the `mobile/` Expo app for the parent 건국대 외국인 유학생 RAG FAQ 챗봇 project. See `../CLAUDE.md` for backend/RAG architecture and repo-wide commands.

## Commands

```bash
npm install
cp .env.example .env      # EXPO_PUBLIC_API_URL=auto (LAN auto-detect) or a fixed http://<ip>:8001

npm start                 # Expo dev server, LAN auto-detect
npm run start:lan         # force --lan mode
npm run start:tunnel      # ngrok tunnel (cross-network / real device off Wi-Fi)
npm run android            # open on Android emulator/device
npm run ios                # open on iOS simulator

npx tsc --noEmit           # type-check (strict mode; no test runner or lint config in this package)
```

There is no test suite or ESLint config in `mobile/` — type-checking via `tsc` is the only static check available.

## Architecture

Single-screen Expo app, no navigation library. Everything is driven by `App.tsx`.

- **`App.tsx`** — entire UI. A `Screen` state (`"home" | "chat"`) toggles between the landing view (language picker, onboarding-stage picker, "open chat" button) and the chat view (`FlatList` of messages + input row). All styling is local `StyleSheet` at the bottom of the file — there is no shared design-system/component library.
- **`src/api/client.ts`** — fetch wrapper for the backend. `sendChat(message, lang)` POSTs to `/chat` and returns a `ChatResponse` with `status: "answered" | "confirm_needed" | "unknown"` plus `citations`. `checkHealth()` polls `/health` and drives the offline banner on the home screen (checked on screen change and on app-foreground via `AppState`).
- **`src/api/resolveApiBase.ts`** — resolves the backend base URL. If `EXPO_PUBLIC_API_URL` is unset or `"auto"`, it pulls the Metro dev-machine host out of `Constants.expoConfig.hostUri` (falling back through `expoGoConfig.debuggerHost`, legacy `manifest.debuggerHost`, `experienceUrl`, `linkingUri`) so real devices reach the Mac's current LAN IP without editing `.env` when Wi-Fi changes. Falls back to `127.0.0.1:8001` (iOS) / `10.0.2.2:8001` (Android emulator) if no host can be detected. Any explicit non-`auto` value is used as-is (trailing slash stripped) — this is the path for staging/prod deployments.
- **`src/i18n/strings.ts`** — flat `Record<Lang, Strings>` table for ko/en/zh/ja UI strings (`Lang` type is imported from `client.ts`, shared with the API layer). Add new UI copy here, not inline in `App.tsx`.
- **`src/openSourceLink.ts`** — opens citation `source_url`s via `expo-web-browser`'s in-app `SFSafariViewController` rather than `Linking`/Safari, specifically because backgrounding for external Safari was killing/white-screening Expo Go on return.

### Chat response handling

Citations are only rendered when `status === "answered"` and `citations.length > 0`; `status === "unknown"` suppresses citation links even if present. `confirm_needed` responses carry `pending_id`/`confirm_prompt` in the `ChatPayload`/`ChatResponse` shape but the confirm/deny flow (`confirm: "yes" | "no"`) is not yet wired up in `App.tsx` — only the initial `sendChat` path is used.

### App identity

Bundle/package id `edu.konkuk.intl.student`, app name "KU Intl Student" (`app.json`). No `eas.json` yet — `eas build:configure` (see `../CLAUDE.md`) generates it on first run.
