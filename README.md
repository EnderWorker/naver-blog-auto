# NaverBlogAuto — 네이버 블로그 자동 포스팅 도구

원고.html 파일을 파싱하여 네이버 블로그 스마트에디터 ONE에
제목 + 본문 + 인용구 + 구분선을 자동으로 입력하는 Windows 데스크탑 도구입니다.

## 요구사항

- Python 3.11+
- Windows OS
- 네이버 계정 (수동 로그인)

## 설치

```bash
pip install -r requirements.txt
playwright install chromium
```

## 사용법

1. `assets/` 폴더에 `원고.html` 파일을 넣습니다.
2. `config.py`에서 `BLOG_ID`를 본인 블로그 ID로 변경합니다.
3. 실행합니다:
   ```bash
   python main.py
   ```
4. 브라우저가 열리면 네이버에 로그인합니다.
5. 콘솔에서 Enter를 누르면 자동 입력이 시작됩니다.
6. 완료 후 이미지 업로드 / 카테고리 / 태그 / 발행을 직접 진행합니다.

## exe 빌드

```bash
build.bat
```
빌드 결과: `dist/NaverBlogAuto.exe`

## 설정 (config.py)

| 항목 | 기본값 | 설명 |
|------|--------|------|
| BLOG_ID | enjees_world | 네이버 블로그 ID |
| QUOTE_STYLE | 4 | 인용구 스타일 번호 (1~5) |
| DIVIDER_STYLE | dot | 구분선 스타일 (dot=점선) |
| BODY_SIZE | 16 | 본문 글자 크기 (px) |
| HEADING_SIZE | 24 | 대제목 글자 크기 (px) |
| SUBHEADING_SIZE | 18 | 소제목 글자 크기 (px) |
| ACTION_DELAY | 300 | 동작 간 대기 시간 (ms) |

## 지원하는 원고 블록 타입

- 포스트 제목 (title)
- 일반 본문 (text) — bold, color, size 서식 포함
- 인용구 (quote_left, highlight_box, stat_box, info_box, summary_box)
- 체크리스트 (checklist_box)
- 구분선 (divider)
- 대제목 / 소제목 (heading / subheading)
- 빈 줄 (spacing)
- 이미지 위치 표시 (image_placeholder) — 스킵, 콘솔 로그만 출력

## 주의사항

- 네이버 로그인은 수동으로 진행해야 합니다.
- 스마트에디터 ONE 업데이트 시 셀렉터 수정이 필요할 수 있습니다.
- exe를 다른 PC에 배포할 경우 해당 PC에서도 `playwright install chromium` 실행이 필요합니다.
