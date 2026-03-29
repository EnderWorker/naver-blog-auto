"""스마트에디터 ONE 직접 조작 — 제목/본문/인용구/구분선/서식 입력."""

from config import ACTION_DELAY, BODY_SIZE, HEADING_SIZE, SUBHEADING_SIZE
from editor.selectors import (
    TITLE_INPUT,
    BODY_AREA,
    TOOLBAR_QUOTE,
    TOOLBAR_DIVIDER,
    TOOLBAR_BOLD,
    TOOLBAR_FONT_SIZE,
    QUOTE_STYLE_PREFIX,
    DIVIDER_STYLE_DOT,
    FONT_SIZE_ITEM,
    LAST_PARAGRAPH,
)


def _delay(page, ms=None):
    page.wait_for_timeout(ms or ACTION_DELAY)


# ── 제목 ──────────────────────────────────────────────

def set_title(page, title_text):
    """제목 영역에 텍스트를 입력하고 본문으로 포커스를 이동한다."""
    title_el = page.locator(TITLE_INPUT).first
    title_el.click()
    _delay(page)
    page.keyboard.type(title_text, delay=20)
    _delay(page)
    # 본문으로 이동
    page.keyboard.press("Tab")
    _delay(page)


# ── 본문 포커스 ───────────────────────────────────────

def click_body_area(page):
    """본문 편집 영역 끝에 포커스를 잡는다."""
    # 마지막 paragraph를 클릭 시도, 실패 시 일반 body area 사용
    last = page.locator(LAST_PARAGRAPH)
    if last.count() > 0:
        last.last.click()
    else:
        body = page.locator(BODY_AREA)
        if body.count() > 0:
            body.last.click()
    _delay(page, 100)
    # 문서 끝으로 이동
    page.keyboard.press("Control+End")
    _delay(page, 100)


# ── 텍스트 입력 (서식 포함) ───────────────────────────

def _build_segments(text, formatting):
    """
    전체 텍스트를 formatting 기준으로 세그먼트 리스트로 분할한다.
    각 세그먼트: {"text": str, "bold": bool, "color": str|None, "size": int|None}
    """
    if not formatting:
        return [{"text": text, "bold": False, "color": None, "size": None}]

    # bold 서식만 추출 (가장 흔함)
    bold_texts = [f["text"] for f in formatting if f.get("type") == "bold"]
    color_map = {f["text"]: f["color"] for f in formatting if f.get("type") == "color"}
    size_map = {f["text"]: f["size"] for f in formatting if f.get("type") == "size"}

    all_special = {}
    for f in formatting:
        ft = f.get("text", "")
        if ft and ft not in all_special:
            all_special[ft] = f

    if not all_special:
        return [{"text": text, "bold": False, "color": None, "size": None}]

    segments = []
    remaining = text

    while remaining:
        # 가장 먼저 등장하는 서식 텍스트 찾기
        earliest_pos = len(remaining)
        earliest_key = None

        for key in all_special:
            pos = remaining.find(key)
            if pos != -1 and pos < earliest_pos:
                earliest_pos = pos
                earliest_key = key

        if earliest_key is None:
            # 남은 텍스트는 일반
            segments.append({"text": remaining, "bold": False, "color": None, "size": None})
            break

        # 서식 텍스트 앞의 일반 텍스트
        if earliest_pos > 0:
            segments.append({
                "text": remaining[:earliest_pos],
                "bold": False,
                "color": None,
                "size": None,
            })

        # 서식 텍스트
        segments.append({
            "text": earliest_key,
            "bold": earliest_key in bold_texts,
            "color": color_map.get(earliest_key),
            "size": size_map.get(earliest_key),
        })

        remaining = remaining[earliest_pos + len(earliest_key):]

    return segments


def insert_text(page, text, formatting=None):
    """
    본문에 텍스트를 입력한다.
    formatting이 있으면 세그먼트 단위로 서식을 적용한다.
    """
    click_body_area(page)

    segments = _build_segments(text, formatting)

    for seg in segments:
        seg_text = seg["text"]
        if not seg_text:
            continue

        # bold ON
        if seg["bold"]:
            page.keyboard.press("Control+b")
            _delay(page, 100)

        page.keyboard.type(seg_text, delay=10)

        # bold OFF
        if seg["bold"]:
            page.keyboard.press("Control+b")
            _delay(page, 100)

    page.keyboard.press("Enter")
    _delay(page)


# ── 인용구 삽입 ──────────────────────────────────────

