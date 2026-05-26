# 실제 iPhone / Android에서 Expo 실행

## QR이 안 될 때 (가장 흔한 원인)

### 1. 잘못된 앱으로 스캔

| 방법 | 결과 |
|------|------|
| **iPhone 기본 카메라** | Expo 프로젝트가 안 열리거나 Safari만 열림 |
| **Expo Go 앱 → Scan QR code** | 정상 |

Expo Go 설치 후 앱을 열고 **Home → Scan QR code** 로 터미널 QR을 스캔하세요.

### 2. PC와 폰이 다른 네트워크

- Mac과 iPhone이 **같은 Wi‑Fi** 인지 확인
- 학교/카페 Wi‑Fi는 **기기 간 차단(AP isolation)** 이 있어 LAN QR이 실패할 수 있음  
  → 아래 **Tunnel 모드** 사용

### 3. Tunnel 모드 (QR/LAN 둘 다 실패 시)

```bash
cd mobile
npx expo start --tunnel
```

처음이면 `@expo/ngrok` 설치 안내가 나올 수 있습니다. `y` 로 진행.

터널 URL로 QR이 생성되며, 네트워크가 달라도 연결되는 경우가 많습니다 (느릴 수 있음).

### 4. 수동으로 URL 입력

Expo Go → **Enter URL manually**:

```text
exp://192.168.55.184:8081
```

`192.168.55.184` 는 Mac의 LAN IP (`ipconfig getifaddr en0`)로 바꾸세요.

---

## QR은 되는데 챗봇만 「API offline」일 때

`mobile/.env` 의 `127.0.0.1` 은 **폰 자신**을 가리킵니다. Mac IP로 바꿔야 합니다.

```env
EXPO_PUBLIC_API_URL=http://192.168.55.184:8001
```

백엔드는 반드시:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

`.env` 수정 후 Metro **재시작** (`r` 또는 `npx expo start` 다시).

Mac 방화벽에서 **8001**, **8081** 허용이 필요할 수 있습니다.

---

## iOS 시뮬레이터 (QR 불필요)

Xcode 시뮬레이터 + 라이선스 동의 후:

```bash
cd mobile
npx expo start
# 터미널에서 i
```

시뮬레이터 API 주소: `http://127.0.0.1:8001`

---

## 링크 누른 뒤 앱이 흰 화면만 보일 때

**원인**: 출처 URL을 `Linking`으로 **Safari 전체 화면**에 열면 Expo Go가 백그라운드에서 JS 연결이 끊겨, 돌아올 때 흰 화면이 될 수 있습니다.

**조치** (코드 반영됨):

- 링크는 **인앱 브라우저**(`expo-web-browser`)로 엽니다. 상단 **완료**로 앱 복귀.
- 이미 흰 화면이면: Expo Go에서 기기 흔들기 → **Reload**, 또는 터미널에서 `r`

---

## 체크리스트

- [ ] Expo Go 최신 버전 (SDK 52 호환)
- [ ] `npm install` 완료
- [ ] 백엔드 `/health` 응답 (`curl http://127.0.0.1:8001/health`)
- [ ] `mobile/.env` 에 Mac LAN IP
- [ ] Expo Go 앱 내 QR 스캔 (카메라 앱 X)
