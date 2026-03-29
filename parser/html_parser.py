"""원고.html 파서 — HTML을 블록 리스트로 변환한다."""

import re
from bs4 import BeautifulSoup, Tag


def _get_style(tag):
    """태그의 style 속성을 딕셔너리로 반환한다."""
    raw = tag.get("style", "")
    if not raw:
        return {}
    pairs = {}
    for part in raw.split(";"):
        part = part.strip()
        if ":" not in part:
            continue
        key, val = part.split(":", 1)
        pairs[key.strip().lower()] = val.strip()
    return pairs


def _extract_formatting(tag):
    """태그 내부의 bold/color/size 서식 정보를 추출한다. 동일 텍스트는 병합."""
    raw = []
    for child in tag.descendants:
        if not isinstance(child, Tag):
            continue
        text = child.get_text(strip=True)
        if not text:
            continue
        if child.name in ("b", "strong"):
            raw.append({"type": "bold", "text": text})
        elif child.name == "span":
            style = _get_style(child)
            if "color" in style:
                raw.append({"type": "color", "text": text, "color": style["color"]})
            if "font-size" in style:
                size_str = style["font-size"].replace("px", "").strip()
                try:
                    raw.append({"type": "size", "text": text, "size": int(size_str)})
                except ValueError:
                    pass
            if "font-weight" in style and style["font-weight"] == "bold":
                raw.append({"type": "bold", "text": text})

    # 동일 텍스트에 대한 서식을 병합하여 반환
    merged = {}
    for f in raw:
        ft = f["text"]
        if ft not in merged:
            merged[ft] = []
        # 중복 type+text 조합은 건너뛴다
        if not any(existing["type"] == f["type"] and existing["text"] == ft for existing in merged[ft]):
            merged[ft].append(f)

    result = []
    for entries in merged.values():
        result.extend(entries)
    return result


def _inner_text(tag):
    """태그 내부 텍스트를 추출한다. <br>은 줄바꿈으로 변환."""
    for br in tag.find_all("br"):
        br.replace_with("\n")
    return tag.get_text().strip()


def _inner_text_space(tag):
    """태그 내부 텍스트를 추출한다. <br>은 공백으로 변환."""
    for br in tag.find_all("br"):
        br.replace_with(" ")
    return tag.get_text().strip()


def _is_spacing(tag):
    """빈 줄(spacing) 블록인지 판별한다."""
    if tag.name != "p":
        return False
    html = tag.decode_contents().strip()
    if html in ("&nbsp;", "\xa0", ""):
        return True
    text = tag.get_text(strip=True)
    if text in ("", "\xa0"):
        return True
    return False


def _is_title(tag):
    """제목 블록인지 판별한다 (font-size:28px + bold)."""
    if tag.name != "p":
        return False
    style = _get_style(tag)
    fs = style.get("font-size", "")
    fw = style.get("font-weight", "")
    if "28" in fs and fw == "bold":
        return True
    for child in tag.descendants:
        if isinstance(child, Tag):
            cs = _get_style(child)
            if "28" in cs.get("font-size", "") and (
                cs.get("font-weight", "") == "bold"
                or child.name in ("b", "strong")
            ):
                return True
    return False


def _is_quote_left(tag):
    """좌측 라인 인용구인지 판별한다."""
    if tag.name != "div":
        return False
    style = _get_style(tag)
    return "border-left" in style and "background" in style


def _is_highlight_box(tag):
    """어두운 그라데이션 강조 박스인지 판별한다."""
    if tag.name != "div":
        return False
    style = _get_style(tag)
    bg = style.get("background", "")
    return "linear-gradient" in bg and "#1a1a2e" in bg


def _is_stat_box(tag):
    """통계 데이터 박스 (컬러풀 그라데이션)인지 판별한다."""
    if tag.name != "div":
        return False
    style = _get_style(tag)
    bg = style.get("background", "")
    return "linear-gradient" in bg and "to right" in bg


def _is_info_box(tag):
    """노란 정보 박스인지 판별한다."""
    if tag.name != "div":
        return False
    style = _get_style(tag)
    return "#fff3cd" in style.get("background", "") and "#ffc107" in style.get("border", "")


def _is_checklist_box(tag):
    """체크리스트 박스인지 판별한다."""
    if tag.name != "div":
        return False
    style = _get_style(tag)
    bg = style.get("background", "")
    text = tag.get_text()
    return "#f5f5f5" in bg and any(c in text for c in ("✓", "✔", "✅", "☑", "✗"))


def _is_summary_box(tag):
    """마지막 요약 박스인지 판별한다."""
    if tag.name != "div":
        return False
    style = _get_style(tag)
    return "#fafafa" in style.get("background", "") and "2px solid #e0e0e0" in style.get("border", "")


def _is_divider(tag):
    """구분선인지 판별한다."""
    if tag.name != "div":
        return False
    style = _get_style(tag)
    if "border-top" not in style:
        return False
    text = tag.get_text(strip=True)
    return text == ""


