"""네이버 스마트에디터 ONE DOM에 HTML을 직접 주입한다."""

from config import ACTION_DELAY, LOAD_DELAY


def inject_title(page, title_text):
    """
    에디터 제목 필드에 텍스트를 입력한다.
    제목은 contenteditable이므로 keyboard.type으로 입력한다.
    """
    title_selector = ".se-documentTitle .se-text-paragraph"
    page.wait_for_selector(title_selector, timeout=10000)
    page.click(title_selector)
    page.wait_for_timeout(ACTION_DELAY)

    # 기존 내용 지우기
    page.keyboard.press("Control+a")
    page.keyboard.press("Delete")
    page.wait_for_timeout(100)

    # 제목 입력
    page.keyboard.type(title_text, delay=20)
    page.wait_for_timeout(ACTION_DELAY)


def inject_body_html(page, body_html):
    """
    에디터 본문 영역에 HTML을 직접 주입한다.
    기존 본문 컴포넌트를 모두 제거하고 새 HTML로 교체한다.

    Args:
        page: Playwright Page 객체
        body_html: blocks_to_editor_html()이 생성한 HTML 문자열
    """
    # JS 안에서 템플릿 리터럴을 깨는 특수문자 이스케이프
    escaped_html = (
        body_html
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )

    js_code = f"""
    (() => {{
        const container = document.querySelector('.se-components-container')
                       || document.querySelector('[class*="components-container"]')
                       || document.querySelector('.se-content');
        if (!container) {{
            throw new Error('에디터 본문 컨테이너를 찾을 수 없습니다.');
        }}

        // 기존 본문 컴포넌트 모두 제거 (제목 컴포넌트 제외)
        const existing = container.querySelectorAll(':scope > .se-component:not(.se-documentTitle)');
        existing.forEach(c => c.remove());

        // 새 HTML 주입
        container.insertAdjacentHTML('beforeend', `{escaped_html}`);

        return 'injected';
    }})();
    """

    result = page.evaluate(js_code)
    page.wait_for_timeout(LOAD_DELAY)
    return result


def verify_injection(page):
    """
    주입이 정상적으로 완료되었는지 검증한다.
    삽입된 컴포넌트 수와 타입별 카운트를 반환한다.
    """
    js_code = """
    (() => {
        const container = document.querySelector('.se-components-container')
                       || document.querySelector('[class*="components-container"]')
                       || document.querySelector('.se-content');
        if (!container) return { error: 'container not found' };

        const components = container.querySelectorAll('.se-component');
        const types = {};
        components.forEach(c => {
            const cls = Array.from(c.classList);
            let type = 'unknown';
            if (cls.includes('se-text'))           type = 'text';
            else if (cls.includes('se-quotation')) type = 'quotation';
            else if (cls.includes('se-horizontalLine')) type = 'horizontalLine';
            else if (cls.includes('se-image'))     type = 'image';
            types[type] = (types[type] || 0) + 1;
        });

        return { total: components.length, types: types };
    })();
    """
    return page.evaluate(js_code)
