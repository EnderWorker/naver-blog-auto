"""네이버 블로그 자동 포스팅 도구 — 메인 엔트리포인트."""

import os

from config import BLOG_ID, NAVER_URL, HTML_FILE_PATH, get_resource_path
from parser.html_parser import parse_html
from editor.browser import launch_browser, wait_for_login, navigate_to_editor, close_browser
from editor.html_builder import blocks_to_editor_html
from editor.injector import inject_title, inject_body_html, verify_injection


def main():
    print("=" * 50)
    print("  네이버 블로그 자동 포스팅 도구 v2.0")
    print(f"  블로그: {BLOG_ID}")
    print("  방식: DOM 직접 주입")
    print("=" * 50)

    # ── 1단계: 브라우저 실행 ──
    print("\n🌐 브라우저를 실행합니다...")
    context, page = launch_browser()
    page.goto(NAVER_URL, wait_until="domcontentloaded")

    # ── 2단계: 로그인 대기 ──
    wait_for_login(page)

    # ── 3단계: 글쓰기 페이지 이동 ──
    print("📝 블로그 글쓰기 페이지로 이동합니다...")
    navigate_to_editor(page, BLOG_ID)
    print("✅ 에디터 로딩 완료\n")

    # ── 4단계: HTML 파싱 ──
    print("📄 원고 파일을 분석합니다...")
    html_path = get_resource_path(HTML_FILE_PATH)

    if not os.path.exists(html_path):
        raise FileNotFoundError(f"원고 파일을 찾을 수 없습니다: {html_path}")

    blocks = parse_html(html_path)
    print(f"   → 총 {len(blocks)}개 블록 감지")

    type_counts = {}
    for b in blocks:
        t = b["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    for t, c in type_counts.items():
        print(f"   → {t}: {c}개")

    # ── 5단계: 에디터 HTML 변환 ──
    print("\n🔨 에디터 HTML로 변환합니다...")
    title_text, body_html, image_positions = blocks_to_editor_html(blocks)
    title_preview = (title_text[:30] + "...") if len(title_text) > 30 else title_text
    print(f"   → 제목: {title_preview}")
    print(f"   → 본문 HTML: {len(body_html):,} bytes")
    print(f"   → 이미지 위치: {len(image_positions)}곳")

    # ── 6단계: 제목 입력 ──
    if title_text:
        print("\n📌 제목을 입력합니다...")
        inject_title(page, title_text)
        print("   ✅ 제목 입력 완료")

    # ── 7단계: 본문 DOM 주입 ──
    print("\n🚀 본문을 에디터에 주입합니다...")
    result = inject_body_html(page, body_html)
    print(f"   ✅ DOM 주입 완료 (결과: {result})")

    # ── 8단계: 주입 검증 ──
    print("\n🔍 주입 결과를 검증합니다...")
    verification = verify_injection(page)
    if "error" in verification:
        print(f"   ⚠️  검증 실패: {verification['error']}")
    else:
        print(f"   → 총 컴포넌트: {verification['total']}개")
        for comp_type, count in verification.get("types", {}).items():
            print(f"   → {comp_type}: {count}개")

    # ── 9단계: 이미지 위치 안내 ──
    if image_positions:
        print(f"\n🖼️  이미지 삽입이 필요한 위치 ({len(image_positions)}곳):")
        for img in image_positions:
            desc = img["description"][:50]
            print(f"   #{img['index']}: {desc}...")

    # ── 완료 ──
    print("\n" + "=" * 50)
    print("✅ 원고 입력이 완료되었습니다!")
    print("👉 아래 작업을 직접 진행하세요:")
    print("   1. [이미지 삽입 위치] 텍스트를 찾아 실제 이미지로 교체")
    print("   2. 카테고리 / 태그 설정")
    print("   3. 발행")
    print("=" * 50)

    close_browser(context)


def _start_esc_listener():
    """백그라운드 스레드에서 ESC 키를 감지하여 메인 스레드를 중단한다."""
    import msvcrt
    import threading
    import _thread
    import time

    def _listen():
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\x1b':  # ESC
                    print("\n\n⛔ ESC 키가 감지되었습니다. 프로그램을 종료합니다...")
                    _thread.interrupt_main()
                    return
            time.sleep(0.05)

    threading.Thread(target=_listen, daemon=True).start()


if __name__ == "__main__":
    import traceback
    _start_esc_listener()
    try:
        main()
    except KeyboardInterrupt:
        print("\n⛔ 사용자에 의해 중단되었습니다.")
    except Exception:
        print("\n" + "=" * 50)
        print("❌ 오류가 발생하여 프로그램이 종료되었습니다.")
        print("=" * 50)
        traceback.print_exc()
    finally:
        input("\n종료하려면 Enter를 누르세요...")
