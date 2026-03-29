@echo off
echo [1/2] Installing dependencies...
pip install -r requirements.txt
playwright install chromium

echo [2/2] Building exe...
pyinstaller --onefile --name NaverBlogAuto --add-data "assets;assets" main.py

echo Done! Check dist/NaverBlogAuto.exe
pause
