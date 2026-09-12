from __future__ import annotations

import glob
import logging
import os
import platform
import subprocess
import sys
from pathlib import Path

import undetected_chromedriver as uc

from config.settings import PAGE_LOAD_TIMEOUT

logger = logging.getLogger(__name__)

# ── Apple Silicon(arm64) chromedriver 호환 ──────────────────────
# undetected-chromedriver 3.5.5는 macOS에서 항상 x86(mac-x64) 드라이버를 받는
# 버그가 있어 arm64 Mac에서 'Bad CPU type in executable' 오류로 5%에서 멈춘다.
# 아래 두 함수로 (1) 다운로드 플랫폼을 mac-arm64로 교정하고
# (2) 이미 받아둔 x86 캐시 드라이버를 삭제해 네이티브 드라이버를 다시 받게 한다.

_IS_APPLE_SILICON = sys.platform.startswith("darwin") and platform.machine() == "arm64"

# arm64 Mach-O cputype 상수 (CPU_TYPE_ARM | CPU_ARCH_ABI64)
_MACHO_CPUTYPE_ARM64 = 0x0100000C


def _codesign_adhoc(path: str) -> None:
    """arm64 바이너리에 ad-hoc 서명 + quarantine 제거.

    uc가 chromedriver를 패치하면 코드 서명이 깨져 macOS가 arm64 바이너리를
    SIGKILL(-9)로 죽인다. ad-hoc 재서명으로 실행 가능 상태로 만든다.
    """
    if not (_IS_APPLE_SILICON and os.path.isfile(path)):
        return
    # 다운로드 격리 속성 제거 (Gatekeeper)
    subprocess.run(["xattr", "-d", "com.apple.quarantine", path],
                   capture_output=True)
    # ad-hoc(서명자 '-') 강제 재서명
    res = subprocess.run(["codesign", "--force", "--sign", "-", path],
                         capture_output=True, text=True)
    if res.returncode == 0:
        logger.info(f"chromedriver ad-hoc 재서명 완료: {path}")
    else:
        logger.warning(f"chromedriver 재서명 실패: {res.stderr.strip()}")


def _patch_uc_for_apple_silicon() -> None:
    """uc 패처가 (1) mac-arm64 드라이버를 받고 (2) 패치 후 ad-hoc 재서명하도록 교정 (arm64 전용)."""
    if not _IS_APPLE_SILICON:
        return
    try:
        from undetected_chromedriver.patcher import Patcher
    except Exception as e:  # pragma: no cover
        logger.warning(f"uc 패처 임포트 실패 — arm64 교정 건너뜀: {e}")
        return
    if getattr(Patcher, "_arm64_patched", False):
        return
    _orig_set_platform = Patcher._set_platform_name
    _orig_patch_exe = Patcher.patch_exe

    def _set_platform_name(self):
        _orig_set_platform(self)
        # darwin이면 uc가 mac64/mac-x64로 잘못 지정 → 신형 드라이버는 mac-arm64로 교정
        if self.platform.endswith("darwin") and not getattr(self, "is_old_chromedriver", False):
            self.platform_name = "mac-arm64"

    def _patch_exe(self):
        result = _orig_patch_exe(self)
        # 패치로 깨진 서명을 ad-hoc로 복구 (SIGKILL 방지)
        _codesign_adhoc(self.executable_path)
        return result

    Patcher._set_platform_name = _set_platform_name
    Patcher.patch_exe = _patch_exe
    Patcher._arm64_patched = True
    logger.info("uc 패처를 mac-arm64 + ad-hoc 재서명용으로 교정함 (Apple Silicon)")


def _is_arm64_binary(path: str) -> bool:
    """Mach-O 바이너리가 arm64인지 확인 (헤더 cputype 검사)."""
    try:
        with open(path, "rb") as f:
            f.read(4)  # magic
            cputype = int.from_bytes(f.read(4), "little")
        return cputype == _MACHO_CPUTYPE_ARM64
    except Exception:
        return False


def _purge_wrong_arch_driver() -> None:
    """arm64인데 캐시된 chromedriver가 x86이면 삭제 → uc가 올바른 드라이버를 재다운로드 (arm64 전용)."""
    if not _IS_APPLE_SILICON:
        return
    cache_dir = os.path.expanduser(
        "~/Library/Application Support/undetected_chromedriver"
    )
    for fp in glob.glob(os.path.join(cache_dir, "*chromedriver*")):
        if os.path.isfile(fp) and not _is_arm64_binary(fp):
            try:
                os.remove(fp)
                logger.info(f"x86 chromedriver 캐시 삭제 (arm64 재다운로드 유도): {fp}")
            except Exception as e:
                logger.warning(f"chromedriver 캐시 삭제 실패 ({fp}): {e}")


