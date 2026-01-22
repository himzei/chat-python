# 이미지/PDF 텍스트 추출기

이미지 파일 또는 PDF 파일에서 텍스트를 추출하여 텍스트 파일로 다운로드할 수 있는 Flask 웹 애플리케이션입니다.

## 주요 기능

- 📷 **이미지 OCR**: PNG, JPG, JPEG, GIF, BMP, TIFF 파일에서 텍스트 추출
- 📄 **PDF OCR**: PDF 파일의 각 페이지에서 텍스트 추출
- 🌏 **다국어 지원**: 한국어와 영어 텍스트 인식
- 💾 **다운로드**: 추출된 텍스트를 .txt 파일로 즉시 다운로드
- 🎨 **모던 UI**: 드래그 앤 드롭을 지원하는 직관적인 인터페이스

## 사전 요구사항

### 1. Tesseract OCR 설치

**Windows:**
- [Tesseract OCR 다운로드](https://github.com/UB-Mannheim/tesseract/wiki)
- 설치 후 기본 경로: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- 한국어 언어팩도 함께 설치하세요

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-kor
```

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang
```

### 2. Poppler 설치 (PDF 처리용)

**Windows:**
1. [Poppler Windows 다운로드](https://github.com/oschwartz10612/poppler-windows/releases/)
   - 최신 `Release-XX.XX.X-X.zip` 파일 다운로드
2. 압축 해제 (예: `C:\poppler`)
3. `app.py` 파일에서 POPPLER_PATH 수정:
   ```python
   POPPLER_PATH = r"C:\poppler\Library\bin"  # 실제 경로로 변경
   ```
4. (선택사항) 시스템 PATH에 추가하면 코드 수정 불필요

**Linux:**
```bash
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

## 설치 방법

1. **저장소 클론 또는 파일 다운로드**

2. **가상환경 생성 및 활성화** (권장)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **필요한 패키지 설치**
```bash
pip install -r requirements.txt
```

4. **경로 설정 확인**
- `app.py` 파일에서 Tesseract와 Poppler 경로가 올바른지 확인
```python
# Tesseract 경로
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Poppler 경로 (PDF 처리 시 필요)
POPPLER_PATH = r"C:\poppler\Library\bin"
```

## 실행 방법

```bash
python app.py
```

서버가 시작되면 브라우저에서 다음 주소로 접속:
```
http://localhost:5000
```

## 사용 방법

1. 웹 페이지에서 **파일 선택** 또는 **드래그 앤 드롭**으로 이미지/PDF 파일 업로드
2. **텍스트 추출하기** 버튼 클릭
3. 추출된 텍스트가 `.txt` 파일로 자동 다운로드됨

## 지원 파일 형식

- **이미지**: PNG, JPG, JPEG, GIF, BMP, TIFF
- **문서**: PDF
- **최대 파일 크기**: 16MB

## 기술 스택

- **Backend**: Flask (Python)
- **OCR Engine**: Tesseract OCR
- **이미지 처리**: Pillow (PIL)
- **PDF 처리**: pdf2image
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## 주의사항

- OCR 정확도는 이미지 품질에 따라 달라질 수 있습니다
- 고해상도의 선명한 이미지를 사용하면 더 좋은 결과를 얻을 수 있습니다
- PDF 파일 처리는 이미지 파일보다 시간이 더 소요될 수 있습니다
- 손글씨 인식 정확도는 제한적일 수 있습니다

## 문제 해결

### Tesseract를 찾을 수 없다는 에러
- Tesseract가 올바르게 설치되었는지 확인
- `app.py`의 `tesseract_cmd` 경로가 올바른지 확인

### PDF 처리 오류 (`Unable to get page count`)
- Poppler가 설치되어 있는지 확인
- `app.py`의 `POPPLER_PATH` 경로가 올바른지 확인
- Windows의 경우 Poppler의 `bin` 폴더 내에 `pdfinfo.exe`가 있는지 확인
- 또는 Poppler의 `bin` 폴더를 시스템 PATH에 추가

### 한국어 인식이 안 됨
- Tesseract 한국어 언어팩이 설치되어 있는지 확인

## 라이선스

개인 및 상업적 용도로 자유롭게 사용 가능합니다.
