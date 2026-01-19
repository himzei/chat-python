from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from main import text_to_speech_korean
import logging
import os
from pathlib import Path

# Flask 앱 초기화
app = Flask(__name__)
# CORS 설정 (프론트엔드에서 접근 가능하도록)
CORS(app)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/", methods=["GET"])
def index():
    """메인 페이지 (프론트엔드)"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>한글 텍스트 음성 변환</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 40px;
                max-width: 600px;
                width: 100%;
            }
            
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
                font-size: 28px;
            }
            
            .input-group {
                margin-bottom: 20px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                color: #555;
                font-weight: 600;
            }
            
            textarea {
                width: 100%;
                min-height: 150px;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 16px;
                font-family: inherit;
                resize: vertical;
                transition: border-color 0.3s;
            }
            
            textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .char-count {
                text-align: right;
                color: #999;
                font-size: 12px;
                margin-top: 5px;
            }
            
            .button-group {
                display: flex;
                gap: 10px;
                margin-top: 20px;
            }
            
            button {
                flex: 1;
                padding: 15px 30px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .btn-primary:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            .btn-primary:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            
            .btn-secondary {
                background: #f0f0f0;
                color: #333;
            }
            
            .btn-secondary:hover:not(:disabled) {
                background: #e0e0e0;
            }
            
            .btn-secondary:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                display: none;
            }
            
            .message {
                margin-top: 20px;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                font-weight: 500;
                display: none;
            }
            
            .message.success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            
            .message.error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            
            .loading {
                display: none;
                text-align: center;
                margin-top: 20px;
                color: #667eea;
            }
            
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 한글 텍스트 음성 변환</h1>
            
            <div class="input-group">
                <label for="textInput">변환할 텍스트를 입력하세요:</label>
                <textarea id="textInput" placeholder="예: 안녕하세요. 오늘 날씨가 정말 좋네요."></textarea>
                <div class="char-count">
                    <span id="charCount">0</span> / 5000자
                </div>
            </div>
            
            <div class="button-group">
                <button class="btn-primary" id="convertBtn" onclick="convertText()">음성 변환</button>
                <button class="btn-secondary" id="downloadBtn" onclick="downloadFile()" disabled>파일 다운로드</button>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <div>음성을 생성하는 중...</div>
            </div>
            
            <div class="message" id="message"></div>
        </div>
        
        <script>
            let audioFilePath = null;
            
            // 글자 수 카운트
            const textInput = document.getElementById('textInput');
            const charCount = document.getElementById('charCount');
            
            textInput.addEventListener('input', function() {
                const count = this.value.length;
                charCount.textContent = count;
                
                if (count > 5000) {
                    charCount.style.color = '#dc3545';
                } else {
                    charCount.style.color = '#999';
                }
            });
            
            // 음성 변환 함수
            async function convertText() {
                const text = textInput.value.trim();
                
                // 입력 검증
                if (!text) {
                    showMessage('텍스트를 입력해주세요.', 'error');
                    return;
                }
                
                if (text.length > 5000) {
                    showMessage('텍스트는 5000자 이하여야 합니다.', 'error');
                    return;
                }
                
                // UI 상태 변경
                const convertBtn = document.getElementById('convertBtn');
                const downloadBtn = document.getElementById('downloadBtn');
                const loading = document.getElementById('loading');
                const message = document.getElementById('message');
                
                convertBtn.disabled = true;
                downloadBtn.disabled = true;
                downloadBtn.style.display = 'none';
                loading.style.display = 'block';
                message.style.display = 'none';
                
                try {
                    const response = await fetch('/api/text-to-speech', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ text: text })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        audioFilePath = data.file_path;
                        showMessage('음성 변환이 완료되었습니다!', 'success');
                        downloadBtn.disabled = false;
                        downloadBtn.style.display = 'block';
                    } else {
                        showMessage('오류: ' + data.message, 'error');
                    }
                } catch (error) {
                    showMessage('서버 오류가 발생했습니다: ' + error.message, 'error');
                } finally {
                    convertBtn.disabled = false;
                    loading.style.display = 'none';
                }
            }
            
            // 파일 다운로드 함수
            function downloadFile() {
                if (audioFilePath) {
                    window.location.href = '/api/download/' + encodeURIComponent(audioFilePath);
                }
            }
            
            // 메시지 표시 함수
            function showMessage(msg, type) {
                const message = document.getElementById('message');
                message.textContent = msg;
                message.className = 'message ' + type;
                message.style.display = 'block';
            }
            
            // Enter 키로 변환 (Ctrl+Enter)
            textInput.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'Enter') {
                    convertText();
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)


@app.route("/api/text-to-speech", methods=["POST"])
def text_to_speech():
    """
    텍스트를 음성으로 변환하는 API 엔드포인트
    
    요청 형식:
    {
        "text": "변환할 텍스트"
    }
    
    응답 형식:
    {
        "success": true/false,
        "message": "결과 메시지"
    }
    """
    try:
        # 요청 데이터 검증
        if not request.is_json:
            return jsonify({
                "success": False,
                "message": "Content-Type이 application/json이 아닙니다."
            }), 400
        
        data = request.get_json()
        
        # 텍스트 필드 검증
        if "text" not in data:
            return jsonify({
                "success": False,
                "message": "요청에 'text' 필드가 없습니다."
            }), 400
        
        text = data.get("text", "").strip()
        
        # 빈 텍스트 검증
        if not text:
            return jsonify({
                "success": False,
                "message": "텍스트가 비어있습니다."
            }), 400
        
        # 텍스트 길이 제한 (너무 긴 텍스트 방지)
        if len(text) > 1000:
            return jsonify({
                "success": False,
                "message": "텍스트가 너무 깁니다. (최대 1000자)"
            }), 400
        
        # 음성 변환 실행
        logger.info(f"텍스트 음성 변환 요청: {text[:50]}...")
        file_path = text_to_speech_korean(text)
        
        return jsonify({
            "success": True,
            "message": "텍스트가 성공적으로 음성으로 변환되었습니다.",
            "file_path": file_path
        }), 200
        
    except ValueError as ve:
        # 입력값 오류
        logger.error(f"입력값 오류: {ve}")
        return jsonify({
            "success": False,
            "message": str(ve)
        }), 400
        
    except RuntimeError as re:
        # 런타임 오류 (엔진 초기화 실패 등)
        logger.error(f"런타임 오류: {re}")
        return jsonify({
            "success": False,
            "message": f"음성 변환 중 오류가 발생했습니다: {str(re)}"
        }), 500
        
    except Exception as e:
        # 기타 예상치 못한 오류
        logger.error(f"예상치 못한 오류: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"서버 오류가 발생했습니다: {str(e)}"
        }), 500


@app.route("/api/download/<path:filename>", methods=["GET"])
def download_file(filename):
    """
    생성된 음성 파일을 다운로드하는 엔드포인트
    
    Args:
        filename: 다운로드할 파일명 (output/xxx.mp3 형식)
    """
    try:
        # 보안을 위해 파일 경로 검증
        file_path = Path(filename)
        
        # 상위 디렉토리 접근 방지 (output 디렉토리 내의 파일만 허용)
        if not str(file_path).startswith("output"):
            return jsonify({
                "success": False,
                "message": "잘못된 파일 경로입니다."
            }), 400
        
        # 파일 존재 여부 확인
        if not file_path.exists():
            return jsonify({
                "success": False,
                "message": "파일을 찾을 수 없습니다."
            }), 404
        
        # 파일 다운로드
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=f"음성변환_{file_path.stem}.mp3",
            mimetype='audio/mpeg'
        )
        
    except Exception as e:
        logger.error(f"파일 다운로드 오류: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"파일 다운로드 중 오류가 발생했습니다: {str(e)}"
        }), 500


@app.route("/api/test", methods=["GET"])
def test_endpoint():
    """테스트용 엔드포인트"""
    return jsonify({
        "success": True,
        "message": "API가 정상적으로 작동합니다."
    }), 200


@app.errorhandler(404)
def not_found(error):
    """404 오류 처리"""
    return jsonify({
        "success": False,
        "message": "요청한 엔드포인트를 찾을 수 없습니다."
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 오류 처리"""
    return jsonify({
        "success": False,
        "message": "서버 내부 오류가 발생했습니다."
    }), 500


if __name__ == "__main__":
    # 개발 서버 실행
    # production 환경에서는 gunicorn이나 uwsgi 같은 WSGI 서버 사용 권장
    app.run(
        host="0.0.0.0",  # 모든 네트워크 인터페이스에서 접근 가능
        port=5000,       # 포트 번호
        debug=True       # 디버그 모드 (개발 환경에서만 사용)
    )
