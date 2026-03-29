"""브라우저 실행, 자동 로그인, 에디터 페이지 이동."""

import os
import sys
from playwright.sync_api import sync_playwright
from config import LOAD_DELAY, ACTION_DELAY

# 에디터 컨테이너 셀렉터 (selectors.py 제거 후 직접 정의)
EDITOR_CONTAINER = ".se-documentTitle"

_playwright = None


def _get_exe_dir():
    """exe 실행 파일이 위치한 디렉토리를 반환한다."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(".")


def _set_playwright_browsers_path():
    """exe 모드에서 PLAYWRIGHT_BROWSERS_PATH를 시스템 설치 경로로 설정한다."""
    if getattr(sys, 'frozen', False):
        localappdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.join(localappdata, 'ms-playwright')


def launch_browser():
    """Playwright Chromium을 persistent context로 실행한다."""
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


def auto_login(page, login_id, login_pw):
    """
    네이버 로그인 페이지에서 ID/PW를 자동 입력하여 로그인한다.
    로그인 성공 시 True, 추가 인증이 필요한 경우 False를 반환한다.
    """
    print("\n🔑 네이버 자동 로그인을 시도합니다...")

    login_url = "https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com%2F"
    page.goto(login_url, wait_until="domcontentloaded")
    page.wait_for_timeout(1000)

    # ID 입력 (사람처럼 타이핑)
    page.click("#id")
    page.wait_for_timeout(300)
    page.keyboard.type(login_id, delay=60)
    page.wait_for_timeout(300)

    # PW 입력
    page.click("#pw")
    page.wait_for_timeout(300)
    page.keyboard.type(login_pw, delay=60)
    page.wait_for_timeout(500)

    # 로그인 버튼 클릭
    page.click(".btn_login")
    page.wait_for_timeout(2000)

    current_url = page.url

    # 추가 인증 페이지 감지 (CAPTCHA, 2차 인증 등)
    if any(k in current_url for k in ("nidlogin", "nid.naver.com/user2", "captcha")):
        print("\n⚠️  추가 인증이 필요합니다. 브라우저에서 직접 인증을 완료한 후 Enter를 누르세요...")
        input()

        current_url = page.url
        if "nidlogin" in current_url:
            raise Exception("로그인에 실패했습니다. 브라우저 상태를 확인하세요.")

    print("   ✅ 로그인 완료")
    page.wait_for_timeout(ACTION_DELAY)


def navigate_to_editor(page, blog_id):
    """블로그 글쓰기 페이지로 이동하고 에디터 로딩을 대기한다."""
    url = f"https://blog.naver.com/{blog_id}/postwrite"

    try:
        page.goto(url, wait_until="domcontentloaded")
    except Exception:
        pass

    # 로그인 페이지로 빠진 경우
    if "nidlogin" in page.url:
        print("\n⚠️  로그인 세션이 만료되었습니다. 브라우저에서 로그인 후 Enter를 누르세요...")
        input()
        try:
            page.goto(url, wait_until="domcontentloaded")
        except Exception:
            pass

    if "nidlogin" in page.url:
        raise Exception(
            f"로그인에 실패했습니다. 현재 URL: {page.url}\n"
            "브라우저에서 직접 네이버에 로그인한 뒤 프로그램을 다시 실행하세요."
        )

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
