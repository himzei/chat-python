# EXE 파일 빌드 가이드

이미지/PDF 텍스트 추출기를 exe 파일로 빌드하는 방법입니다.

## 사전 요구사항

1. **Python 설치** (3.8 이상 권장)
2. **Tesseract OCR 설치**
   - 다운로드: https://github.com/UB-Mannheim/tesseract/wiki
   - 기본 설치 경로: `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. **Poppler 설치** (PDF 처리용, 선택사항)
   - 다운로드: https://github.com/oschwartz10612/poppler-windows/releases
   - 설치 경로: `C:\poppler\Library\bin` (또는 PATH 환경변수에 등록)

## 빌드 방법

### 방법 1: 배치 파일 사용 (권장)

1. 명령 프롬프트 또는 PowerShell을 관리자 권한으로 실행
2. 프로젝트 폴더로 이동:
   ```bash
   cd C:\Users\krcea\Documents\chat-python\img2text
   ```
3. 배치 파일 실행:
   ```bash
   build_exe.bat
   ```

빌드가 완료되면 `dist` 폴더에 `img2text.exe` 파일이 생성됩니다.

### 방법 2: 수동 빌드

1. 필요한 패키지 설치:
   ```bash
   pip install -r requirements.txt
   ```

2. PyInstaller로 빌드:
   ```bash
   pyinstaller --name=img2text --onefile --windowed --add-data="templates;templates" --hidden-import=flask --hidden-import=pytesseract --hidden-import=PIL --hidden-import=pdf2image --hidden-import=pandas --hidden-import=openpyxl --hidden-import=werkzeug --hidden-import=webbrowser --collect-all=flask --collect-all=pytesseract --collect-all=PIL --collect-all=pdf2image app_exe.py
   ```

## 빌드 결과

- **exe 파일 위치**: `dist\img2text.exe`
- **빌드 임시 파일**: `build` 폴더 (삭제 가능)
- **spec 파일**: `img2text.spec` (재빌드 시 사용 가능)

## exe 파일 실행 방법

1. `dist\img2text.exe` 파일을 더블클릭하여 실행
2. 자동으로 웹 브라우저가 열리며 `http://127.0.0.1:5000`에서 앱이 실행됩니다
3. 이미지나 PDF 파일을 업로드하여 텍스트 추출

## 주의사항

1. **Tesseract OCR 필수**: exe 파일을 실행하는 컴퓨터에 Tesseract OCR이 설치되어 있어야 합니다.
   - 설치 경로: `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - 다른 경로에 설치한 경우 `app_exe.py`의 경로를 수정해야 합니다.

2. **Poppler (PDF 처리용)**: PDF 파일을 처리하려면 Poppler가 필요합니다.
   - 설치 경로: `C:\poppler\Library\bin`
   - 다른 경로에 설치한 경우 `app_exe.py`의 `POPPLER_PATH` 변수를 수정해야 합니다.

3. **업로드 폴더**: exe 파일 실행 시 exe 파일이 있는 디렉토리에 `uploads` 폴더가 자동으로 생성됩니다.

4. **방화벽 경고**: exe 파일을 처음 실행할 때 Windows 방화벽 경고가 나타날 수 있습니다. "액세스 허용"을 선택하세요.

## 문제 해결

### 빌드 오류 발생 시

1. 모든 의존성이 설치되었는지 확인:
   ```bash
   pip install -r requirements.txt
   ```

2. PyInstaller가 최신 버전인지 확인:
   ```bash
   pip install --upgrade pyinstaller
   ```

### exe 실행 오류 발생 시

1. Tesseract OCR이 올바른 경로에 설치되어 있는지 확인
2. 필요한 언어 팩이 설치되어 있는지 확인 (한국어: kor)
3. 콘솔 창이 나타나는 경우 오류 메시지를 확인하세요

### 템플릿 파일을 찾을 수 없다는 오류 발생 시

- `templates` 폴더가 exe 파일과 같은 디렉토리에 있는지 확인
- 빌드 시 `--add-data="templates;templates"` 옵션이 포함되었는지 확인

## 배포

exe 파일을 다른 컴퓨터에서 실행하려면:

1. `dist\img2text.exe` 파일 복사
2. 대상 컴퓨터에 Tesseract OCR 설치
3. (선택사항) Poppler 설치 (PDF 처리용)
4. exe 파일 실행

**참고**: exe 파일은 단일 파일로 패키징되어 있지만, 실행 시 임시 폴더에 압축을 풀기 때문에 첫 실행이 다소 느릴 수 있습니다.
