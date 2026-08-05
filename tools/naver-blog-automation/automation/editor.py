"""네이버 블로그 Smart Editor ONE 자동화.

원본(choigpt-ai/naver-blog-automation)의 automation/editor.py를 기반으로 하되:
- 저장 관련 함수들이 "발행" 계열 텍스트(config.safety.FORBIDDEN_BUTTON_TEXTS)를
  가진 요소는 어떤 경로로도 후보에서 배제하도록 재확인하는 가드를 추가했다.
- 사진 설명(캡션) 입력 메서드(set_last_image_caption)를 추가했다.
- 카카오 CTA 이미지 링크 자동화, 카테고리 자동 선택 등 기프트클린 요구사항에
  없는 기능은 제거했다(공격면 축소).

주의: 아래 CSS/XPath 셀렉터는 네이버가 UI를 바꾸면 깨질 수 있다. 이 파일에서
셀렉터가 바뀌어야 할 지점은 config/selectors.py의 EditorSelectors 클래스다.
셀렉터가 모두 실패하면 예외 없이 False를 반환/로그로 남기고 상위 호출부가
"안전하게 중단"하도록 설계되어 있다(automation/orchestrator.py 참고).
"""
import time
import random
import logging
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.settings import (
    NAVER_BLOG_WRITE_URL,
    EDITOR_LOAD_TIMEOUT,
    TYPING_DELAY,
    THINK_PAUSE_RANGE,
    REREAD_PROBABILITY,
)
from config.selectors import EditorSelectors
from config.safety import FORBIDDEN_BUTTON_TEXTS
from utils.retry import retry

logger = logging.getLogger(__name__)

TYPING_CHUNK_SIZE = 100


def _is_forbidden_text(text: str) -> bool:
    """저장 버튼 후보 텍스트가 '발행' 계열 금지어를 포함하는지 확인 (모든 클릭 경로 공통 가드)."""
    t = (text or "").strip()
    return any(bad in t for bad in FORBIDDEN_BUTTON_TEXTS)


