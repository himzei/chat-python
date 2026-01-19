from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import qrcode
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 세션 보안을 위한 시크릿 키

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    메인 페이지: 텍스트 입력 폼을 표시하고 QR 코드 생성 요청을 처리
    """
    if request.method == 'POST':
        # 폼에서 입력된 텍스트 가져오기
        input_text = request.form.get('qr_data', '').strip()
        
        # 입력값 검증
        if not input_text:
            flash('텍스트를 입력해주세요.', 'error')
            return render_template('index.html')
        
        try:
            # QR 코드 생성 (main.py의 로직 참조)
            img = qrcode.make(input_text)
            
            # 파일명 생성 (타임스탬프 포함하여 중복 방지)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'qrcode_{timestamp}.png'
            
            # 현재 폴더에 QR 코드 이미지 저장
            filepath = os.path.join(os.getcwd(), filename)
            img.save(filepath)
            
            flash(f'QR 코드가 성공적으로 생성되었습니다: {filename}', 'success')
            return render_template('index.html', qr_filename=filename)
            
        except Exception as e:
            # 에러 발생 시 사용자에게 알림
            flash(f'QR 코드 생성 중 오류가 발생했습니다: {str(e)}', 'error')
            return render_template('index.html')
    
    # GET 요청 시 폼 페이지 표시
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    """
    생성된 QR 코드 이미지 파일 다운로드
    """
    try:
        filepath = os.path.join(os.getcwd(), filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            flash('파일을 찾을 수 없습니다.', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'파일 다운로드 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Flask 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5000)
