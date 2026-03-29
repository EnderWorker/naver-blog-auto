"""네이버 스마트에디터 ONE DOM 셀렉터 정의 + fallback 유틸."""


# ── 셀렉터 후보 리스트 (앞에서부터 순서대로 시도) ──

TITLE_INPUT_CANDIDATES = (
    ".se-documentTitle .se-text-paragraph",
    ".se-title-text .se-text-paragraph",
    "[class*='documentTitle'] [contenteditable='true']",
)

BODY_AREA_CANDIDATES = (
    ".se-component-content .se-text-paragraph",
    ".se-main-container .se-text-paragraph",
    "[class*='component'] [contenteditable='true']",
)

TOOLBAR_QUOTE_CANDIDATES = (
    'button[data-name="quotation"]',
    'button[data-type="quotation"]',
    '.se-toolbar-item-quotation button',
    'button[class*="quotation"]',
)

TOOLBAR_DIVIDER_CANDIDATES = (
    'button[data-name="horizontalLine"]',
    'button[data-type="horizontalLine"]',
    '.se-toolbar-item-horizontalLine button',
    'button[class*="horizontalLine"]',
)

TOOLBAR_BOLD_CANDIDATES = (
    'button[data-name="bold"]',
    'button[data-type="bold"]',
    '.se-toolbar-item-bold button',
)

TOOLBAR_FONT_SIZE_CANDIDATES = (
    "button.se-text-size-button",
    ".se-toolbar-item-font-size button",
    'button[class*="text-size"]',
    'button[class*="fontSize"]',
)

QUOTE_STYLE_PREFIX = ".se-quotation-style-"

DIVIDER_STYLE_DOT_CANDIDATES = (
    'button[data-style="dot"]',
    '.se-horizontal-line-style-dot',
    '.se-horizontal-line-item:nth-child(2)',
)

FONT_SIZE_ITEM_TEMPLATE = '.se-font-size-item[data-size="{}"]'

EDITOR_CONTAINER_CANDIDATES = (
    ".se-documentTitle",
    "[class*='documentTitle']",
    ".se-editor",
)

LAST_PARAGRAPH_CANDIDATES = (
    ".se-component:last-child .se-text-paragraph",
    ".se-main-container .se-text-paragraph:last-of-type",
)


# ── 하위 호환용 단일 셀렉터 (기존 코드 참조 유지) ──

TITLE_INPUT = TITLE_INPUT_CANDIDATES[0]
BODY_AREA = BODY_AREA_CANDIDATES[0]
TOOLBAR_QUOTE = TOOLBAR_QUOTE_CANDIDATES[0]
TOOLBAR_DIVIDER = TOOLBAR_DIVIDER_CANDIDATES[0]
TOOLBAR_BOLD = TOOLBAR_BOLD_CANDIDATES[0]
TOOLBAR_FONT_SIZE = TOOLBAR_FONT_SIZE_CANDIDATES[0]
DIVIDER_STYLE_DOT = DIVIDER_STYLE_DOT_CANDIDATES[0]
FONT_SIZE_ITEM = FONT_SIZE_ITEM_TEMPLATE
EDITOR_CONTAINER = EDITOR_CONTAINER_CANDIDATES[0]
LAST_PARAGRAPH = LAST_PARAGRAPH_CANDIDATES[0]


# ── fallback 유틸 함수 ──

def find_element(page, candidates, timeout=5000):
    """
    셀렉터 후보 리스트를 순서대로 시도하여 첫 번째 매칭 요소를 반환한다.
    모든 후보가 실패하면 예외를 발생시킨다.

    Args:
        page: Playwright Page 객체
        candidates: 셀렉터 문자열 tuple
        timeout: 각 후보별 탐색 대기 시간 (ms)
    Returns:
        Locator 객체
    """
    if isinstance(candidates, str):
        candidates = (candidates,)

    for sel in candidates:
        try:
            loc = page.locator(sel)
            loc.first.wait_for(timeout=timeout)
            if loc.count() > 0:
                return loc.first
        except Exception:
            continue

    raise Exception(
        f"요소를 찾을 수 없습니다. 시도한 셀렉터: {candidates}"
    )
