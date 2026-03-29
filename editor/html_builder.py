"""파싱된 블록을 네이버 스마트에디터 ONE 내부 HTML로 변환한다."""

from config import (
    BODY_FONT, BODY_SIZE, BODY_ALIGN, BODY_LINE_HEIGHT, BODY_COLOR,
    HEADING_FONT, HEADING_SIZE, HEADING_ALIGN, HEADING_LINE_HEIGHT,
    HEADING_COLOR, HEADING_BOLD,
    TITLE_HEADING_FONT, TITLE_HEADING_SIZE, TITLE_HEADING_ALIGN,
    TITLE_HEADING_LINE_HEIGHT, TITLE_HEADING_COLOR, TITLE_HEADING_BOLD,
    QUOTE_STYLE_CLASS, QUOTE_FONT, QUOTE_SIZE, QUOTE_LINE_HEIGHT, QUOTE_COLOR,
    CITE_FONT, CITE_SIZE, CITE_COLOR,
    DIVIDER_STYLE_CLASS,
)


def _build_span(text, font_class, size_class, color, bold=False):
    """텍스트 span 요소를 생성한다. bold이면 <b>로 감싼다."""
    inner = text
    if bold:
        inner = f"<b>{text}</b>"
    return (
        f'<span class="{font_class} {size_class} __se-node" '
        f'style="color: {color};">{inner}</span>'
    )


def _build_paragraph(spans_html, align_class, line_height):
    """하나의 <p> 문단을 생성한다."""
    return (
        f'<p class="se-text-paragraph {align_class}" '
        f'style="line-height: {line_height};">'
        f'{spans_html}'
        f'</p>'
    )


def _build_text_segments(text, formatting, font_class, size_class, color):
    """
    텍스트와 formatting 정보를 기반으로 span HTML 조각들을 생성한다.
    formatting에 bold/color/size가 있으면 해당 부분만 다른 스타일을 적용한다.
    """
    if not formatting:
        return _build_span(text, font_class, size_class, color)

    # formatting을 text 기준으로 병합
    fmt_map = {}
    for f in formatting:
        ft = f.get("text", "")
        if not ft:
            continue
        if ft not in fmt_map:
            fmt_map[ft] = {"bold": False, "color": None, "size": None}
        if f["type"] == "bold":
            fmt_map[ft]["bold"] = True
        elif f["type"] == "color":
            fmt_map[ft]["color"] = f["color"]
        elif f["type"] == "size":
            fmt_map[ft]["size"] = f["size"]

    if not fmt_map:
        return _build_span(text, font_class, size_class, color)

    # 텍스트를 세그먼트로 분할
    result = ""
    remaining = text

    while remaining:
        earliest_pos = len(remaining)
        earliest_key = None

        for key in fmt_map:
            pos = remaining.find(key)
            if pos != -1 and pos < earliest_pos:
                earliest_pos = pos
                earliest_key = key

        if earliest_key is None:
            result += _build_span(remaining, font_class, size_class, color)
            break

        # 서식 텍스트 앞의 일반 텍스트
        if earliest_pos > 0:
            result += _build_span(
                remaining[:earliest_pos], font_class, size_class, color
            )

        # 서식이 적용된 텍스트
        attrs = fmt_map[earliest_key]
        seg_bold = attrs["bold"]
        seg_color = attrs["color"] or color
        seg_size = size_class
        if attrs["size"]:
            seg_size = f"se-fs{attrs['size']}"

        result += _build_span(
            earliest_key, font_class, seg_size, seg_color, bold=seg_bold
        )

        remaining = remaining[earliest_pos + len(earliest_key):]

    return result


# ── 공개 빌더 함수들 ──────────────────────────────────


