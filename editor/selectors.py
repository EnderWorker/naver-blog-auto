"""네이버 스마트에디터 ONE DOM 셀렉터 정의."""

# 제목 영역
TITLE_INPUT = ".se-documentTitle .se-text-paragraph"

# 본문 편집 영역
BODY_AREA = ".se-component-content .se-text-paragraph"

# 툴바 버튼
TOOLBAR_QUOTE = 'button[data-name="quotation"]'
TOOLBAR_DIVIDER = 'button[data-name="horizontalLine"]'
TOOLBAR_BOLD = 'button[data-name="bold"]'
TOOLBAR_FONT_SIZE = "button.se-text-size-button"

# 인용구 스타일 선택
QUOTE_STYLE_PREFIX = ".se-quotation-style-"

# 구분선 스타일 선택
DIVIDER_STYLE_DOT = 'button[data-style="dot"]'

# 글자 크기 드롭다운 항목
FONT_SIZE_ITEM = '.se-font-size-item[data-size="{}"]'

# 에디터 컨테이너 (로딩 확인용)
EDITOR_CONTAINER = ".se-documentTitle"

# 본문 컴포넌트의 마지막 텍스트 영역
LAST_PARAGRAPH = ".se-component:last-child .se-text-paragraph"
