"""
Centralized DOM selectors for Naver web pages.
When Naver updates their HTML structure, update ONLY this file.

NOTE: These selectors must be verified against the live Naver pages
using browser DevTools (F12). Naver updates their DOM periodically.
"""


class LoginSelectors:
    """https://nid.naver.com/nidlogin.login"""
    ID_PW_TAB = "#qrlog\\.logtab"       # "ID/전화번호" 탭 (QR코드가 기본 탭일 수 있음)
    ID_INPUT = "input#id"
    PW_INPUT = "input#pw"
    LOGIN_BUTTON = "#log\\.login"
    CAPTCHA_CONTAINER = "#captcha"
    LOGIN_ERROR_MSG = ".error_message"


class EditorSelectors:
    """https://blog.naver.com/{id}/postwrite - Smart Editor ONE"""
    # iframe
    MAIN_FRAME = "#mainFrame"

    # Popup
    POPUP_CLOSE = "button.btn_close"

    # "작성 중인 글이 있습니다" 팝업 — 취소 버튼 (새 글 작성)
    DRAFT_POPUP_CANCEL = "button.cancel"
    DRAFT_POPUP_CANCEL_ALT = "//button[contains(text(), '취소')]"

    # Title
    TITLE_AREA = ".se-documentTitle .se-text-paragraph"
    TITLE_TEXTAREA = "textarea.se-fs-"

    # Body
    BODY_AREA = ".se-component.se-text .se-text-paragraph"
    BODY_SECTION = ".se-section-text"

    # Image upload — 사진 버튼 & hidden file input
    PHOTO_BUTTON = "button[data-name='image']"
    PHOTO_FILE_INPUT = "input[type='file'][accept*='image']"
    PHOTO_FILE_INPUT_ALT = "input[type='file']"

    # Save — 해시 클래스는 빌드마다 바뀌므로 여러 패턴 사용
    SAVE_BUTTON_CANDIDATES = [
        "button.save_btn__m9KHH",               # 기존 해시
        "button[class*='save_btn']",             # save_btn 포함하는 클래스
        "button.publish_btn__",                  # 발행 버튼 변형
        "button[class*='publish_btn']",
    ]
    SAVE_BUTTON_XPATH_CANDIDATES = [
        "//button[contains(text(), '발행')]",
        "//button[contains(text(), '저장')]",
        "//button[contains(@class, 'save')]",
    ]

    # Editor container
    EDITOR_CONTAINER = ".se-editor"
    EDITOR_CONTENT = ".se-content"

    # 임시저장 버튼 (발행보다 우선 탐색)
    TEMP_SAVE_BUTTON_CANDIDATES = [
        "button[class*='tempsave']",
        "button[class*='temp_save']",
        "button[class*='draft']",
    ]
    TEMP_SAVE_XPATH_CANDIDATES = [
        "//button[contains(text(), '임시저장')]",
        "//button[contains(text(), '저장')]",
    ]

    # 카테고리 선택 (글쓰기 페이지 좌측 또는 상단 패널)
    # Naver Smart Editor ONE — 실제 빌드마다 클래스가 바뀔 수 있어 여러 패턴 사용
    CATEGORY_SELECT_CANDIDATES = [
        "select[name='category']",
        "select.category_select",
        ".category_select select",
        "#category",
    ]
    CATEGORY_OPTION_XPATH = "//select[contains(@name,'category')]//option[contains(text(),'{name}')]"
    CATEGORY_BUTTON_XPATH = "//button[contains(@class,'category') and contains(text(),'{name}')]"

    # 태그 입력 — 반드시 '발행' 버튼 클릭 후 설정 패널이 열린 다음에 탐색
    # JS로 모든 iframe 포함 탐색 필요 (editor.py set_tags 참고)
    TAG_INPUT_CANDIDATES = [
        "input[placeholder*='태그']",
        "input.tag_input",
        ".tag_wrap input",
        "#tag_input",
        "input[name='tag']",
    ]

    # 태그 패널 열기 버튼 ('발행' 클릭 → 사이드패널에서 태그 입력창 노출)
    PUBLISH_BTN_XPATH = "//button[normalize-space()='발행']"
