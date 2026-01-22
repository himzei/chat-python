@echo off
chcp 65001 >nul
echo ========================================
echo 이미지/PDF 텍스트 추출기 EXE 빌드 스크립트
echo ========================================
echo.

REM PyInstaller 설치 확인
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller가 설치되어 있지 않습니다. 설치 중...
    pip install pyinstaller
    if errorlevel 1 (
        echo PyInstaller 설치 실패!
        pause
        exit /b 1
    )
)

echo.
echo EXE 파일 빌드 시작...
echo.

REM PyInstaller로 빌드 실행 (app_exe.py 사용)
pyinstaller --name=img2text ^
    --onefile ^
    --windowed ^
    --add-data="templates;templates" ^
    --hidden-import=flask ^
    --hidden-import=pytesseract ^
    --hidden-import=PIL ^
    --hidden-import=pdf2image ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=werkzeug ^
    --hidden-import=webbrowser ^
    --collect-all=flask ^
    --collect-all=pytesseract ^
    --collect-all=PIL ^
    --collect-all=pdf2image ^
    app_exe.py

if errorlevel 1 (
    echo.
    echo 빌드 실패!
    pause
    exit /b 1
)

echo.
echo ========================================
echo 빌드 완료!
echo ========================================
echo.
echo exe 파일 위치: dist\img2text.exe
echo.
pause
