import logging
import subprocess
import tempfile
import time
import platform
from pathlib import Path

import pyperclip
import pyautogui

from config.settings import CLIPBOARD_PASTE_DELAY

logger = logging.getLogger(__name__)


def clipboard_paste(text: str, element=None) -> None:
    """
    클립보드 붙여넣기로 텍스트 입력 (봇 감지 우회).
    send_keys() 대신 pyperclip + pyautogui 사용.
    """
    if element is not None:
        element.click()
        time.sleep(0.3)

    pyperclip.copy(text)
    time.sleep(0.1)

    if platform.system() == "Darwin":
        pyautogui.hotkey("command", "v")
    else:
        pyautogui.hotkey("ctrl", "v")

    time.sleep(CLIPBOARD_PASTE_DELAY)


def copy_image_to_clipboard(image_path: str) -> bool:
    """이미지 파일을 OS 클립보드에 '이미지'로 올린다 (붙여넣기용).

    네이버 스마트에디터ONE은 사진 버튼을 누르기 전엔 <input type=file>이 DOM에
    존재하지 않아 send_keys 업로드가 불가능하다. 대신 이미지를 클립보드에 올리고
    본문에 Cmd/Ctrl+V로 붙여넣으면 파일창 없이 인라인 삽입된다.

    macOS: sips로 PNG 변환 후 osascript로 클립보드에 PNG 데이터를 올린다.
    그 외 OS: 미지원(False 반환 → 호출부가 파일 input 폴백 사용).
    """
    src = Path(image_path)
    if not src.exists():
        logger.warning(f"클립보드 복사 실패 — 파일 없음: {src}")
        return False

    if platform.system() != "Darwin":
        logger.info("이미지 클립보드 복사는 현재 macOS만 지원 — 파일 input 폴백 사용")
        return False

    # 1) 어떤 포맷이든 PNG로 정규화 (sips는 macOS 기본 내장)
    tmp_png = Path(tempfile.gettempdir()) / "naver_clip_image.png"
    png_path = src
    if src.suffix.lower() != ".png":
        try:
            subprocess.run(
                ["sips", "-s", "format", "png", str(src), "--out", str(tmp_png)],
                check=True, capture_output=True,
            )
            png_path = tmp_png
        except Exception as e:
            logger.warning(f"sips PNG 변환 실패({src.name}): {e}")
            return False

    # 2) osascript로 PNG 데이터를 클립보드에 올림
    script = f'set the clipboard to (read (POSIX file "{png_path}") as «class PNGf»)'
    try:
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        return True
    except Exception as e:
        logger.warning(f"osascript 클립보드 이미지 적재 실패({src.name}): {e}")
        return False


def clipboard_clear() -> None:
    """클립보드 내용 삭제 (보안)."""
    pyperclip.copy("")