def _is_heading(tag):
    """섹션 대제목인지 판별한다."""
    if tag.name != "p":
        return False
    style = _get_style(tag)
    has_border = "border-left" in style and "6px" in style.get("border-left", "")
    has_size = "24" in style.get("font-size", "")
    has_bold = style.get("font-weight", "") == "bold"
    if has_border and has_size and has_bold:
        return True
    for child in tag.descendants:
        if isinstance(child, Tag):
            cs = _get_style(child)
            if "border-left" in cs and "6px" in cs.get("border-left", ""):
                if "24" in cs.get("font-size", "") or "24" in style.get("font-size", ""):
                    return True
    return False


def _is_subheading(tag):
    """소제목인지 판별한다."""
    if tag.name != "p":
        return False
    style = _get_style(tag)
    bg = style.get("background", "")
    display = style.get("display", "")
    fw = style.get("font-weight", "")
    subheading_colors = ("#eaf2f8", "#fdf2e9", "#f4ecf7")
    if any(c in bg for c in subheading_colors) and "inline-block" in display and fw == "bold":
        return True
    for child in tag.descendants:
        if isinstance(child, Tag):
            cs = _get_style(child)
            cbg = cs.get("background", "")
            if any(c in cbg for c in subheading_colors) and cs.get("font-weight", "") == "bold":
                return True
    return False


def _is_image_placeholder(tag):
    """이미지 위치 표시인지 판별한다."""
    if tag.name != "p":
        return False
    style = _get_style(tag)
    color = style.get("color", "")
    fs = style.get("font-size", "")
    text = tag.get_text(strip=True)
    return "#999" in color and "13" in fs and text.startswith("[이미지:")


def parse_html(filepath):
    """
    원고.html을 파싱하여 블록 리스트를 반환한다.

    Returns:
        list[dict]: 각 블록은 type 키를 포함하며,
                    text, formatting 등 추가 키를 가질 수 있다.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # 최상위 <div> 찾기 — 없으면 body 또는 soup 자체
    root = soup.find("div")
    if root is None:
        root = soup.find("body") or soup

    blocks = []
    title_found = False

    for child in root.children:
        if not isinstance(child, Tag):
            continue

        # 1. title (첫 번째만)
        if not title_found and _is_title(child):
            title_found = True
            blocks.append({
                "type": "title",
                "text": _inner_text_space(child),
                "formatting": _extract_formatting(child),
            })
            continue

        # 2. spacing
        if _is_spacing(child):
            blocks.append({"type": "spacing"})
            continue

        # 3. quote_left
        if _is_quote_left(child):
            blocks.append({
                "type": "quote_left",
                "text": _inner_text(child),
                "formatting": _extract_formatting(child),
            })
            continue

        # 4. highlight_box
        if _is_highlight_box(child):
            fmt = _extract_formatting(child)
            # ffd700 span → bold 처리
            for span in child.find_all("span"):
                s = _get_style(span)
                if s.get("color", "").lower() == "#ffd700":
                    t = span.get_text(strip=True)
                    if t and not any(f.get("text") == t and f.get("type") == "bold" for f in fmt):
                        fmt.append({"type": "bold", "text": t})
            blocks.append({
                "type": "highlight_box",
                "text": _inner_text(child),
                "formatting": fmt,
            })
            continue

        # 5. stat_box
        if _is_stat_box(child):
            blocks.append({
                "type": "stat_box",
                "text": _inner_text(child),
                "formatting": _extract_formatting(child),
            })
            continue

        # 6. info_box
        if _is_info_box(child):
            blocks.append({
                "type": "info_box",
                "text": _inner_text(child),
                "formatting": _extract_formatting(child),
            })
            continue

        # 7. checklist_box
        if _is_checklist_box(child):
            blocks.append({
                "type": "checklist_box",
                "text": _inner_text(child),
                "formatting": _extract_formatting(child),
            })
            continue

        # 8. summary_box
        if _is_summary_box(child):
            blocks.append({
                "type": "summary_box",
                "text": _inner_text(child),
                "formatting": _extract_formatting(child),
            })
            continue

        # 9. divider
        if _is_divider(child):
            blocks.append({"type": "divider"})
            continue

        # 10. heading
        if _is_heading(child):
            blocks.append({
                "type": "heading",
                "text": _inner_text(child),
                "formatting": _extract_formatting(child),
            })
            continue

        # 11. subheading
        if _is_subheading(child):
            blocks.append({
                "type": "subheading",
                "text": _inner_text(child),
                "formatting": _extract_formatting(child),
            })
            continue

        # 12. image_placeholder
        if _is_image_placeholder(child):
            blocks.append({
                "type": "image_placeholder",
                "text": child.get_text(strip=True),
            })
            continue

        # 13. text (기본)
        if child.name == "p":
            text = _inner_text(child)
            if text:
                blocks.append({
                    "type": "text",
                    "text": text,
                    "formatting": _extract_formatting(child),
                })
            continue

        # div 등 기타 태그 중 텍스트가 있으면 text로 처리
        text = _inner_text(child)
        if text:
            blocks.append({
                "type": "text",
                "text": text,
                "formatting": _extract_formatting(child),
            })

    return blocks
