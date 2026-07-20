# giftclean-cms-auth (PR-A)

CMS 로그인 PIN을 서버(Cloudflare Worker)에서 검증하고, 성공 시 짧은 수명(2시간)의 세션 토큰을 발급하는 전용 Worker입니다.

이 Worker에는 다음이 **포함되어 있지 않습니다**:
- data/*.json 저장 기능
- GitHub commit/push 로직
- GitHub 토큰 사용

배포 방법과 Secret 설정 방법은 저장소 루트의 `cms/README.md`를 참고하세요.

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
