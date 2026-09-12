import time
import random
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config.settings import NAVER_LOGIN_URL, NAVER_BLOG_WRITE_URL, LOGIN_WAIT_TIMEOUT
from config.selectors import LoginSelectors
from utils.retry import retry

logger = logging.getLogger(__name__)


class NaverLogin:
    """네이버 로그인 자동화 (클립보드 붙여넣기 방식)."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, LOGIN_WAIT_TIMEOUT)

    @retry(max_attempts=2, exceptions=(TimeoutException, Exception))
    def login(self, naver_id: str, naver_pw: str, blog_id: str = None) -> bool:
        """
        네이버 로그인 실행.

        1. 로그인 페이지 이동 (리턴 URL: 블로그 글쓰기)
        2. ID 클립보드 붙여넣기
        3. PW 클립보드 붙여넣기
        4. 로그인 버튼 클릭
        5. 로그인 성공 검증
        """
        logger.info("Starting Naver login...")

        login_url = NAVER_LOGIN_URL
        if blog_id:
            return_url = NAVER_BLOG_WRITE_URL.format(blog_id=blog_id)
            login_url = f"{NAVER_LOGIN_URL}?url={return_url}"
        self.driver.get(login_url)
        time.sleep(random.uniform(1.5, 2.5))

        # "ID/전화번호" 탭 클릭 (QR코드 탭이 기본일 수 있음)
        try:
            id_tab = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, LoginSelectors.ID_PW_TAB))
            )
            id_tab.click()
            time.sleep(random.uniform(0.5, 1.0))
            logger.debug("Clicked ID/PW tab")
        except TimeoutException:
            logger.debug("ID/PW tab not found, already on ID login form")

        # ID 입력 (JavaScript로 직접 입력 + 이벤트 발생)
        id_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, LoginSelectors.ID_INPUT))
        )
        self._js_input(id_input, naver_id)
        logger.debug("ID input completed")
        time.sleep(random.uniform(0.8, 1.5))

        # PW 입력
        pw_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, LoginSelectors.PW_INPUT))
        )
        self._js_input(pw_input, naver_pw)
        logger.debug("PW input completed")
        time.sleep(random.uniform(0.8, 1.5))

        # 로그인 버튼 클릭
        login_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, LoginSelectors.LOGIN_BUTTON))
        )
        login_btn.click()
        logger.info("Login button clicked")
        time.sleep(2)

        return self._verify_login()

    def _js_input(self, element, text: str) -> None:
        """JavaScript로 입력 필드에 값 설정 (포커스 문제 방지)."""
        self.driver.execute_script("""
            var el = arguments[0];
            var text = arguments[1];
            el.focus();
            el.value = text;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        """, element, text)

    def _verify_login(self) -> bool:
        """로그인 성공 여부 확인 (URL redirect 체크)."""
        current_url = self.driver.current_url
        if "nidlogin" not in current_url:
            logger.info(f"Login successful. URL: {current_url}")
            return True

        try:
            error = self.driver.find_element(
                By.CSS_SELECTOR, LoginSelectors.LOGIN_ERROR_MSG
            )
            logger.error(f"Login failed: {error.text}")
        except Exception:
            logger.error("Login failed: still on login page")

        return False