class SmartEditorOne:
    """네이버 블로그 Smart Editor ONE 자동화."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, EDITOR_LOAD_TIMEOUT)

    # ── 유틸리티 ──────────────────────────────────────────────

    def _random_sleep(self, base: float, variance: float = 0.5) -> None:
        lo = base * (1 - variance)
        hi = base * (1 + variance)
        time.sleep(random.uniform(lo, hi))

    def _human_click(self, element) -> None:
        actions = ActionChains(self.driver)
        actions.move_to_element_with_offset(
            element, random.randint(-3, 3), random.randint(-3, 3),
        )
        actions.pause(random.uniform(0.1, 0.3))
        actions.click()
        actions.perform()

    def _type_like_human(self, text: str) -> None:
        for start in range(0, len(text), TYPING_CHUNK_SIZE):
            chunk = text[start:start + TYPING_CHUNK_SIZE]
            actions = ActionChains(self.driver)
            for char in chunk:
                actions.send_keys(char)
                delay = random.uniform(TYPING_DELAY * 0.5, TYPING_DELAY * 4.0)
                if random.random() < 0.05:
                    delay += random.uniform(0.3, 0.8)
                actions.pause(delay)
            actions.perform()

    def think_pause(self, lo: float | None = None, hi: float | None = None) -> None:
        lo = THINK_PAUSE_RANGE[0] if lo is None else lo
        hi = THINK_PAUSE_RANGE[1] if hi is None else hi
        time.sleep(random.uniform(lo, hi))

    def reread_scroll(self, probability: float | None = None) -> None:
        probability = REREAD_PROBABILITY if probability is None else probability
        if random.random() > probability:
            return
        try:
            self.driver.execute_script("window.scrollBy(0, -320);")
            self._random_sleep(1.6, 0.4)
            self.driver.execute_script("window.scrollBy(0, 320);")
            self._random_sleep(0.9, 0.4)
        except Exception:
            pass

    # ── 네비게이션 ────────────────────────────────────────────

    def navigate_to_editor(self, blog_id: str) -> None:
        url = NAVER_BLOG_WRITE_URL.format(blog_id=blog_id)
        self.driver.get(url)
        logger.info(f"Navigating to editor: {url}")
        self._random_sleep(3)

        current_url = self.driver.current_url
        logger.info(f"Current URL after navigation: {current_url}")

        self._dismiss_draft_popup()

        try:
            self._switch_to_editor_iframe()
            self._wait_for_editor_load()
        except TimeoutException:
            logger.info("No iframe found, checking editor directly...")
            self.driver.switch_to.default_content()
            self._wait_for_editor_load()

        self._dismiss_popup()

    def _switch_to_editor_iframe(self) -> None:
        self.driver.switch_to.default_content()
        for selector in [EditorSelectors.MAIN_FRAME, "iframe"]:
            try:
                iframe = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                self.driver.switch_to.frame(iframe)
                logger.info(f"Switched to iframe: {selector}")
                return
            except TimeoutException:
                continue
        raise TimeoutException("No editor iframe found")

    def _wait_for_editor_load(self) -> None:
        for selector in [EditorSelectors.EDITOR_CONTAINER, ".se-content", ".editor_comp", "#content"]:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                self._random_sleep(3)
                logger.info(f"Editor loaded (selector: {selector})")
                return
            except TimeoutException:
                continue
        page_source_snippet = self.driver.page_source[:2000]
        logger.error(f"Editor not found. Page source snippet: {page_source_snippet}")
        raise TimeoutException("Editor elements not found on page")

    def _dismiss_popup(self) -> None:
        try:
            close_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, EditorSelectors.POPUP_CLOSE))
            )
            close_btn.click()
            self._random_sleep(0.5)
            logger.debug("Popup dismissed")
        except TimeoutException:
            logger.debug("No popup found")

    def _dismiss_draft_popup(self) -> None:
        for by, selector in [
            (By.CSS_SELECTOR, EditorSelectors.DRAFT_POPUP_CANCEL),
            (By.XPATH, EditorSelectors.DRAFT_POPUP_CANCEL_ALT),
        ]:
            try:
                cancel_btn = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((by, selector))
                )
                cancel_btn.click()
                self._random_sleep(1)
                logger.info("Draft popup dismissed (clicked cancel)")
                return
            except TimeoutException:
                continue
        logger.debug("No draft popup found")

    # ── 입력 ──────────────────────────────────────────────────

    @retry(max_attempts=3, exceptions=(TimeoutException, NoSuchElementException))
    def input_title(self, title: str) -> None:
        logger.info(f"Entering title: {title[:50]}...")
        self._ensure_editor_iframe()
        title_el = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, EditorSelectors.TITLE_AREA))
        )
        self._human_click(title_el)
        self._random_sleep(0.5)
        self._type_like_human(title)
        logger.debug("Title entered via ActionChains typing")

    @staticmethod
    def _clean_paragraph(p: str) -> str:
        import re
        p = p.strip()
        p = re.sub(r"^#{1,6}\s+", "", p)
        p = re.sub(r"\*\*(.+?)\*\*", r"\1", p)
        p = re.sub(r"\*(.+?)\*", r"\1", p)
        p = p.replace("**", "").replace("*", "").replace("`", "")
        return p.strip()

    def _type_paragraphs(self, text: str) -> None:
        paragraphs = text.split("\n")
        for i, paragraph in enumerate(paragraphs):
            clean = self._clean_paragraph(paragraph)
            if clean:
                self._type_like_human(clean)
                self._random_sleep(0.3)
            if i < len(paragraphs) - 1:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
                self._random_sleep(0.2)

    def _focus_body_end(self) -> bool:
        try:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self._random_sleep(0.2)
        except Exception:
            pass
        try:
            info = self.driver.execute_script("""
                var comps = document.querySelectorAll('.se-main-container > .se-component, .se-component');
                if (!comps.length) return {kind: 'none'};
                var lastC = comps[comps.length - 1];
                if (lastC.classList.contains('se-text')) {
                    var paras = lastC.querySelectorAll('.se-text-paragraph');
                    if (paras.length) {
                        var el = paras[paras.length - 1];
                        el.scrollIntoView({block: 'center'});
                        return {kind: 'text', el: el};
                    }
                }
                lastC.scrollIntoView({block: 'center'});
                return {kind: 'other', el: lastC};
            """)
        except Exception as e:
            logger.debug(f"마지막 컴포넌트 탐색 실패: {e}")
            return False
        kind = (info or {}).get("kind")
        el = (info or {}).get("el")
        if kind in (None, "none") or el is None:
            return False

        if kind == "text":
            try:
                self._human_click(el)
            except Exception:
                try:
                    self.driver.execute_script("arguments[0].click();", el)
                except Exception:
                    return False
            try:
                actions = ActionChains(self.driver)
                actions.key_down(Keys.COMMAND).send_keys(Keys.ARROW_DOWN).key_up(Keys.COMMAND)
                actions.key_down(Keys.COMMAND).send_keys(Keys.ARROW_RIGHT).key_up(Keys.COMMAND)
                actions.perform()
            except Exception:
                pass
            return True

        try:
            self.driver.execute_script("arguments[0].click();", el)
            self._random_sleep(0.4)
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            self._random_sleep(0.4)
            made = self.driver.execute_script("""
                var comps = document.querySelectorAll('.se-component');
                var lastC = comps[comps.length - 1];
                return lastC.classList.contains('se-text');
            """)
            if made:
                logger.info("이미지 뒤에 새 문단 생성 — 캐럿 복귀 완료")
                return True
        except Exception as e:
            logger.debug(f"이미지 뒤 문단 생성 실패: {e}")

        try:
            made = self.driver.execute_script("""
                var comps = document.querySelectorAll('.se-component');
                var lastC = comps[comps.length - 1];
                var btn = lastC.querySelector('.se-component-edge-button[data-direction="bottom"]');
                if (btn) { btn.click(); return true; }
                return false;
            """)
            if made:
                self._random_sleep(0.4)
                logger.info("edge 버튼으로 이미지 뒤 문단 생성")
                return True
        except Exception:
            pass
        logger.warning("본문 끝 캐럿 복귀 실패 — 폴백 경로로 진행")
        return False

    @retry(max_attempts=3, exceptions=(TimeoutException, NoSuchElementException))
    def input_body(self, body: str) -> None:
        logger.info("Entering body content...")
        self._ensure_editor_iframe()
        body_el = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, EditorSelectors.BODY_AREA))
        )
        self._human_click(body_el)
        self._focus_body_end()
        self._random_sleep(0.5)
        self._type_paragraphs(body)
        logger.debug("Body entered (first section)")

    @retry(max_attempts=2, exceptions=(TimeoutException, NoSuchElementException))
    def input_body_chunk(self, text: str) -> None:
        self._ensure_editor_iframe()
        if not self._focus_body_end():
            body_el = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, EditorSelectors.BODY_AREA))
            )
            self._human_click(body_el)
            try:
                ActionChains(self.driver).key_down(Keys.COMMAND).send_keys(
                    Keys.ARROW_DOWN).key_up(Keys.COMMAND).perform()
            except Exception:
                pass
        self._random_sleep(0.3)
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        self._random_sleep(0.2)
        self._type_paragraphs(text)
        logger.debug("Body chunk appended")

    # ── 이미지 ────────────────────────────────────────────────

    def upload_images(self, image_paths: list[str]) -> bool:
        if not image_paths:
            return True
        inserted = 0
        for path in image_paths:
            if self._paste_image(path):
                inserted += 1
                continue
            logger.info(f"클립보드 붙여넣기 실패 → 파일 input 폴백 시도: {path}")
            try:
                if self._try_upload_all([path]):
                    inserted += 1
                else:
                    logger.warning(f"이미지 삽입 실패(스킵): {path}")
            except Exception as e:
                logger.warning(f"파일 input 폴백 실패({path}): {e}")
        if inserted == 0:
            logger.warning("모든 이미지 삽입 실패 — 이미지 없이 저장 진행")
        else:
            logger.info(f"이미지 {inserted}/{len(image_paths)}장 삽입 완료")
        return inserted > 0

    def set_last_image_caption(self, caption: str) -> bool:
        """방금 삽입한 이미지 아래의 캡션(사진 설명) 입력란에 설명을 타이핑한다.

        SmartEditor ONE은 이미지 아래에 '사진 설명을 입력하세요' placeholder를 가진
        캡션 단락을 자동 생성한다. 실패해도 본문 작성은 계속한다(비치명적).
        """
        if not caption:
            return False
        self._ensure_editor_iframe()
        try:
            found = self.driver.execute_script("""
                var caps = document.querySelectorAll('.se-component.se-image .se-caption, '
                    + '.se-component.se-image [class*="caption"] .se-text-paragraph, '
                    + '.se-component.se-image .se-text-paragraph');
                if (!caps.length) return false;
                var el = caps[caps.length - 1];
                el.scrollIntoView({block: 'center'});
                el.click();
                return true;
            """)
            if not found:
                logger.warning("이미지 캡션 입력란을 찾지 못함 — 설명 삽입 스킵")
                return False
            self._random_sleep(0.4)
            self._type_like_human(caption)
            logger.info("이미지 캡션(사진 설명) 입력 완료")
            return True
        except Exception as e:
            logger.warning(f"이미지 캡션 입력 실패(비치명적): {e}")
            return False

    def _count_body_images(self) -> int:
        try:
            return int(self.driver.execute_script(
                "return document.querySelectorAll("
                "'.se-image, .se-component.se-image, img.se-image-resource').length;"
            ) or 0)
        except Exception:
            return 0

    def _paste_image(self, path: str) -> bool:
        import platform as _platform
        from utils.clipboard import copy_image_to_clipboard

        self._ensure_editor_iframe()
        if not copy_image_to_clipboard(path):
            return False

        if not self._focus_body_end():
            try:
                body_el = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, EditorSelectors.BODY_AREA))
                )
                self._human_click(body_el)
            except Exception:
                logger.warning("붙여넣기: 본문 포커스 실패")
                return False
        self._random_sleep(0.4)

        before = self._count_body_images()
        is_mac = _platform.system() == "Darwin"
        mod = Keys.COMMAND if is_mac else Keys.CONTROL
        try:
            ActionChains(self.driver).key_down(mod).send_keys("v").key_up(mod).perform()
        except Exception as e:
            logger.debug(f"ActionChains 붙여넣기 예외: {e}")

        if self._wait_image_inserted(before):
            logger.info(f"이미지 붙여넣기 성공(ActionChains): {Path(path).name}")
            return True

        try:
            import pyautogui
            pyautogui.hotkey("command", "v") if is_mac else pyautogui.hotkey("ctrl", "v")
        except Exception as e:
            logger.debug(f"pyautogui 붙여넣기 예외: {e}")

        if self._wait_image_inserted(before):
            logger.info(f"이미지 붙여넣기 성공(pyautogui): {Path(path).name}")
            return True

        logger.warning(f"붙여넣기 후 이미지 증가 미확인: {Path(path).name}")
        return False

    def _wait_image_inserted(self, before_count: int, timeout: float = 12.0) -> bool:
        steps = int(timeout / 0.5)
        for _ in range(steps):
            self._random_sleep(0.5)
            self._ensure_editor_iframe()
            if self._count_body_images() > before_count:
                self._random_sleep(1.5)
                return True
        return False

    def _try_upload_all(self, image_paths: list[str]) -> bool:
        for path in image_paths:
            abs_path = str(Path(path).resolve())
            file_input = self._locate_file_input()
            if file_input is None:
                logger.warning(f"file input을 어떤 프레임에서도 못 찾음 — 이미지 스킵(파일창 방지): {abs_path}")
                self._ensure_editor_iframe()
                return False
            try:
                self.driver.execute_script(
                    "arguments[0].style.display='block';"
                    "arguments[0].style.visibility='visible';"
                    "arguments[0].style.height='1px';"
                    "arguments[0].style.width='1px';",
                    file_input,
                )
            except Exception:
                pass
            file_input.send_keys(abs_path)
            logger.info(f"Uploaded: {abs_path}")
            self._random_sleep(4)
            self._ensure_editor_iframe()
        return True

    def _locate_file_input(self):
        sel = "input[type='file']"

        def here():
            els = self.driver.find_elements(By.CSS_SELECTOR, sel)
            return els[0] if els else None

        el = here()
        if el:
            return el
        self.driver.switch_to.default_content()
        el = here()
        if el:
            return el
        top = self.driver.find_elements(By.CSS_SELECTOR, "iframe")
        for i in range(len(top)):
            self.driver.switch_to.default_content()
            tf = self.driver.find_elements(By.CSS_SELECTOR, "iframe")
            if i >= len(tf):
                break
            try:
                self.driver.switch_to.frame(tf[i])
            except Exception:
                continue
            el = here()
            if el:
                return el
            nested = self.driver.find_elements(By.CSS_SELECTOR, "iframe")
            for j in range(len(nested)):
                self.driver.switch_to.default_content()
                tf2 = self.driver.find_elements(By.CSS_SELECTOR, "iframe")
                if i >= len(tf2):
                    break
                try:
                    self.driver.switch_to.frame(tf2[i])
                    nf = self.driver.find_elements(By.CSS_SELECTOR, "iframe")
                    if j >= len(nf):
                        break
                    self.driver.switch_to.frame(nf[j])
                except Exception:
                    continue
                el = here()
                if el:
                    return el
        self.driver.switch_to.default_content()
        return None

    # ── 화면 모드 ─────────────────────────────────────────────

    def _ensure_editor_iframe(self) -> None:
        try:
            self._switch_to_editor_iframe()
        except TimeoutException:
            self.driver.switch_to.default_content()

    def switch_to_mobile_view(self) -> bool:
        self.driver.switch_to.default_content()
        clicked = self.driver.execute_script("""
            var btns = document.querySelectorAll('button');
            for (var i = 0; i < btns.length; i++) {
                var t = btns[i].textContent.trim();
                if (t === 'PC 화면' || t.includes('PC 화면')) {
                    btns[i].click();
                    return true;
                }
            }
            return false;
        """)
        if clicked:
            self._random_sleep(1)
            logger.info("모바일 화면 모드로 전환됨")
        else:
            logger.warning("'PC 화면' 버튼 없음 — 이미 모바일 모드이거나 버튼 위치 변경됨")
        self._ensure_editor_iframe()
        return clicked

    # ── 저장 (임시저장 전용 — 발행 경로 없음) ────────────────────

    def save(self) -> bool:
        """임시저장 버튼 클릭. '발행' 계열 텍스트를 가진 요소는 절대 클릭하지 않는다
        (config.safety.FORBIDDEN_BUTTON_TEXTS로 3중 필터링, _is_forbidden_text 참고)."""
        logger.info("Temp-saving post (임시저장)...")

        if self._js_click_temp_save():
            self._random_sleep(3)
            logger.info("임시저장 clicked (JS)")
            return True

        try:
            self.driver.switch_to.default_content()
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self._random_sleep(1)
            self._ensure_editor_iframe()
        except Exception:
            pass
        if self._js_click_temp_save():
            self._random_sleep(3)
            logger.info("임시저장 clicked (JS, 패널 닫은 후)")
            return True

        save_btn = self._find_temp_save_button()
        if save_btn is None:
            self._log_save_candidates()
            logger.error("임시저장 button not found in any context — 안전하게 중단합니다")
            return False

        self._human_click(save_btn)
        self._random_sleep(3)
        logger.info("임시저장 button clicked (element)")
        return True

    def _js_click_temp_save(self) -> bool:
        """JS로 '임시저장' 컨트롤을 찾아 클릭. '발행'류 텍스트는 find()가 아예 후보에서 제외한다."""
        self.driver.switch_to.default_content()
        try:
            return bool(self.driver.execute_script("""
                var FORBIDDEN = arguments[0];
                function forbidden(t){
                    for (var i=0;i<FORBIDDEN.length;i++){ if (t.indexOf(FORBIDDEN[i])!==-1) return true; }
                    return false;
                }
                function find(doc){
                    var els = doc.querySelectorAll('button, a, [role="button"], span[onclick]');
                    for (var i=0;i<els.length;i++){
                        var t=(els[i].textContent||'').trim();
                        if (forbidden(t)) continue;
                        if (t==='임시저장') return els[i];
                    }
                    for (var i=0;i<els.length;i++){
                        var t=(els[i].textContent||'').trim();
                        if (forbidden(t)) continue;
                        if (t.indexOf('임시저장')!==-1) return els[i];
                    }
                    for (var i=0;i<els.length;i++){
                        var t=(els[i].textContent||'').trim();
                        if (forbidden(t)) continue;
                        if (t.indexOf('저장')!==-1) return els[i];
                    }
                    return null;
                }
                function search(doc){
                    var b=find(doc); if(b) return b;
                    var ifr=doc.querySelectorAll('iframe');
                    for(var i=0;i<ifr.length;i++){
                        try{ var d=ifr[i].contentDocument||ifr[i].contentWindow.document; if(d){ var r=search(d); if(r) return r; } }catch(e){}
                    }
                    return null;
                }
                var btn=search(document);
                if(!btn) return false;
                btn.scrollIntoView({block:'center'});
                btn.click();
                return true;
            """, list(FORBIDDEN_BUTTON_TEXTS)))
        except Exception as e:
            logger.warning(f"JS 임시저장 클릭 실패: {e}")
            return False

    def _log_save_candidates(self) -> None:
        try:
            cands = self.driver.execute_script("""
                function collect(doc, out){
                    var els = doc.querySelectorAll('button, a, [role="button"]');
                    for (var i=0;i<els.length;i++){
                        var t=(els[i].textContent||'').trim();
                        if (t && t.length<=14) out.push(t);
                    }
                    var ifr=doc.querySelectorAll('iframe');
                    for(var j=0;j<ifr.length;j++){
                        try{ var d=ifr[j].contentDocument||ifr[j].contentWindow.document; if(d) collect(d,out); }catch(e){}
                    }
                }
                var out=[]; collect(document,out); return out;
            """)
            logger.warning(f"임시저장 후보 버튼/링크 텍스트: {cands}")
        except Exception as e:
            logger.debug(f"save 후보 로깅 실패: {e}")

    def _find_temp_save_button(self):
        self.driver.switch_to.default_content()

        for selector in EditorSelectors.TEMP_SAVE_BUTTON_CANDIDATES:
            els = self.driver.find_elements(By.CSS_SELECTOR, selector)
            for el in els:
                if el.is_displayed() and not _is_forbidden_text(el.text):
                    logger.info(f"임시저장 button found (CSS): {selector}")
                    return el

        for xpath in EditorSelectors.TEMP_SAVE_XPATH_CANDIDATES:
            els = self.driver.find_elements(By.XPATH, xpath)
            for el in els:
                if el.is_displayed() and not _is_forbidden_text(el.text):
                    logger.info(f"임시저장 button found (XPath): {xpath}")
                    return el

        try:
            self._switch_to_editor_iframe()
            for xpath in EditorSelectors.TEMP_SAVE_XPATH_CANDIDATES:
                els = self.driver.find_elements(By.XPATH, xpath)
                for el in els:
                    if el.is_displayed() and not _is_forbidden_text(el.text):
                        logger.info(f"임시저장 button found in iframe: {xpath}")
                        return el
        except TimeoutException:
            pass

        self.driver.switch_to.default_content()
        return self._find_temp_save_btn_js()

    def _find_temp_save_btn_js(self):
        try:
            el = self.driver.execute_script("""
                var FORBIDDEN = arguments[0];
                function forbidden(t){
                    for (var i=0;i<FORBIDDEN.length;i++){ if (t.indexOf(FORBIDDEN[i])!==-1) return true; }
                    return false;
                }
                function findBtn(doc) {
                    var buttons = doc.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {
                        var t = buttons[i].textContent.trim();
                        if (forbidden(t)) continue;
                        if (t === '임시저장') return buttons[i];
                    }
                    for (var j = 0; j < buttons.length; j++) {
                        var t = buttons[j].textContent.trim();
                        if (forbidden(t)) continue;
                        if (t.includes('저장')) return buttons[j];
                    }
                    return null;
                }
                var btn = findBtn(document);
                if (btn) return btn;
                var iframes = document.querySelectorAll('iframe');
                for (var i = 0; i < iframes.length; i++) {
                    try {
                        var b = findBtn(iframes[i].contentDocument);
                        if (b) return b;
                    } catch(e) {}
                }
                return null;
            """, list(FORBIDDEN_BUTTON_TEXTS))
            if el:
                logger.info("임시저장 button found via JS")
            return el
        except Exception as e:
            logger.warning(f"JS 임시저장 search failed: {e}")
            return None

    # ── 태그 ──────────────────────────────────────────────────

    def open_settings_panel(self) -> bool:
        """태그 입력 사이드패널을 연다.

        네이버 UI 특성상 이 패널의 진입 버튼 라벨이 '발행'이다. 이 함수는 패널을
        '여는' 것만 하며, 그 안의 최종 발행 확정 버튼은 절대 클릭하지 않는다
        (그런 버튼을 클릭하는 코드는 이 파일 어디에도 없다). 실제 저장은
        save()가 임시저장 버튼만 찾아 클릭한다.
        """
        self.driver.switch_to.default_content()
        try:
            els = self.driver.find_elements(By.XPATH, EditorSelectors.PUBLISH_BTN_XPATH)
            for el in els:
                if el.is_displayed():
                    self._human_click(el)
                    self._random_sleep(2)
                    logger.info("설정 패널 열림 (발행 버튼 클릭 — 패널 오픈 용도, 저장 아님)")
                    return True
        except Exception as e:
            logger.debug(f"발행 버튼 XPath 클릭 실패, JS로 재시도: {e}")

        clicked = self.driver.execute_script("""
            var btns = document.querySelectorAll('button');
            for (var i = 0; i < btns.length; i++) {
                if (btns[i].textContent.trim() === '발행') { btns[i].click(); return true; }
            }
            return false;
        """)
        if clicked:
            self._random_sleep(2)
            logger.info("설정 패널 열림 (발행 버튼 JS 클릭 — 패널 오픈 용도, 저장 아님)")
            return True
        logger.warning("'발행' 버튼 없음 — 설정 패널을 열지 못함 (태그는 인라인 입력으로 폴백)")
        return False

    def set_tags(self, tags: list[str]) -> bool:
        if not tags:
            return True
        limited = tags[:5]
        logger.info(f"Setting tags: {limited}")

        self.driver.switch_to.default_content()
        self._random_sleep(0.5)
        tag_input = self.driver.execute_script("""
            function findTagInput(doc) {
                var inputs = Array.from(doc.querySelectorAll('input'));
                return inputs.find(function(i) {
                    var ph = (i.placeholder || '').toLowerCase();
                    var nm = (i.name || '').toLowerCase();
                    var cls = (i.className || '').toLowerCase();
                    var aria = (i.getAttribute('aria-label') || '').toLowerCase();
                    return ph.includes('태그') || nm.includes('tag')
                        || cls.includes('tag') || aria.includes('태그');
                }) || null;
            }
            var found = findTagInput(document);
            if (found) return found;
            var iframes = document.querySelectorAll('iframe');
            for (var i = 0; i < iframes.length; i++) {
                try {
                    var doc = iframes[i].contentDocument || iframes[i].contentWindow.document;
                    found = findTagInput(doc);
                    if (found) return found;
                } catch(e) {}
            }
            return null;
        """)

        if tag_input is None:
            logger.warning("Tag input not found (인라인/iframe 포함) — skipping tags (비치명적)")
            return False

        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView(true); arguments[0].focus();", tag_input
            )
            self._random_sleep(0.5)
            for tag in limited:
                self._type_like_human(tag)
                tag_input.send_keys(Keys.RETURN)
                self._random_sleep(0.6)
                logger.info(f"Tag entered: {tag}")
            logger.info(f"Tags entered: {limited}")
            return True
        except Exception as e:
            logger.warning(f"Tag input failed: {e}")
            return False

    def _log_buttons(self, context: str) -> None:
        try:
            cands = self.driver.execute_script("""
                function collect(doc, out){
                    var els=doc.querySelectorAll('button, a, [role="button"]');
                    for(var i=0;i<els.length;i++){var t=(els[i].textContent||'').trim();var a=(els[i].getAttribute('aria-label')||'');
                        if(t&&t.length<=14)out.push(t); else if(a&&a.length<=14)out.push('aria:'+a);}
                    var ifr=doc.querySelectorAll('iframe');
                    for(var j=0;j<ifr.length;j++){try{var d=ifr[j].contentDocument||ifr[j].contentWindow.document;if(d)collect(d,out);}catch(e){}}
                }
                var out=[];collect(document,out);return out;
            """)
            logger.warning(f"[{context}] 버튼/링크 후보: {cands}")
        except Exception as e:
            logger.debug(f"버튼 로깅 실패: {e}")

    def switch_back_to_main(self) -> None:
        self.driver.switch_to.default_content()
