# Source allowlist

## 로컬 폴더

`config/sources.yaml`:

```yaml
local:
  allowed_roots:
    - data/sources/official
```

- 위 루트 **밖** 파일은 `ingest_local.py`가 `[deny]` 로그 후 스킵
- `allowed_extensions` 밖 확장자도 스킵
- `follow_symlinks: false` — 루트 밖 symlink 차단

## 웹 (선택)

```yaml
web:
  enabled: true
  allowed_domains:
    - your-university.ac.kr
  seed_urls:
    - https://your-university.ac.kr/international
```

- 도메인·path prefix 불일치 URL은 수집 안 함

## 메타데이터

`data/sources/manifest.csv` 예:

```csv
filename,category,lang,verified
housing_guide_en.pdf,housing,en,true
```

없으면 파일명 휴리스틱(`_ko`, `housing` 등) 사용.
