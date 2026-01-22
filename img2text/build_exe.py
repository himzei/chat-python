"""
exe 파일 빌드 스크립트
PyInstaller를 사용하여 Flask 앱을 exe 파일로 변환합니다.
"""
import PyInstaller.__main__
import os

# 현재 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# PyInstaller 옵션 설정
PyInstaller.__main__.run([
    'app_exe.py',  # exe용 메인 파일 (템플릿 경로 처리 포함)
    '--name=img2text',  # exe 파일 이름
    '--onefile',  # 단일 파일로 생성
    '--windowed',  # 콘솔 창 숨기기 (GUI 앱)
    '--add-data=templates;templates',  # 템플릿 폴더 포함
    '--hidden-import=flask',  # Flask 명시적 포함
    '--hidden-import=pytesseract',  # pytesseract 명시적 포함
    '--hidden-import=PIL',  # PIL 명시적 포함
    '--hidden-import=pdf2image',  # pdf2image 명시적 포함
    '--hidden-import=pandas',  # pandas 명시적 포함
    '--hidden-import=openpyxl',  # openpyxl 명시적 포함
    '--hidden-import=werkzeug',  # werkzeug 명시적 포함
    '--hidden-import=webbrowser',  # webbrowser 명시적 포함
    '--collect-all=flask',  # Flask의 모든 서브모듈 수집
    '--collect-all=pytesseract',  # pytesseract의 모든 서브모듈 수집
    '--collect-all=PIL',  # PIL의 모든 서브모듈 수집
    '--collect-all=pdf2image',  # pdf2image의 모든 서브모듈 수집
    '--icon=NONE',  # 아이콘 없음 (필요시 아이콘 파일 경로 지정)
])
