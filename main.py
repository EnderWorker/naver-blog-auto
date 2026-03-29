"""네이버 블로그 자동 포스팅 도구 — 메인 엔트리포인트."""

from config import (
    BLOG_ID, NAVER_URL, ACTION_DELAY, QUOTE_STYLE,
    DIVIDER_STYLE, HTML_FILE_PATH, get_resource_path,
)
from parser.html_parser import parse_html
from editor.browser import launch_browser, wait_for_login, navigate_to_editor, close_browser
from editor.controller import (
    set_title,
    insert_text,
    insert_quote,
    insert_divider,
    insert_heading,
    insert_spacing,
)


def main():
    print("=" * 50)
    print("  네이버 블로그 자동 포스팅 도구")
    print(f"  블로그: {BLOG_ID}")
    print("=" * 50)

    # 1단계: 브라우저 실행
    print("\n🌐 브라우저를 실행합니다...")
    context, page = launch_browser()
    page.goto(NAVER_URL, wait_until="domcontentloaded")

    # 2단계: 로그인 대기
    wait_for_login(page)

    # 3단계: 글쓰기 페이지 이동
    print("📝 블로그 글쓰기 페이지로 이동합니다...")
    navigate_to_editor(page, BLOG_ID)
    print("✅ 에디터 로딩 완료")

    # 4단계: HTML 파싱
    print("📄 원고 파일을 분석합니다...")
    html_path = get_resource_path(HTML_FILE_PATH)
    blocks = parse_html(html_path)
    print(f"   → 총 {len(blocks)}개 블록 감지")

    # 5단계: 에디터에 순차 입력
    print("\n🚀 에디터에 입력을 시작합니다...\n")
    image_count = 0
    total = len(blocks)

    for i, block in enumerate(blocks):
        block_type = block["type"]

        try:
            if block_type == "title":
                print(f"  [{i+1}/{total}] 📌 제목 입력")
                set_title(page, block["text"])

            elif block_type == "spacing":
                insert_spacing(page)

            elif block_type == "text":
                print(f"  [{i+1}/{total}] 📝 본문 텍스트")
                insert_text(page, block["text"], block.get("formatting"))

            elif block_type in ("quote_left", "highlight_box", "stat_box",
                                "info_box", "summary_box"):
                print(f"  [{i+1}/{total}] 💬 인용구 ({block_type})")
                insert_quote(page, block["text"], style=QUOTE_STYLE,
                             formatting=block.get("formatting"))

            elif block_type == "checklist_box":
                print(f"  [{i+1}/{total}] ✅ 체크리스트 (인용구 처리)")
                insert_quote(page, block["text"], style=QUOTE_STYLE,
                             formatting=block.get("formatting"))

            elif block_type == "divider":
                print(f"  [{i+1}/{total}] ── 구분선")
                insert_divider(page, style=DIVIDER_STYLE)

            elif block_type == "heading":
                print(f"  [{i+1}/{total}] 📋 대제목: {block['text'][:20]}...")
                insert_heading(page, block["text"], level="h3")

            elif block_type == "subheading":
                print(f"  [{i+1}/{total}] 📎 소제목: {block['text'][:20]}...")
                insert_heading(page, block["text"], level="h4")

            elif block_type == "image_placeholder":
                image_count += 1
                print(f"  [{i+1}/{total}] 🖼️  이미지 #{image_count} 스킵: {block['text'][:30]}...")

        except Exception as e:
            print(f"  ⚠️  [{i+1}/{total}] {block_type} 입력 실패: {e}")
            continue

        page.wait_for_timeout(ACTION_DELAY)

    # 6단계: 완료
    print("\n" + "=" * 50)
    print("✅ 원고 입력이 완료되었습니다!")
    print(f"🖼️  이미지 삽입 필요 위치: {image_count}곳")
    print("👉 이미지 업로드 / 카테고리 / 태그 / 발행을 직접 진행하세요.")
    print("=" * 50)
    close_browser(context)


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception:
        print("\n" + "=" * 50)
        print("❌ 오류가 발생하여 프로그램이 종료되었습니다.")
        print("=" * 50)
        traceback.print_exc()
    finally:
        input("\n종료하려면 Enter를 누르세요...")
