"""
exe 파일용 Flask 앱 진입점
템플릿 경로를 exe 실행 환경에 맞게 수정합니다.
"""
import sys
import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename
import io
from pdf2image import convert_from_path
import tempfile
import pandas as pd
import re

# exe 파일로 실행될 때의 경로 처리
if getattr(sys, 'frozen', False):
    # exe 파일로 실행 중인 경우
    base_path = sys._MEIPASS  # PyInstaller가 생성한 임시 폴더
    template_folder = os.path.join(base_path, 'templates')
else:
    # 일반 Python 스크립트로 실행 중인 경우
    base_path = os.path.dirname(os.path.abspath(__file__))
    template_folder = os.path.join(base_path, 'templates')

app = Flask(__name__, template_folder=template_folder)
app.secret_key = 'your-secret-key-change-this'  # 세션 암호화를 위한 비밀키

# Tesseract 실행 파일 경로 설정
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Poppler 경로 설정 (PDF 처리를 위해 필요)
POPPLER_PATH = r"C:\poppler\Library\bin"  # 실제 poppler 설치 경로로 변경 필요

# 업로드 설정
# exe 파일 실행 시 현재 실행 디렉토리에 uploads 폴더 생성
if getattr(sys, 'frozen', False):
    # exe 파일로 실행 중인 경우 실행 파일이 있는 디렉토리 사용
    UPLOAD_FOLDER = os.path.join(os.path.dirname(sys.executable), 'uploads')
else:
    # 일반 Python 스크립트로 실행 중인 경우
    UPLOAD_FOLDER = os.path.join(base_path, 'uploads')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# 업로드 폴더가 없으면 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """허용된 파일 확장자인지 확인"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_image(image_path):
    """이미지 파일에서 텍스트 추출"""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang="kor+eng", config="--psm 6")
        return text
    except Exception as e:
        raise Exception(f"이미지 처리 중 오류 발생: {str(e)}")


def extract_text_from_pdf(pdf_path):
    """PDF 파일을 이미지로 변환 후 텍스트 추출"""
    try:
        # PDF를 이미지로 변환 (poppler 필요)
        if os.path.exists(POPPLER_PATH):
            images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
        else:
            # PATH 환경변수에 poppler가 등록되어 있는 경우
            images = convert_from_path(pdf_path, dpi=300)
        
        extracted_text = ""
        for page_number, image in enumerate(images, start=1):
            # 각 페이지에서 텍스트 추출
            text = pytesseract.image_to_string(image, lang="kor+eng", config="--psm 6")
            extracted_text += f"\n--- 페이지 {page_number} ---\n"
            extracted_text += text + "\n"
        
        return extracted_text
    except Exception as e:
        raise Exception(f"PDF 처리 중 오류 발생: {str(e)}")


def parse_text_to_dataframe(text):
    """추출된 텍스트를 표 형식으로 파싱하여 DataFrame 생성"""
    try:
        lines = text.strip().split('\n')
        rows = []
        
        for line in lines:
            # 빈 줄이나 페이지 구분선 제외
            if not line.strip() or line.strip().startswith('---'):
                continue
            
            # 탭이나 여러 공백으로 구분된 데이터를 분리
            if '\t' in line:
                cells = [cell.strip() for cell in line.split('\t') if cell.strip()]
            elif '|' in line:
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            else:
                cells = [cell.strip() for cell in re.split(r'\s{2,}', line) if cell.strip()]
            
            # 셀이 2개 이상인 경우만 행으로 추가
            if len(cells) >= 2:
                rows.append(cells)
            elif len(cells) == 1 and cells[0]:
                rows.append(cells)
        
        if not rows:
            rows = [[line.strip()] for line in lines if line.strip() and not line.strip().startswith('---')]
        
        if not rows:
            raise ValueError("표 형식의 데이터를 찾을 수 없습니다.")
        
        # 가장 긴 행의 길이를 기준으로 컬럼 수 결정
        max_cols = max(len(row) for row in rows)
        
        # 모든 행을 동일한 길이로 맞춤
        normalized_rows = []
        for row in rows:
            normalized_row = row + [''] * (max_cols - len(row))
            normalized_rows.append(normalized_row[:max_cols])
        
        # 첫 번째 행을 헤더로 사용
        if normalized_rows and all(cell.strip() for cell in normalized_rows[0]):
            headers = normalized_rows[0]
            data_rows = normalized_rows[1:]
        else:
            headers = [f'컬럼{i+1}' for i in range(max_cols)]
            data_rows = normalized_rows
        
        # DataFrame 생성
        df = pd.DataFrame(data_rows, columns=headers)
        
        # 빈 행 제거
        df = df.dropna(how='all')
        
        return df
    except Exception as e:
        raise Exception(f"텍스트 파싱 중 오류 발생: {str(e)}")


