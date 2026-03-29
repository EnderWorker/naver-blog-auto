"""브라우저 실행, 로그인 대기, 에디터 페이지 이동."""

import os
from playwright.sync_api import sync_playwright
from config import LOAD_DELAY
from editor.selectors import EDITOR_CONTAINER


_playwright = None
_browser = None


def launch_browser():
    """
    Playwright Chromium을 persistent context로 실행한다.
    로그인 세션을 유지하기 위해 user_data_dir을 사용한다.

    Returns:
        tuple: (browser_context, page)
    """
    global _playwright, _browser

    user_data_dir = os.path.join(os.path.abspath("."), "browser_data")
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


def wait_for_login(page):
    """네이버 로그인을 사용자에게 안내하고 Enter 입력을 대기한다."""
    print("\n🔑 네이버에 로그인한 후 Enter를 누르세요...")
    input()


def navigate_to_editor(page, blog_id):
    """
    블로그 글쓰기 페이지로 이동하고 에디터 로딩을 대기한다.

    Args:
        page: Playwright Page 객체
        blog_id: 네이버 블로그 ID
    """
    url = f"https://blog.naver.com/{blog_id}/postwrite"
    page.goto(url, wait_until="domcontentloaded")

    # 에디터 제목 영역이 나타날 때까지 대기 (최대 30초)
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
