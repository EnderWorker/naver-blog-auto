"""브라우저 실행, 로그인 대기, 에디터 페이지 이동."""

import os
import sys
from playwright.sync_api import sync_playwright
from config import LOAD_DELAY
from editor.selectors import EDITOR_CONTAINER


_playwright = None


def _get_exe_dir():
    """exe 실행 파일이 위치한 디렉토리를 반환한다."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(".")


def _set_playwright_browsers_path():
    """
    exe 모드에서 Playwright가 시스템에 설치된 Chromium을 찾도록
    PLAYWRIGHT_BROWSERS_PATH 환경변수를 설정한다.
    """
    if getattr(sys, 'frozen', False):
        localappdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        browsers_path = os.path.join(localappdata, 'ms-playwright')
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_path


def launch_browser():
    """
    Playwright Chromium을 persistent context로 실행한다.
    로그인 세션을 유지하기 위해 user_data_dir을 사용한다.
    """
    global _playwright

    _set_playwright_browsers_path()
    user_data_dir = os.path.join(_get_exe_dir(), "browser_data")
    os.makedirs(user_data_dir, exist_ok=True)

    _playwright = sync_playwright().start()

    context = _playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,
        viewport={"width": 1280, "height": 900},
        locale="ko-KR",
        args=["--disable-blink-features=AutomationControlled"],
    )

    page = context.pages[0] if context.pages else context.new_page()
    return context, page


def wait_for_login(_page):
    """네이버 로그인을 사용자에게 안내하고 Enter 입력을 대기한다."""
    print("\n🔑 네이버에 로그인한 후 Enter를 누르세요...")
    input()


def navigate_to_editor(page, blog_id):
    """블로그 글쓰기 페이지로 이동하고 에디터 로딩을 대기한다."""
    url = f"https://blog.naver.com/{blog_id}/postwrite"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_selector(EDITOR_CONTAINER, timeout=30000)
    page.wait_for_timeout(LOAD_DELAY)


def close_browser(context):
    """브라우저 컨텍스트와 Playwright를 정리한다."""
    global _playwright
    try:
        context.close()
    except Exception:
        pass
    if _playwright:
        try:
            _playwright.stop()
        except Exception:
            pass