def _resign_cached_driver() -> None:
    """이미 패치돼 캐시된 arm64 chromedriver를 ad-hoc 재서명 (재사용 시 SIGKILL 방지, arm64 전용).

    uc는 패치된 드라이버가 있으면 patch_exe를 건너뛰므로, 실행 직전에 직접 서명한다.
    """
    if not _IS_APPLE_SILICON:
        return
    cache_dir = os.path.expanduser(
        "~/Library/Application Support/undetected_chromedriver"
    )
    for fp in glob.glob(os.path.join(cache_dir, "*chromedriver*")):
        if os.path.isfile(fp) and _is_arm64_binary(fp):
            _codesign_adhoc(fp)

# Chrome 바이너리 후보 경로 (macOS)
_CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chrome.app/Contents/MacOS/Google Chrome",
    "/Users/Shared/Previously Relocated Items 13/Security/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def _find_chrome_binary() -> str | None:
    """설치된 Chrome 바이너리 경로를 찾는다."""
    # 1. 후보 경로 순차 확인
    for path in _CHROME_PATHS:
        if os.path.isfile(path):
            return path
    # 2. osascript로 macOS에 등록된 Chrome 경로 자동 탐색
    try:
        result = subprocess.run(
            ["osascript", "-e", 'POSIX path of (path to application "Google Chrome")'],
            capture_output=True, text=True, timeout=5,
        )
        app_path = result.stdout.strip()
        if app_path:
            binary = os.path.join(app_path, "Contents/MacOS/Google Chrome")
            if os.path.isfile(binary):
                return binary
    except Exception:
        pass
    return None


def _get_chrome_version() -> int | None:
    """설치된 Chrome 메이저 버전을 감지."""
    chrome_bin = _find_chrome_binary()
    if not chrome_bin:
        return None
    try:
        result = subprocess.run(
            [chrome_bin, "--version"],
            capture_output=True, text=True, timeout=5,
        )
        version_str = result.stdout.strip().split()[-1]
        return int(version_str.split(".")[0])
    except Exception:
        return None


def create_driver(use_profile: bool = False, profile_path: str | None = None) -> uc.Chrome:
    """
    undetected-chromedriver로 로컬 Chrome WebDriver 생성.

    Args:
        use_profile: True면 지정된(또는 기본) 프로필 디렉토리를 --user-data-dir로 사용해
            이전 실행의 네이버 로그인 세션을 재사용한다(비밀번호 재입력 없이 진입 시도).
            이 프로필은 이 도구 전용 디렉토리(기본: config.settings.CHROME_PROFILE_DIR)이며,
            사용자가 평소 쓰는 Chrome 프로필과는 분리되어 있어 서로 충돌하지 않는다.
            CHROME_PROFILE_PATH를 사용자의 실제 Chrome 프로필로 지정할 수도 있지만, 그 경우
            해당 프로필을 쓰는 Chrome 창을 먼저 모두 닫아야 한다(동시 사용 시 잠금 오류).
        profile_path: use_profile=True일 때 사용할 프로필 디렉토리 경로. None이면 기본값 사용.
    """
    options = uc.ChromeOptions()

    chrome_bin = _find_chrome_binary()
    if chrome_bin:
        options.binary_location = chrome_bin

    if use_profile:
        from config.settings import CHROME_PROFILE_DIR
        profile_dir = Path(profile_path) if profile_path else CHROME_PROFILE_DIR
        profile_dir.mkdir(parents=True, exist_ok=True)
        options.add_argument(f"--user-data-dir={profile_dir}")
        logger.info(f"Chrome 프로필 재사용: {profile_dir}")

    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=ko-KR")
    options.add_argument("--log-level=3")

    version = _get_chrome_version()

    # Apple Silicon: 잘못된 x86 드라이버 버그 우회 (Bad CPU type 방지)
    _patch_uc_for_apple_silicon()
    _purge_wrong_arch_driver()
    _resign_cached_driver()  # 재사용되는 패치된 캐시도 서명 (SIGKILL -9 방지)

    driver = uc.Chrome(
        options=options,
        version_main=version,
    )

    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    # 네이버 블로그 클립보드 권한 자동 허용 (붙여넣기 시 팝업 방지)
    try:
        driver.execute_cdp_cmd("Browser.grantPermissions", {
            "origin": "https://blog.naver.com",
            "permissions": ["clipboardReadWrite", "clipboardSanitizedWrite"],
        })
        logger.info("Clipboard permissions granted for blog.naver.com")
    except Exception as e:
        logger.warning(f"Could not grant clipboard permissions: {e}")

    logger.info("Chrome WebDriver created with undetected-chromedriver")
    return driver


def close_driver(driver: uc.Chrome) -> None:
    """WebDriver 안전 종료."""
    try:
        driver.quit()
        logger.info("WebDriver closed")
    except Exception as e:
        logger.warning(f"Error closing WebDriver: {e}")
