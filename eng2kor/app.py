from flask import Flask, request, render_template, send_file, jsonify
from deep_translator import GoogleTranslator
import os
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 최대 파일 크기 16MB
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()  # 임시 폴더 사용

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    """파일 확장자가 허용된 형식인지 확인"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_language_code(language):
    """언어 이름을 언어 코드로 변환"""
    language_map = {
        '한국어': 'ko',
        '영어': 'en',
        '일본어': 'ja'
    }
    return language_map.get(language, 'ko')

@app.route('/')
def index():
    """메인 페이지 렌더링"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """파일 업로드 및 번역 처리"""
    try:
        # 파일이 요청에 포함되어 있는지 확인
        if 'file' not in request.files:
            return jsonify({'error': '파일이 업로드되지 않았습니다.'}), 400
        
        file = request.files['file']
        target_language = request.form.get('language', '한국어')
        
        # 파일이 선택되었는지 확인
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
        
        # 파일 확장자 확인
        if not allowed_file(file.filename):
            return jsonify({'error': 'txt 파일만 업로드 가능합니다.'}), 400
        
        # 파일 읽기
        text = file.read().decode('utf-8')
        
        # 텍스트가 비어있는지 확인
        if not text.strip():
            return jsonify({'error': '파일 내용이 비어있습니다.'}), 400
        
        # 목표 언어 코드 가져오기
        target_lang_code = get_language_code(target_language)
        
        # 소스 언어 자동 감지 (한국어, 영어, 일본어 모두 지원)
        # 'auto'를 사용하면 Google Translator가 자동으로 소스 언어를 감지합니다
        source_language = 'auto'
        
        # 번역기 초기화 (자동 언어 감지 사용)
        translator = GoogleTranslator(source=source_language, target=target_lang_code)
        
        # 텍스트 번역 실행
        translated_text = translator.translate(text)
        
        # 파일명 생성 (원본 파일명 + 언어) - secure_filename을 먼저 적용하여 일관성 유지
        original_filename = secure_filename(file.filename)
        filename_without_ext = os.path.splitext(original_filename)[0]
        # 언어명도 안전한 형식으로 변환 (한글 -> 영문 코드)
        language_safe = target_lang_code
        translated_filename = f"{filename_without_ext}_translated_{language_safe}.txt"
        translated_filename = secure_filename(translated_filename)  # 최종 파일명도 안전하게 처리
        
        # 번역된 파일을 최종 경로에 저장
        final_path = os.path.join(app.config['UPLOAD_FOLDER'], translated_filename)
        with open(final_path, 'w', encoding='utf-8') as output_file:
            output_file.write(translated_text)
        
        return jsonify({
            'success': True,
            'filename': translated_filename,
            'download_url': f'/download/{translated_filename}',
            'preview': translated_text[:200] + ('...' if len(translated_text) > 200 else '')
        })
        
    except UnicodeDecodeError:
        return jsonify({'error': '파일 인코딩 오류: UTF-8 형식의 파일만 지원합니다.'}), 400
    except Exception as e:
        return jsonify({'error': f'번역 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """번역된 파일 다운로드"""
    try:
        # 파일명을 안전하게 처리
        safe_filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        # 경로 정규화 (Windows 경로 문제 해결)
        file_path = os.path.normpath(file_path)
        
        # 파일이 존재하는지 확인
        if not os.path.exists(file_path):
            # 디버깅을 위한 로그 (운영 환경에서는 제거 가능)
            import logging
            logging.warning(f'파일을 찾을 수 없음: {file_path}')
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='text/plain; charset=utf-8'
        )
        
    except Exception as e:
        import logging
        logging.error(f'다운로드 오류: {str(e)}')
        return jsonify({'error': f'다운로드 중 오류가 발생했습니다: {str(e)}'}), 500

if __name__ == '__main__':
    # templates 폴더가 없으면 생성
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
