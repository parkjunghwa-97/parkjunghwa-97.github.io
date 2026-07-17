# 기프트클린 네이버 블로그 작성 도우미

짧은 메모/현장정보 + 사진을 입력하면 AI가 기프트클린 톤에 맞는 네이버 블로그 글로
정리하고, **로컬 Chrome**으로 네이버 스마트에디터ONE에 제목·본문·사진·태그를 입력한 뒤
**"임시저장"까지만** 수행하는 로컬 웹 도구입니다.

> ⚠️ 이 도구는 **절대 발행(공개 게시) 버튼을 누르지 않습니다.** 발행은 사람이 네이버에서
> 직접 최종 검토 후 눌러야 합니다. 이 원칙은 `config/safety.py`에 코드로 강제되어 있습니다.

원본: [choigpt-ai/naver-blog-automation](https://github.com/choigpt-ai/naver-blog-automation) (MIT License).
이 폴더는 그 저장소의 구조를 재사용해 기프트클린 전용으로 수정한 파생 버전입니다.
자세한 라이선스/저작권 표시는 `LICENSE`, `NOTICE.md`를 참고하세요.

---

## 1. 원본 저장소 분석 요약

원본은 Threads류 짧은 글 → AI 확장 → 네이버 블로그 임시저장을 하는 범용 도구였습니다.
전체 코드를 읽고 조사한 결과, 계정정보·API 키가 정당한 목적(네이버 로그인, 각 API
공급자) 외의 곳으로 전송되는 코드는 없었고, `subprocess`/`eval`/`exec`/`shell=True` 사용도
모두 로컬 시스템 유틸(macOS 서명, 클립보드, git 해시 조회)에 한정되어 있었으며, 발행
(공개 게시) 버튼을 클릭하는 코드도 없었습니다(저장 로직이 "발행" 텍스트가 포함된 버튼을
3중으로 명시적으로 제외). 세부 내용은 이 세션의 분석 보고서(대화 기록)를 참고하세요.

## 2. 보안 위험 목록 (원본 대비 이 버전에서 보강한 부분)

| 위험 | 원본 상태 | 이 버전에서 조치 |
|---|---|---|
| 계정 평문 저장 | `.env`에 평문, 위험 고지 없음 | `.env.example`에 위험 경고 문구 추가 + Chrome 프로필 재사용 옵션(`USE_CHROME_PROFILE`) 우선 제공 |
| 발행 버튼 오작동 가능성 | 코드상 안전(라이브 미검증) | `config/safety.py`의 `FORBIDDEN_BUTTON_TEXTS`로 모든 클릭 후보에서 "발행"류 텍스트를 원천 배제 + `ALLOW_PUBLISH`를 코드에서 상수 `False`로 고정 |
| 업로드 검증 부재 | 확장자/크기 제한 없음 | `config/safety.py`에 확장자 화이트리스트·용량 제한(기본 20MB)·장수 제한 추가, `/api/publish`에서 검증 |
| 로그 노출 방어층 부재 | 마스킹 유틸 없음 | `utils/mask.py` + `utils/logger.py`에 모든 로그 레코드 마스킹 필터 적용 |
| 세션 재사용 미구현 | 매번 비밀번호 로그인 | `automation/browser.py`에 전용 Chrome 프로필 재사용 옵션 추가 |
| 개인정보 노출 경고 없음 | 없음 | `core/pii_guard.py`(전화번호/주소/도어락 패턴 텍스트 스캔 + 수동 확인 체크리스트, 자동 얼굴/차량번호 인식은 없다고 명시) |
| EXIF 위치정보 | 옵션 없음 | `core/image_exif.py`로 GPS EXIF만 제거한 새 바이트 반환(원본 파일 불변) |
| 대량/예약 실행, 자동 댓글·공감 | 없음(원본에도 없었음) | `config/safety.py`에 명시적으로 비활성 상수로 선언 + 1회 1글 강제(`enforce_single_post_run`) |

## 3. 수정한 파일 목록 (원본 대비)

**거의 그대로 재사용**: `automation/browser.py`(프로필 재사용 옵션 추가), `automation/login.py`,
`config/selectors.py`, `utils/retry.py`, `utils/clipboard.py`, `models/blog_post.py`,
`core/keyword_researcher.py`.

**전면 재작성**: `automation/editor.py`(발행 텍스트 배제 가드, 캡션 입력 기능 추가),
`automation/orchestrator.py`(기프트클린 사진 3그룹 흐름, 안전장치 배선), `web/server.py`,
`web/static/index.html`, `config/settings.py`, `utils/env_loader.py`, `utils/logger.py`.

**신규 작성**: `config/safety.py`, `utils/mask.py`, `core/giftclean_writer.py`,
`core/pii_guard.py`, `core/image_exif.py`, `core/keyword_research.py`, `core/datalab_client.py`,
`models/giftclean_post.py`, `tests/*`.

**이식하지 않음(범위 밖)**: `gui/*`(데스크톱 GUI), `post_single.py`, `continue_draft.py`,
`add_tags_only.py`, `core/llm_generator.py`, `core/thumbnail_html.py`, 카카오 CTA 자동 삽입 기능.

## 4. 변경 전후 구조

```
원본: 스레드 글 → AI 확장(범용 톤) → 임시저장(카카오 CTA 자동 삽입 포함)
이 버전: 기프트클린 입력 폼(서비스/지역/사진 3그룹 등)
  → 키워드 조사(실데이터 우선, 없으면 확인불가+수동입력)
  → 사용자 승인
  → 기프트클린 톤 글 생성(금지표현 검사 + 1회 재작성)
  → 개인정보 경고 + 최종 확인 화면(제목/글자수/사진수/태그)
  → 사용자가 확인 버튼을 눌러야 임시저장 진행
  → DRY_RUN=true면 실제 네이버 접촉 없이 미리보기만
```

## 5. 설치 방법

```bash
cd tools/naver-blog-automation
python3.12 -m venv .venv
source .venv/bin/activate          # Windows는 아래 6번 참고
pip install -r requirements.txt
cp .env.example .env
# .env를 열어 최소한 CLAUDE_API_KEY(또는 OPENAI_API_KEY) 하나는 채우세요.
# 네이버 계정 정보는 DRY_RUN 테스트에는 필요 없습니다.
```

크롬(Chrome)이 설치되어 있어야 실제 저장(DRY_RUN=false) 시 동작합니다. 드라이버는
Selenium Manager가 자동으로 설치합니다.

## 6. Windows 기준 실행 방법

```powershell
cd tools\naver-blog-automation
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
notepad .env   REM API 키 등을 채운 뒤 저장
python web_app.py
```

브라우저가 자동으로 `http://127.0.0.1:8787` 을 엽니다. 종료는 터미널에서 `Ctrl+C`.

## 7. .env.example

이 폴더의 `.env.example` 참고. 핵심 요약:
- `DRY_RUN=true` (기본값) — 실제 네이버에 아무 것도 입력/저장하지 않음
- `CLAUDE_API_KEY` 또는 `OPENAI_API_KEY` 중 하나 필수(글 생성)
- `NAVER_ID`/`NAVER_PW`/`BLOG_ID` 또는 `USE_CHROME_PROFILE=true`(권장) 중 하나로 로그인 구성
- `NAVER_SEARCHAD_*`/`NAVER_CLIENT_*`/`NAVER_DATALAB_*`는 선택 — 없으면 키워드 조사가
  "확인 불가" + 수동 입력 모드로 동작

## 8. 테스트 결과

`tests/` 아래 46개 pytest 테스트가 모두 통과합니다(선택된 요청사항 7단계 11개 항목 전부
커버). 실제 Chrome/Selenium 없이 동작하도록 `tests/conftest.py`가 selenium/
undetected-chromedriver를 가벼운 가짜 모듈로 대체합니다.

```bash
pip install -r requirements.txt
pytest tests/ -q
# 46 passed
```

DRY_RUN 모드 수동 검증도 완료: `/api/status`, `/api/keywords/research`(수동 폴백 포함),
`/api/publish`(확인 누락/확장자 위반/용량 위반 거부, 정상 요청은 실제 Naver·Selenium
접촉 없이 SSE로 "예정 동작"만 반환) 를 로컬에서 직접 호출해 확인했습니다.

## 9. 알려진 한계

- **가장 중요한 한계**: 이 코드는 클라우드/원격 세션에서 작성·테스트되었습니다.
  네이버 로그인은 요구사항대로 **사용자 PC의 로컬 Chrome에서만** 실행해야 하므로, 실제
  네이버 로그인·임시저장(H단계)은 이 환경에서 수행/검증하지 못했습니다. 반드시 사용자의
  PC에서 `DRY_RUN=false`로 직접 1회 실행해 검증해야 합니다.
- 네이버 UI(스마트에디터ONE) 셀렉터는 네이버가 언제든 바꿀 수 있습니다 — 아래 10번 참고.
- 사진 속 얼굴/차량번호 등은 자동으로 인식하지 않습니다(수동 확인 체크리스트만 제공).
- Chrome 프로필 재사용(`USE_CHROME_PROFILE`)은 최초 1회 수동 로그인이 필요하며, 사용자의
  평소 Chrome 프로필을 직접 가리키게 하면 그 프로필을 쓰는 Chrome 창을 모두 닫아야 합니다.
- 클립보드 이미지 붙여넣기(`utils/clipboard.py`)는 macOS 전용 경로가 가장 안정적이며,
  Windows/Linux에서는 파일 input 폴백 경로를 씁니다(원본 저장소와 동일한 제약).
- 데이터랩/검색광고 API 명세는 네이버 정책 변경에 따라 달라질 수 있습니다.

## 10. 네이버 UI 변경 시 수정 지점

1. `config/selectors.py` — 로그인 폼, 에디터 iframe, 제목/본문 영역, 팝업 셀렉터
2. `automation/editor.py`
   - `_find_temp_save_button` / `_js_click_temp_save` / `_find_temp_save_btn_js` — 임시저장 버튼 탐색
   - `open_settings_panel` — 태그 패널을 여는 "발행" 버튼(주의: 이름은 "발행"이지만 패널만 엶)
   - `set_last_image_caption` — 사진 설명(캡션) 입력란
   - `set_tags` — 태그 입력창
3. `config/safety.py`의 `FORBIDDEN_BUTTON_TEXTS` — 네이버가 발행 관련 버튼 문구를 바꾸면
   이 목록도 함께 업데이트해야 안전장치가 계속 작동합니다.

셀렉터가 전부 실패하면 예외가 발생해 `web/server.py`가 이를 잡아 "안전하게 중단"하고
사용자에게 마스킹된 오류 메시지를 보여줍니다(무한 재시도 없음).

## 11. 초보 사용자 사용 설명서

1. 5·6번 설치 방법대로 설치하고 `.env`에 최소한 `CLAUDE_API_KEY`를 채웁니다.
2. `python web_app.py` 실행 → 브라우저가 자동으로 열립니다.
3. 상단 배너가 "DRY_RUN 모드"인지 확인합니다(처음엔 항상 이 상태여야 합니다).
4. 1단계 화면에서 글 유형·서비스 종류·지역·주제·메모·키워드·문의 문구를 입력하고,
   작업사례형이면 작업 전/중/후 사진을 각각 올립니다.
5. "다음: 키워드 조사"를 누르면 실제 검색 데이터(또는 확인불가 표시)가 표에 나옵니다.
   필요하면 메인/보조/질문형/지역 키워드를 직접 수정한 뒤 "키워드 승인하고 글 생성"을 누릅니다.
6. 생성된 제목/본문/태그를 검토하고 필요하면 직접 수정합니다. 경고 문구(금지 표현,
   개인정보 등)가 있으면 반드시 확인 후 수정합니다.
7. "다음: 임시저장 최종 확인"에서 제목/글자수/사진수/태그/개인정보 경고를 다시 확인하고,
   체크박스를 체크해야 "임시저장 실행" 버튼이 활성화됩니다.
8. DRY_RUN이 꺼져 있다면(`.env`의 `DRY_RUN=false`) 실제로 로컬 Chrome이 열리고 네이버에
   로그인해 임시저장까지 진행합니다. 진행 로그를 보면서 완료 메시지를 확인하세요.
9. 네이버 블로그 관리 화면의 "저장 글"에서 내용을 최종 검토하고, **사람이 직접** 발행
   버튼을 누릅니다.

## 12. 원본 저장소 대비 변경 내역 요약

- 범용 "Threads → 블로그" 글쓰기를 기프트클린 청소업체 전용 구조/톤/금지표현 규칙으로 교체
- 발행 금지·업로드 검증·로그 마스킹·개인정보 경고·EXIF 제거·1회 1글 제한 등 안전장치 신설
- 키워드 조사에 공개 점수식(검색수 40 + 경쟁도 20 + 서비스적합 20 + 지역적합 10 + 추세 10)과
  수동 폴백 모드 도입
- 데스크톱 GUI, 카카오 CTA 자동삽입, 썸네일 자동생성, 다중계정 배치실행 등 요구사항 밖 기능은 제거

## 13. 임시저장 전 최종 체크리스트 (사람이 직접 확인)

- [ ] 제목에 지역명·핵심 서비스가 자연스럽게 들어있고 사실과 다른 숫자가 없는가
- [ ] 본문에 입력하지 않은 비용·시간·인력수·고객 후기가 지어내어져 있지 않은가
- [ ] 금지 표현("무조건 제거", "100% 복구", "최저가" 등)이 없는가
- [ ] 사진에 얼굴/차량번호/주소/도어락 비밀번호/전화번호가 보이지 않는가(수동 확인)
- [ ] 사진이 작업 전 → 중 → 후 순서로 올바르게 배치되어 있는가
- [ ] 태그가 실제 서비스/지역과 맞는가
- [ ] 개인정보 경고가 떴다면 원인을 확인하고 수정했는가
- [ ] "임시저장"이지 "발행"이 아님을 다시 한 번 확인했는가
- [ ] 저장 후 네이버 블로그에서 사람이 직접 최종 검토·발행할 계획인가
