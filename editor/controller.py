"""스마트에디터 ONE 직접 조작 — 제목/본문/인용구/구분선/서식 입력."""

import re
from config import ACTION_DELAY, BODY_SIZE, HEADING_SIZE, SUBHEADING_SIZE
from editor.selectors import (
    find_element,
    dump_toolbar_buttons,
    TITLE_INPUT_CANDIDATES,
    BODY_AREA_CANDIDATES,
    TOOLBAR_QUOTE_CANDIDATES,
    TOOLBAR_DIVIDER_CANDIDATES,
    TOOLBAR_FONT_SIZE_CANDIDATES,
    QUOTE_STYLE_PREFIX,
    DIVIDER_STYLE_DOT_CANDIDATES,
    FONT_SIZE_ITEM_TEMPLATE,
    LAST_PARAGRAPH_CANDIDATES,
)


def _delay(page, ms=None):
    page.wait_for_timeout(ms or ACTION_DELAY)


def _normalize(s):
    """공백/줄바꿈을 정규화하여 비교 가능한 문자열로 변환한다."""
    return re.sub(r'\s+', ' ', s).strip()


# ── 제목 ──────────────────────────────────────────────

def set_title(page, title_text):
    """제목 영역에 텍스트를 입력하고 본문으로 포커스를 이동한다."""
    title_el = find_element(page, TITLE_INPUT_CANDIDATES)
    title_el.click()
    _delay(page)
    page.keyboard.type(title_text, delay=20)
    _delay(page)
    page.keyboard.press("Tab")
    _delay(page)


# ── 본문 포커스 ───────────────────────────────────────

def click_body_area(page):
    """본문 편집 영역 끝에 포커스를 잡는다."""
    try:
        last = find_element(page, LAST_PARAGRAPH_CANDIDATES, timeout=2000)
        last.click()
    except Exception:
        try:
            body = find_element(page, BODY_AREA_CANDIDATES, timeout=2000)
            body.click()
        except Exception:
            pass
    _delay(page, 100)
    page.keyboard.press("Control+End")
    _delay(page, 100)


# ── 서식 세그먼트 빌더 ────────────────────────────────

def _merge_formatting(formatting):
    """
    동일 텍스트에 대한 서식 정보를 병합한다.
    예: bold "텍스트" + size "텍스트" → {"text": "텍스트", bold: True, size: 24}
    """
    if not formatting:
        return {}
    merged = {}
    for f in formatting:
        ft = f.get("text", "")
        if not ft:
            continue
        if ft not in merged:
            merged[ft] = {"text": ft, "bold": False, "color": None, "size": None}
        if f["type"] == "bold":
            merged[ft]["bold"] = True
        elif f["type"] == "color":
            merged[ft]["color"] = f["color"]
        elif f["type"] == "size":
            merged[ft]["size"] = f["size"]
    return merged


def _build_segments(text, formatting):
    """
    전체 텍스트를 formatting 기준으로 세그먼트 리스트로 분할한다.
    텍스트 매칭은 정규화 후 수행하여 공백/줄바꿈 차이를 흡수한다.
    """
    if not formatting:
        return [{"text": text, "bold": False, "color": None, "size": None}]

    merged = _merge_formatting(formatting)
    if not merged:
        return [{"text": text, "bold": False, "color": None, "size": None}]

    segments = []
    remaining = text

    while remaining:
        earliest_pos = len(remaining)
        earliest_key = None

        for key in merged:
            # 원본 텍스트에서 위치 탐색
            orig_pos = remaining.find(key)
            if orig_pos == -1:
                # 정규화된 텍스트에서 근사 탐색
                norm_key = _normalize(key)
                norm_pos = _normalize(remaining).find(norm_key)
                if norm_pos == -1:
                    continue
                orig_pos = norm_pos  # 근사치

            if orig_pos < earliest_pos:
                earliest_pos = orig_pos
                earliest_key = key

        if earliest_key is None:
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
        attrs = merged[earliest_key]
        segments.append({
            "text": earliest_key,
            "bold": attrs["bold"],
            "color": attrs["color"],
            "size": attrs["size"],
        })

        remaining = remaining[earliest_pos + len(earliest_key):]

    return segments


# ── 세그먼트 단위 텍스트 타이핑 ───────────────────────

def _type_segments(page, segments):
    """세그먼트 리스트를 순서대로 타이핑하며 서식을 적용한다."""
    for seg in segments:
        seg_text = seg["text"]
        if not seg_text:
            continue

        # bold ON
        if seg["bold"]:
            page.keyboard.press("Control+b")
            _delay(page, 100)

        # 줄바꿈 처리: \n을 Enter로 분리
        lines = seg_text.split("\n")
        for j, line in enumerate(lines):
            if line:
                page.keyboard.type(line, delay=10)
            if j < len(lines) - 1:
                page.keyboard.press("Enter")

        # bold OFF
        if seg["bold"]:
            page.keyboard.press("Control+b")
            _delay(page, 100)


