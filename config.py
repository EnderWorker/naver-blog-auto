import sys
import os

BLOG_ID = "enjees_world"
HTML_FILE_PATH = "assets/원고.html"
EDITOR_URL = f"https://blog.naver.com/{BLOG_ID}/postwrite"
NAVER_URL = "https://www.naver.com"

# ── 브라우저 설정 ──
BROWSER_CHANNEL = "chrome"

# ── 에디터 HTML 생성 설정 ──
# 본문 텍스트
BODY_FONT = "se-ff-system"
BODY_SIZE = "se-fs16"
BODY_ALIGN = "se-text-paragraph-align-center"
BODY_LINE_HEIGHT = "2"
BODY_COLOR = "rgb(0, 0, 0)"

# 소제목
HEADING_FONT = "se-ff-system"
HEADING_SIZE = "se-fs24"
HEADING_ALIGN = "se-text-paragraph-align-center"
HEADING_LINE_HEIGHT = "2"
HEADING_COLOR = "rgb(0, 0, 0)"
HEADING_BOLD = True

# 대제목
TITLE_HEADING_FONT = "se-ff-system"
TITLE_HEADING_SIZE = "se-fs28"
TITLE_HEADING_ALIGN = "se-text-paragraph-align-center"
TITLE_HEADING_LINE_HEIGHT = "2"
TITLE_HEADING_COLOR = "rgb(0, 0, 0)"
TITLE_HEADING_BOLD = True

# 인용구 (밑줄 스타일)
QUOTE_STYLE_CLASS = "se-l-quotation_underline"
QUOTE_FONT = "se-ff-nanummyeongjo"
QUOTE_SIZE = "se-fs19"
QUOTE_LINE_HEIGHT = "1.8"
QUOTE_COLOR = "rgb(0, 0, 0)"
CITE_FONT = "se-ff-nanumgothic"
CITE_SIZE = "se-fs13"
CITE_COLOR = "rgb(119, 119, 119)"

# 구분선 (점선)
DIVIDER_STYLE_CLASS = "se-l-line5"

# 동작 딜레이 (ms)
ACTION_DELAY = 300
LOAD_DELAY = 2000


def get_resource_path(relative_path):
    """리소스 경로를 반환한다. exe 모드에서는 실행 파일 위치 기준으로 탐색한다."""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)
