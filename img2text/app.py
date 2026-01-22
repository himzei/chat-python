from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import pytesseract
from PIL import Image
import os
from werkzeug.utils import secure_filename
import io
from pdf2image import convert_from_path
import tempfile
import pandas as pd
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # 세션 암호화를 위한 비밀키

# Tesseract 실행 파일 경로 설정
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Poppler 경로 설정 (PDF 처리를 위해 필요)
# poppler를 C:\poppler에 설치한 경우, 아래 경로를 실제 설치 경로로 수정하세요
POPPLER_PATH = r"C:\poppler\Library\bin"  # 실제 poppler 설치 경로로 변경 필요

# 업로드 설정
UPLOAD_FOLDER = 'uploads'
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
        # poppler_path가 존재하는 경우에만 사용
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
            # 일반적인 구분자: 탭, 2개 이상의 공백, | (파이프)
            if '\t' in line:
                # 탭으로 구분된 경우
                cells = [cell.strip() for cell in line.split('\t') if cell.strip()]
            elif '|' in line:
                # 파이프로 구분된 경우
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            else:
                # 여러 공백으로 구분된 경우 (2개 이상의 연속 공백)
                cells = [cell.strip() for cell in re.split(r'\s{2,}', line) if cell.strip()]
            
            # 셀이 2개 이상인 경우만 행으로 추가 (단일 텍스트는 제외)
            if len(cells) >= 2:
                rows.append(cells)
            elif len(cells) == 1 and cells[0]:
                # 단일 셀인 경우도 추가 (텍스트 데이터)
                rows.append(cells)
        
        if not rows:
            # 표 형식이 아닌 경우, 각 줄을 하나의 행으로 처리
            rows = [[line.strip()] for line in lines if line.strip() and not line.strip().startswith('---')]
        
        if not rows:
            raise ValueError("표 형식의 데이터를 찾을 수 없습니다.")
        
        # 가장 긴 행의 길이를 기준으로 컬럼 수 결정
        max_cols = max(len(row) for row in rows)
        
        # 모든 행을 동일한 길이로 맞춤 (빈 셀로 채움)
        normalized_rows = []
        for row in rows:
            normalized_row = row + [''] * (max_cols - len(row))
            normalized_rows.append(normalized_row[:max_cols])
        
        # 첫 번째 행을 헤더로 사용 (모두 비어있지 않은 경우)
        if normalized_rows and all(cell.strip() for cell in normalized_rows[0]):
            headers = normalized_rows[0]
            data_rows = normalized_rows[1:]
        else:
            # 헤더가 없는 경우 기본 헤더 생성
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
    # 파일이 업로드되었는지 확인
    if 'file' not in request.files:
        flash('파일이 선택되지 않았습니다.', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    # 파일명이 비어있는지 확인
    if file.filename == '':
        flash('파일이 선택되지 않았습니다.', 'error')
        return redirect(url_for('index'))
    
    # 파일 확장자 검증
    if not allowed_file(file.filename):
        flash('허용되지 않는 파일 형식입니다. (png, jpg, jpeg, gif, bmp, tiff, pdf만 가능)', 'error')
        return redirect(url_for('index'))
    
    try:
        # 안전한 파일명 생성
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
        
        # 추출된 텍스트가 없는 경우
        if not extracted_text.strip():
            flash('텍스트를 추출할 수 없습니다. 이미지에 텍스트가 없거나 인식이 불가능합니다.', 'warning')
            return redirect(url_for('index'))
        
        # 텍스트를 메모리에 저장하여 다운로드 제공
        text_bytes = io.BytesIO()
        text_bytes.write(extracted_text.encode('utf-8'))
        text_bytes.seek(0)
        
        # 원본 파일명에서 확장자를 .txt로 변경
        output_filename = filename.rsplit('.', 1)[0] + '.txt'
        
        return send_file(
            text_bytes,
            mimetype='text/plain',
            as_attachment=True,
            download_name=output_filename
        )
        
    except Exception as e:
        flash(f'처리 중 오류가 발생했습니다: {str(e)}', 'error')
        # 오류 발생 시 임시 파일이 있다면 삭제
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        return redirect(url_for('index'))


@app.route('/convert-to-excel', methods=['POST'])
def convert_pdf_to_excel():
    """PDF 파일을 엑셀 파일로 변환"""
    # 파일이 업로드되었는지 확인
    if 'file' not in request.files:
        flash('파일이 선택되지 않았습니다.', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    # 파일명이 비어있는지 확인
    if file.filename == '':
        flash('파일이 선택되지 않았습니다.', 'error')
        return redirect(url_for('index'))
    
    # PDF 파일인지 확인
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
        
        # 원본 파일명에서 확장자를 .xlsx로 변경
        output_filename = filename.rsplit('.', 1)[0] + '.xlsx'
        
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=output_filename
        )
        
    except Exception as e:
        flash(f'엑셀 변환 중 오류가 발생했습니다: {str(e)}', 'error')
        # 오류 발생 시 임시 파일이 있다면 삭제
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