# ── 텍스트 입력 (서식 포함) ───────────────────────────

def insert_text(page, text, formatting=None):
    """
    본문에 텍스트를 입력한다.
    formatting이 있으면 세그먼트 단위로 서식을 적용한다.
    """
    click_body_area(page)
    segments = _build_segments(text, formatting)
    _type_segments(page, segments)
    page.keyboard.press("Enter")
    _delay(page)


# ── 인용구 삽입 ──────────────────────────────────────

def insert_quote(page, text, style=4, formatting=None):
    """
    인용구 블록을 삽입하고 내부에 텍스트를 입력한다.
    formatting이 있으면 인용구 내부에서도 서식을 적용한다.
    """
    click_body_area(page)

    # 인용구 버튼 클릭
    quote_btn = find_element(page, TOOLBAR_QUOTE_CANDIDATES)
    quote_btn.click()
    _delay(page, 500)

    # 스타일 선택
    style_selector = f"{QUOTE_STYLE_PREFIX}{style}"
    try:
        style_btn = page.locator(style_selector)
        if style_btn.count() > 0:
            style_btn.click()
            _delay(page, 500)
    except Exception:
        pass  # 스타일 선택 실패 시 기본 스타일로 진행

    # 인용구 내부에 텍스트 입력 (서식 포함)
    lines = text.split("\n")
    for idx, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped:
            page.keyboard.press("Enter")
            _delay(page, 50)
            continue

        # 이 라인에 해당하는 formatting만 필터
        line_fmt = [f for f in (formatting or []) if f.get("text", "") in line_stripped]
        segments = _build_segments(line_stripped, line_fmt)
        _type_segments(page, segments)

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

    try:
        divider_btn = find_element(page, TOOLBAR_DIVIDER_CANDIDATES)
    except Exception:
        dump_toolbar_buttons(page)
        raise
    divider_btn.click()
    _delay(page, 500)

    # 점선 스타일 선택
    if style == "dot":
        try:
            dot_btn = find_element(page, DIVIDER_STYLE_DOT_CANDIDATES, timeout=3000)
            dot_btn.click()
            _delay(page, 500)
        except Exception:
            # fallback: 팝업 내 두 번째 항목 시도
            try:
                items = page.locator(".se-horizontal-line-item")
                if items.count() >= 2:
                    items.nth(1).click()
                    _delay(page, 500)
            except Exception:
                pass  # 스타일 선택 실패 시 기본 구분선으로 진행

    page.keyboard.press("ArrowDown")
    _delay(page)


# ── 제목/소제목 삽입 ─────────────────────────────────

def insert_heading(page, text, level="h3"):
    """
    제목(h3) 또는 소제목(h4)을 입력한다.
    크기를 변경하고 볼드를 적용한 뒤, 다음 줄에서 본문 크기로 안전하게 복원한다.
    """
    click_body_area(page)

    target_size = HEADING_SIZE if level == "h3" else SUBHEADING_SIZE

    # 텍스트 입력
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
    _delay(page, 200)

    # 새 줄에서 서식 복원 (임시 텍스트 기법)
    # 빈 줄에서는 글자크기 변경이 동작하지 않을 수 있으므로
    # 임시 공백을 입력한 후 선택 → 크기 복원 → 볼드 해제 → 삭제
    page.keyboard.type(" ")
    page.keyboard.press("Shift+Home")
    _delay(page, 50)
    apply_font_size(page, BODY_SIZE)
    page.keyboard.press("Control+b")  # 볼드 해제
    _delay(page, 50)
    # 임시 공백 삭제
    page.keyboard.press("End")
    page.keyboard.press("Backspace")
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
    가능한 값: 11, 13, 15, 16, 18, 20, 24, 28, 30, 34, 40
    """
    try:
        size_btn = find_element(page, TOOLBAR_FONT_SIZE_CANDIDATES, timeout=3000)
        size_btn.click()
        _delay(page, 300)

        # 해당 크기 항목 선택
        size_item_sel = FONT_SIZE_ITEM_TEMPLATE.format(size)
        size_item = page.locator(size_item_sel)
        if size_item.count() > 0:
            size_item.click()
        else:
            # data-size가 없으면 텍스트로 찾기
            page.locator(f'text="{size}"').first.click()
        _delay(page, 200)
    except Exception as e:
        if "요소를 찾을 수 없습니다" in str(e):
            dump_toolbar_buttons(page)
        print(f"  ⚠️  글자 크기 변경 실패 ({size}px): {e}")