def insert_quote(page, text, style=4, formatting=None):
    """
    인용구 블록을 삽입하고 내부에 텍스트를 입력한다.

    Args:
        page: Playwright Page
        text: 인용구 내부 텍스트
        style: 인용구 스타일 번호 (기본 4)
        formatting: 서식 정보 리스트
    """
    click_body_area(page)

    # 인용구 버튼 클릭
    quote_btn = page.locator(TOOLBAR_QUOTE)
    quote_btn.click()
    _delay(page, 500)

    # 스타일 선택
    style_selector = f"{QUOTE_STYLE_PREFIX}{style}"
    style_btn = page.locator(style_selector)
    if style_btn.count() > 0:
        style_btn.click()
        _delay(page, 500)

    # 인용구 내부에 텍스트 입력
    lines = text.split("\n")
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            page.keyboard.press("Enter")
            continue
        page.keyboard.type(line, delay=10)
        if idx < len(lines) - 1:
            page.keyboard.press("Enter")
        _delay(page, 50)

    # 인용구 밖으로 나가기
    page.keyboard.press("ArrowDown")
    _delay(page)
    page.keyboard.press("Enter")
    _delay(page)


# ── 구분선 삽입 ──────────────────────────────────────

def insert_divider(page, style="dot"):
    """구분선을 삽입한다."""
    click_body_area(page)

    divider_btn = page.locator(TOOLBAR_DIVIDER)
    divider_btn.click()
    _delay(page, 500)

    # 점선 스타일 선택
    if style == "dot":
        dot_btn = page.locator(DIVIDER_STYLE_DOT)
        if dot_btn.count() > 0:
            dot_btn.click()
            _delay(page, 500)
        else:
            # 팝업 내 두 번째 스타일 선택 시도 (점선이 대체로 2번째)
            items = page.locator(".se-horizontal-line-item")
            if items.count() >= 2:
                items.nth(1).click()
                _delay(page, 500)

    # 구분선 아래로 이동
    page.keyboard.press("ArrowDown")
    _delay(page)


# ── 제목/소제목 삽입 ─────────────────────────────────

def insert_heading(page, text, level="h3"):
    """
    제목(h3) 또는 소제목(h4)을 입력한다.
    크기를 변경하고 볼드를 적용한 뒤 본문 크기로 복원한다.
    """
    click_body_area(page)

    target_size = HEADING_SIZE if level == "h3" else SUBHEADING_SIZE

    page.keyboard.type(text, delay=10)
    _delay(page, 100)

    # 입력한 텍스트 전체 선택
    page.keyboard.press("Home")
    _delay(page, 50)
    page.keyboard.press("Shift+End")
    _delay(page, 100)

    # 글자 크기 변경
    apply_font_size(page, target_size)

    # 볼드 적용
    page.keyboard.press("Control+b")
    _delay(page, 100)

    # 줄 끝으로 이동 후 다음 줄
    page.keyboard.press("End")
    _delay(page, 50)
    page.keyboard.press("Enter")
    _delay(page, 100)

    # 본문 기본 크기로 복원
    apply_font_size(page, BODY_SIZE)
    _delay(page, 100)

    # 볼드 해제
    page.keyboard.press("Control+b")
    _delay(page)


# ── 빈 줄 삽입 ───────────────────────────────────────

def insert_spacing(page):
    """빈 줄 하나를 삽입한다."""
    click_body_area(page)
    page.keyboard.press("Enter")
    _delay(page)


# ── 글자 크기 변경 ───────────────────────────────────

def apply_font_size(page, size):
    """
    현재 선택된 텍스트의 글자 크기를 변경한다.

    Args:
        size: 글자 크기 (px). 가능한 값: 11,13,15,16,18,20,24,28,30,34,40
    """
    # 글자크기 드롭다운 버튼 클릭
    size_btn = page.locator(TOOLBAR_FONT_SIZE)
    if size_btn.count() == 0:
        # 대체 셀렉터 시도
        size_btn = page.locator('.se-toolbar button:has-text("글자크기")')
    if size_btn.count() > 0:
        size_btn.first.click()
        _delay(page, 300)

        # 해당 크기 항목 선택
        size_item = page.locator(FONT_SIZE_ITEM.format(size))
        if size_item.count() > 0:
            size_item.click()
        else:
            # data-size가 없으면 텍스트로 찾기
            page.locator(f'text="{size}"').first.click()
        _delay(page, 200)
