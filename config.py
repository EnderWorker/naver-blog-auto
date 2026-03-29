import sys
import os

BLOG_ID = "enjees_world"
HTML_FILE_PATH = "assets/원고.html"
EDITOR_URL = f"https://blog.naver.com/{BLOG_ID}/postwrite"
NAVER_URL = "https://www.naver.com"

# 인용구 스타일: 4번 (심플 좌측 라인)
QUOTE_STYLE = 4
# 구분선 스타일: 점선
DIVIDER_STYLE = "dot"

# 글자 크기 (모바일 최적화)
TITLE_SIZE = 28
HEADING_SIZE = 24
SUBHEADING_SIZE = 18
BODY_SIZE = 16

# 동작 안정화 딜레이 (ms)
ACTION_DELAY = 300
LOAD_DELAY = 2000


def get_resource_path(relative_path):
    """리소스 경로를 반환한다. exe 모드에서는 실행 파일 위치 기준으로 탐색한다."""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)