def pdf_to_excel(pdf_path):
    """PDF 파일을 엑셀 파일로 변환"""
    try:
        # PDF에서 텍스트 추출
        extracted_text = extract_text_from_pdf(pdf_path)
        
        if not extracted_text.strip():
            raise ValueError("PDF에서 텍스트를 추출할 수 없습니다.")
        
        # 텍스트를 DataFrame으로 파싱
        df = parse_text_to_dataframe(extracted_text)
        
        # Excel 파일을 메모리에 저장
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        excel_buffer.seek(0)
        return excel_buffer
    except Exception as e:
        raise Exception(f"PDF를 엑셀로 변환 중 오류 발생: {str(e)}")


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """파일 업로드 및 텍스트 추출 처리"""
    if 'file' not in request.files:
        flash('파일이 선택되지 않았습니다.', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('파일이 선택되지 않았습니다.', 'error')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('허용되지 않는 파일 형식입니다. (png, jpg, jpeg, gif, bmp, tiff, pdf만 가능)', 'error')
        return redirect(url_for('index'))
    
    try:
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        # 파일 형식에 따라 텍스트 추출
        if file_extension == 'pdf':
            extracted_text = extract_text_from_pdf(temp_file_path)
        else:
            extracted_text = extract_text_from_image(temp_file_path)
        
        # 임시 파일 삭제
        os.unlink(temp_file_path)
        
        if not extracted_text.strip():
            flash('텍스트를 추출할 수 없습니다. 이미지에 텍스트가 없거나 인식이 불가능합니다.', 'warning')
            return redirect(url_for('index'))
        
        # 텍스트를 메모리에 저장하여 다운로드 제공
        text_bytes = io.BytesIO()
        text_bytes.write(extracted_text.encode('utf-8'))
        text_bytes.seek(0)
        
        output_filename = filename.rsplit('.', 1)[0] + '.txt'
        
        return send_file(
            text_bytes,
            mimetype='text/plain',
            as_attachment=True,
            download_name=output_filename
        )
        
    except Exception as e:
        flash(f'처리 중 오류가 발생했습니다: {str(e)}', 'error')
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        return redirect(url_for('index'))


@app.route('/convert-to-excel', methods=['POST'])
def convert_pdf_to_excel():
    """PDF 파일을 엑셀 파일로 변환"""
    if 'file' not in request.files:
        flash('파일이 선택되지 않았습니다.', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('파일이 선택되지 않았습니다.', 'error')
        return redirect(url_for('index'))
    
    filename = secure_filename(file.filename)
    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if file_extension != 'pdf':
        flash('엑셀 변환은 PDF 파일만 지원합니다.', 'error')
        return redirect(url_for('index'))
    
    try:
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        # PDF를 엑셀로 변환
        excel_buffer = pdf_to_excel(temp_file_path)
        
        # 임시 파일 삭제
        os.unlink(temp_file_path)
        
        output_filename = filename.rsplit('.', 1)[0] + '.xlsx'
        
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=output_filename
        )
        
    except Exception as e:
        flash(f'엑셀 변환 중 오류가 발생했습니다: {str(e)}', 'error')
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        return redirect(url_for('index'))


if __name__ == '__main__':
    # exe 파일로 실행될 때는 콘솔 창을 열지 않도록 설정
    import webbrowser
    import threading
    
    def open_browser():
        """브라우저 자동 열기"""
        import time
        time.sleep(1.5)  # 서버 시작 대기
        webbrowser.open('http://127.0.0.1:5000')
    
    # 브라우저 자동 열기 (별도 스레드에서)
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    app.run(debug=False, host='127.0.0.1', port=5000)
