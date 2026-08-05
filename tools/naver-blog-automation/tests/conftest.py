"""테스트 전용 설정.

이 저장소의 automation/* 모듈은 실 Selenium/Chrome을 전제로 한다. 이 프로젝트는
"네이버 로그인은 사용자 PC의 로컬 Chrome에서만 실행한다"는 원칙이므로, CI/샌드박스
환경에는 실제 Chrome이 없다(있어서도 안 된다). 따라서 selenium/undetected_chromedriver/
pyautogui/pyperclip을 가벼운 가짜 모듈로 대체해 '임포트'만 가능하게 하고, 각 테스트는
automation.orchestrator의 개별 함수(create_driver, NaverLogin, SmartEditorOne)를
monkeypatch로 교체해 실제 브라우저 동작 없이 로직만 검증한다.
"""
from __future__ import annotations

import sys
import types

import pytest


def _install_fake_selenium():
    if "selenium" in sys.modules:
        return

    selenium = types.ModuleType("selenium")
    webdriver = types.ModuleType("selenium.webdriver")
    common = types.ModuleType("selenium.webdriver.common")
    by_mod = types.ModuleType("selenium.webdriver.common.by")
    keys_mod = types.ModuleType("selenium.webdriver.common.keys")
    ac_mod = types.ModuleType("selenium.webdriver.common.action_chains")
    support = types.ModuleType("selenium.webdriver.support")
    ui_mod = types.ModuleType("selenium.webdriver.support.ui")
    ec_mod = types.ModuleType("selenium.webdriver.support.expected_conditions")
    chrome_mod = types.ModuleType("selenium.webdriver.chrome")
    chrome_opts_mod = types.ModuleType("selenium.webdriver.chrome.options")
    exc_mod = types.ModuleType("selenium.common.exceptions")
    common_top = types.ModuleType("selenium.common")

    class By:
        CSS_SELECTOR = "css selector"
        XPATH = "xpath"

    class Keys:
        ENTER = "\n"
        ESCAPE = "\x1b"
        ARROW_DOWN = "down"
        ARROW_RIGHT = "right"
        COMMAND = "command"
        CONTROL = "control"
        SHIFT = "shift"
        RETURN = "\r"

    class _Chain:
        def __init__(self, *a, **k): pass
        def move_to_element_with_offset(self, *a, **k): return self
        def pause(self, *a, **k): return self
        def click(self, *a, **k): return self
        def perform(self, *a, **k): return None
        def send_keys(self, *a, **k): return self
        def key_down(self, *a, **k): return self
        def key_up(self, *a, **k): return self

    class WebDriverWait:
        def __init__(self, driver, timeout): self.driver = driver
        def until(self, cond): return cond(self.driver)

    def _presence(*a, **k):
        def cond(driver): raise TimeoutException("stub: no real DOM in tests")
        return cond

    class ExpectedConditions:
        element_to_be_clickable = staticmethod(_presence)
        presence_of_element_located = staticmethod(_presence)

    class TimeoutException(Exception):
        pass

    class NoSuchElementException(Exception):
        pass

    class ChromeOptions:
        def __init__(self): self._args = []
        def add_argument(self, a): self._args.append(a)

    by_mod.By = By
    keys_mod.Keys = Keys
    ac_mod.ActionChains = _Chain
    ui_mod.WebDriverWait = WebDriverWait
    ec_mod.element_to_be_clickable = ExpectedConditions.element_to_be_clickable
    ec_mod.presence_of_element_located = ExpectedConditions.presence_of_element_located
    exc_mod.TimeoutException = TimeoutException
    exc_mod.NoSuchElementException = NoSuchElementException
    chrome_opts_mod.Options = ChromeOptions

    common.by = by_mod
    common.keys = keys_mod
    common.action_chains = ac_mod
    support.ui = ui_mod
    support.expected_conditions = ec_mod
    webdriver.common = common
    webdriver.support = support
    webdriver.chrome = chrome_mod
    chrome_mod.options = chrome_opts_mod
    webdriver.Chrome = object
    selenium.webdriver = webdriver
    selenium.common = common_top
    common_top.exceptions = exc_mod

    for name, mod in [
        ("selenium", selenium), ("selenium.webdriver", webdriver),
        ("selenium.webdriver.common", common), ("selenium.webdriver.common.by", by_mod),
        ("selenium.webdriver.common.keys", keys_mod),
        ("selenium.webdriver.common.action_chains", ac_mod),
        ("selenium.webdriver.support", support), ("selenium.webdriver.support.ui", ui_mod),
        ("selenium.webdriver.support.expected_conditions", ec_mod),
        ("selenium.webdriver.chrome", chrome_mod),
        ("selenium.webdriver.chrome.options", chrome_opts_mod),
        ("selenium.common", common_top), ("selenium.common.exceptions", exc_mod),
    ]:
        sys.modules[name] = mod

    # undetected_chromedriver
    uc_mod = types.ModuleType("undetected_chromedriver")
    uc_mod.ChromeOptions = ChromeOptions
    uc_mod.Chrome = object
    sys.modules["undetected_chromedriver"] = uc_mod
    patcher_mod = types.ModuleType("undetected_chromedriver.patcher")
    class Patcher:
        pass
    patcher_mod.Patcher = Patcher
    sys.modules["undetected_chromedriver.patcher"] = patcher_mod

    # pyautogui / pyperclip (헤드리스 테스트 환경엔 디스플레이가 없음)
    pyautogui_mod = types.ModuleType("pyautogui")
    pyautogui_mod.hotkey = lambda *a, **k: None
    sys.modules["pyautogui"] = pyautogui_mod

    pyperclip_mod = types.ModuleType("pyperclip")
    pyperclip_mod.copy = lambda *a, **k: None
    sys.modules["pyperclip"] = pyperclip_mod


_install_fake_selenium()


@pytest.fixture(autouse=True, scope="session")
def _fake_selenium_session():
    _install_fake_selenium()
    yield
