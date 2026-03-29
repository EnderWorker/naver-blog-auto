@echo off
echo ============================================
echo   NaverBlogAuto Build Script
echo ============================================

echo.
echo [1/3] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [2/3] Installing Chromium browser...
playwright install chromium

echo.
echo [3/3] Building exe...
pyinstaller --onefile --name NaverBlogAuto --add-data "assets;assets" main.py

echo.
echo ============================================
echo   Build complete! -^> dist\NaverBlogAuto.exe
echo ============================================
echo.
echo ⚠️  주의사항:
echo   - exe를 다른 PC에 배포할 경우, 해당 PC에서도
echo     pip install playwright 후
echo     playwright install chromium 을 실행해야 합니다.
echo   - assets 폴더에 원고.html 파일을 넣어야 합니다.
echo.
pause
