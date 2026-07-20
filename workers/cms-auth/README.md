# giftclean-cms-auth (PR-A, PR-B1)

CMS 로그인 PIN을 서버(Cloudflare Worker)에서 검증하고, 성공 시 짧은 수명(2시간)의 세션 토큰을 발급하는 전용 Worker입니다. PR-B1부터는 세션 토큰으로 보호되는 `data/*.json` 조회(`/content`)와 저장 사전검증(`/save`, dryRun 전용)도 포함합니다.

이 Worker에는 다음이 **아직 포함되어 있지 않습니다** (PR-B2 이후 예정):
- 실제 GitHub commit/push 로직 (`/save`는 dryRun 모드로만 동작하며, `dryRun:false`를 보내도 commit하지 않고 `dry_run_only` 응답만 돌려줍니다)
- `GITHUB_SAVE_TOKEN` 사용 — `data/*.json`은 공개 저장소 읽기이므로 이 단계에서는 토큰 없이 조회됩니다

배포 방법과 Secret 설정 방법은 저장소 루트의 `cms/README.md`를 참고하세요.

## 환경 변수 (`wrangler.toml [vars]`, 비밀값 아님)

- `ALLOWED_ORIGINS` — 콤마로 구분된 다중 허용 origin 목록. CORS `Access-Control-Allow-Origin`을 요청의 `Origin` 헤더가 이 목록에 있을 때만 그 값으로 반영합니다(목록에 없으면 `null`).
- `GITHUB_REPO_OWNER`, `GITHUB_REPO_NAME`, `GITHUB_BRANCH` — `/content`, `/save`가 조회하는 저장소/브랜치

## 엔드포인트

### `POST /login`

요청 본문:
```json
{ "pin": "관리자가 입력한 PIN" }
```

성공 응답 (200):
```json
{ "token": "서명된 세션 토큰", "expiresAt": 1234567890 }
```

실패 응답:
- `401` — PIN 불일치
- `400` — 잘못된 요청 본문
- `500` — Worker에 `ADMIN_PIN` 또는 `SESSION_SECRET`이 아직 설정되지 않음

### `GET /content?type=banners`

요청 헤더: `Authorization: Bearer <세션 토큰>`

세션 토큰을 검증하고, `type`이 저장 whitelist(현재 `banners`만)에 있으면 GitHub Contents API로 `data/banners.json`을 조회해 반환합니다. 화면에 보여줄 콘텐츠와 저장 시 충돌 비교에 쓸 `sha`를 항상 같은 시점에 함께 제공하기 위한 엔드포인트입니다.

성공 응답 (200):
```json
{ "type": "banners", "path": "data/banners.json", "sha": "abc123...", "content": [ { "id": "banner-001", "...": "..." } ] }
```

실패 응답:
- `401` — 세션 토큰 없음/서명 불일치/만료
- `403` — whitelist에 없는 `type`
- `502` — GitHub Contents API 조회 실패

### `POST /save` (PR-B1: dryRun 전용, 실제 commit 없음)

요청 헤더: `Authorization: Bearer <세션 토큰>`

요청 본문:
```json
{
  "type": "banners",
  "payload": [ { "id": "banner-001", "title": "...", "description": "...", "button": "...", "link": "#contact", "visible": true, "sort": 1 } ],
  "expectedSha": "abc123...",
  "dryRun": true
}
```

처리 순서: 세션 검증 → whitelist 확인 → payload 구조/필수 필드 검증 → GitHub에서 현재 `sha` 재조회 → `expectedSha`와 비교 → **여기까지 전부 통과해야만** dryRun 분기로 진행합니다.

- `dryRun`이 `true`이거나 생략된 경우: 실제 commit 없이 `{"ok":true,"dryRun":true,...}` 200 응답 (안전한 기본값)
- `dryRun`이 명시적으로 `false`인 경우: **실제 commit을 수행하지 않고** `501` + `{"error":"dry_run_only"}` 응답

실패 응답:
- `401` — 세션 토큰 없음/서명 불일치/만료
- `403` — whitelist에 없는 `type`
- `400` — `payload`가 배열이 아니거나 필수 필드 누락 (`details`에 상세 목록 포함)
- `409` — `expectedSha`가 GitHub의 현재 `sha`와 다름 (충돌)
- `502` — GitHub Contents API 조회 실패
- `501` — `dryRun:false` 요청 (PR-B1에서는 아직 지원하지 않음)