def build_text_component(text, formatting=None, align=None, line_height=None):
    """
    일반 본문 텍스트 컴포넌트 HTML을 생성한다.
    여러 줄(\\n)은 각각 별도의 <p>로 생성한다.
    """
    _align = align or BODY_ALIGN
    _lh = line_height or BODY_LINE_HEIGHT

    lines = text.split("\n")
    paragraphs = ""

    for line in lines:
        line = line.strip()
        if not line:
            paragraphs += (
                f'<p class="se-text-paragraph {_align}" '
                f'style="line-height: {_lh};">'
                f'<span class="{BODY_FONT} {BODY_SIZE} __se-node" '
                f'style="color: {BODY_COLOR};">\u200b</span>'
                f'</p>'
            )
        else:
            spans = _build_text_segments(
                line, formatting, BODY_FONT, BODY_SIZE, BODY_COLOR
            )
            paragraphs += _build_paragraph(spans, _align, _lh)

    return (
        f'<div class="se-component se-text">'
        f'<div class="se-component-content">'
        f'<div class="se-section se-section-text">'
        f'<div class="se-module se-module-text">'
        f'{paragraphs}'
        f'</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )


def build_heading_component(text, level="h3"):
    """
    대제목(h3) 또는 소제목(h4) 컴포넌트 HTML을 생성한다.
    구조는 일반 텍스트와 동일하지만 크기/볼드가 다르다.
    """
    if level == "h3":
        font = TITLE_HEADING_FONT
        size = TITLE_HEADING_SIZE
        align = TITLE_HEADING_ALIGN
        lh = TITLE_HEADING_LINE_HEIGHT
        color = TITLE_HEADING_COLOR
        bold = TITLE_HEADING_BOLD
    else:
        font = HEADING_FONT
        size = HEADING_SIZE
        align = HEADING_ALIGN
        lh = HEADING_LINE_HEIGHT
        color = HEADING_COLOR
        bold = HEADING_BOLD

    span = _build_span(text, font, size, color, bold=bold)
    paragraph = _build_paragraph(span, align, lh)

    return (
        f'<div class="se-component se-text">'
        f'<div class="se-component-content">'
        f'<div class="se-section se-section-text">'
        f'<div class="se-module se-module-text">'
        f'{paragraph}'
        f'</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )


def build_spacing_component():
    """빈 줄(spacing) 컴포넌트 HTML을 생성한다."""
    return (
        f'<div class="se-component se-text">'
        f'<div class="se-component-content">'
        f'<div class="se-section se-section-text">'
        f'<div class="se-module se-module-text">'
        f'<p class="se-text-paragraph {BODY_ALIGN}" '
        f'style="line-height: {BODY_LINE_HEIGHT};">'
        f'<span class="{BODY_FONT} {BODY_SIZE} __se-node" '
        f'style="color: {BODY_COLOR};">\u200b</span>'
        f'</p>'
        f'</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )


def build_quote_component(text, formatting=None, cite=""):
    """
    인용구 컴포넌트 HTML을 생성한다 (밑줄 스타일).
    여러 줄(\\n)은 각각 별도의 <p>로 생성한다.
    """
    lines = text.split("\n")
    quote_paragraphs = ""

    for line in lines:
        line = line.strip()
        if not line:
            quote_paragraphs += (
                f'<p class="se-text-paragraph se-text-paragraph-align-left" '
                f'style="line-height: {QUOTE_LINE_HEIGHT};">'
                f'<span class="{QUOTE_FONT} {QUOTE_SIZE} __se-node" '
                f'style="color: {QUOTE_COLOR};">\u200b</span>'
                f'</p>'
            )
        else:
            spans = _build_text_segments(
                line, formatting, QUOTE_FONT, QUOTE_SIZE, QUOTE_COLOR
            )
            quote_paragraphs += _build_paragraph(
                spans, "se-text-paragraph-align-left", QUOTE_LINE_HEIGHT
            )

    cite_content = cite if cite else "\u200b"
    cite_html = (
        f'<div class="se-module se-module-text se-cite">'
        f'<p class="se-text-paragraph se-text-paragraph-align-left" '
        f'style="line-height: 1.5;">'
        f'<span class="{CITE_FONT} {CITE_SIZE} __se-node" '
        f'style="color: {CITE_COLOR};">{cite_content}</span>'
        f'</p>'
        f'</div>'
    )

    return (
        f'<div class="se-component se-quotation {QUOTE_STYLE_CLASS}">'
        f'<div class="se-component-content">'
        f'<div class="se-section se-section-quotation {QUOTE_STYLE_CLASS} se-section-align-center">'
        f'<div class="se-quotation-container">'
        f'<div class="se-module se-module-text se-quote">'
        f'{quote_paragraphs}'
        f'</div>'
        f'{cite_html}'
        f'</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )


def build_divider_component():
    """구분선(점선) 컴포넌트 HTML을 생성한다."""
    return (
        f'<div class="se-component se-horizontalLine">'
        f'<div class="se-component-content">'
        f'<div class="se-section se-section-horizontalLine {DIVIDER_STYLE_CLASS} se-section-align-center">'
        f'<div class="se-module se-module-horizontalLine">'
        f'<hr class="se-hr">'
        f'</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )


def blocks_to_editor_html(blocks):
    """
    파싱된 블록 리스트 전체를 에디터 내부 HTML 문자열로 변환한다.
    title 블록은 별도 반환한다 (에디터 제목 필드에 입력해야 하므로).

    Args:
        blocks: parse_html()이 반환한 블록 리스트

    Returns:
        tuple: (title_text, body_html, image_positions)
    """
    title_text = ""
    body_parts = []
    image_positions = []
    image_count = 0

    for i, block in enumerate(blocks):
        block_type = block["type"]
        text = block.get("text", "")
        formatting = block.get("formatting")

        if block_type == "title":
            title_text = text

        elif block_type == "spacing":
            body_parts.append(build_spacing_component())

        elif block_type == "text":
            body_parts.append(build_text_component(text, formatting))

        elif block_type in ("quote_left", "highlight_box", "stat_box",
                            "info_box", "checklist_box", "summary_box"):
            body_parts.append(build_quote_component(text, formatting))

        elif block_type == "divider":
            body_parts.append(build_divider_component())

        elif block_type == "heading":
            body_parts.append(build_heading_component(text, level="h3"))

        elif block_type == "subheading":
            body_parts.append(build_heading_component(text, level="h4"))

        elif block_type == "image_placeholder":
            image_count += 1
            image_positions.append({
                "index": image_count,
                "description": text,
                "block_position": i,
            })
            placeholder_text = f"[이미지 #{image_count} 삽입 위치]"
            body_parts.append(build_text_component(placeholder_text))

    body_html = "\n".join(body_parts)
    return title_text, body_html, image_positions
