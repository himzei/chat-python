from flask import Flask, request, jsonify, render_template
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 최대 파일 크기 16MB

# 감정 분석 모델 로드 (앱 시작 시 한 번만 로드)
print("감정 분석 모델을 로드하는 중...")
try:
    tokenizer = AutoTokenizer.from_pretrained("beomi/kcbert-base")
    model = AutoModelForSequenceClassification.from_pretrained("beomi/kcbert-base", num_labels=2)
    print("감정 분석 모델 로드 완료!")
except Exception as e:
    print(f"감정 분석 모델 로드 실패: {str(e)}")
    tokenizer = None
    model = None


def analyze_sentiment(text):
    """
    텍스트의 감정을 분석하는 함수
    
    Args:
        text: 분석할 텍스트 문자열
    
    Returns:
        dict: 감정 분석 결과 (polarity, positive_prob, negative_prob)
    """
    # 모델이 로드되지 않은 경우 에러 반환
    if tokenizer is None or model is None:
        return {
            'error': '감정 분석 모델이 로드되지 않았습니다.'
        }
    
    try:
        # 텍스트가 비어있는지 확인
        if not text or not text.strip():
            return {
                'error': '분석할 텍스트가 비어있습니다.'
            }
        
        # 토큰화 및 모델 입력 준비
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        # 감정 분석 수행
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)
        
        # 모델 라벨 확인: 실제로는 0이 긍정, 1이 부정일 수 있음
        # 라벨이 반대로 되어 있어서 수정함
        positive_score = probs[0][0].item()   # 0번 인덱스가 실제로는 긍정
        negative_score = probs[0][1].item()    # 1번 인덱스가 실제로는 부정
        polarity = (positive_score - 0.5) * 2  # -1(부정) ~ 1(긍정)로 변환
        
        return {
            'polarity': round(polarity, 3),           # 극성 점수 (-1 ~ 1)
            'positive_prob': round(positive_score, 3),  # 긍정 확률 (0 ~ 1)
            'negative_prob': round(negative_score, 3),   # 부정 확률 (0 ~ 1)
            'sentiment': '긍정' if positive_score > 0.5 else '부정'  # 감정 판정
        }
    
    except Exception as e:
        return {
            'error': f'감정 분석 중 오류 발생: {str(e)}'
        }


@app.route('/')
def index():
    """메인 페이지 - 프론트엔드 UI 제공"""
    return render_template('sentiment.html')


@app.route('/api')
def api_info():
    """API 사용 안내 엔드포인트"""
    return jsonify({
        'message': '감정 분석 API 서버',
        'endpoints': {
            '/analyze': 'POST - 텍스트를 JSON으로 전송하여 감정 분석',
            '/upload': 'POST - 텍스트 파일을 업로드하여 감정 분석'
        },
        'example': {
            'analyze': {
                'method': 'POST',
                'url': '/analyze',
                'body': {'text': '오늘 정말 기분이 좋아요!'}
            },
            'upload': {
                'method': 'POST',
                'url': '/upload',
                'form-data': {'file': 'your_file.txt'}
            }
        }
    })


@app.route('/analyze', methods=['POST'])
def analyze_text():
    """
    텍스트를 입력받아 감정 분석을 수행하는 엔드포인트
    
    Request Body (JSON):
        {
            "text": "분석할 텍스트"
        }
    
    Returns:
        JSON: 감정 분석 결과
    """
    try:
        # JSON 데이터 확인
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': '요청 데이터가 없습니다. JSON 형식으로 {"text": "분석할 텍스트"}를 전송해주세요.'
            }), 400
        
        if 'text' not in data:
            return jsonify({
                'error': '텍스트가 제공되지 않았습니다. "text" 필드를 포함해주세요.'
            }), 400
        
        text = data['text'].strip()
        
        # 텍스트가 비어있는지 확인
        if not text:
            return jsonify({
                'error': '텍스트가 비어있습니다.'
            }), 400
        
        # 감정 분석 수행
        result = analyze_sentiment(text)
        
        # 에러가 있는 경우
        if 'error' in result:
            return jsonify(result), 500
        
        # 성공 응답
        return jsonify({
            'success': True,
            'text': text,
            'result': result
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'처리 중 오류가 발생했습니다: {str(e)}'
        }), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    텍스트 파일을 업로드하여 감정 분석을 수행하는 엔드포인트
    
    Request:
        form-data with 'file' field containing a text file
    
    Returns:
        JSON: 감정 분석 결과
    """
    try:
        # 파일 업로드 확인
        if 'file' not in request.files:
            return jsonify({
                'error': '파일이 업로드되지 않았습니다. "file" 필드로 파일을 전송해주세요.'
            }), 400
        
        file = request.files['file']
        
        # 파일명 확인
        if file.filename == '':
            return jsonify({
                'error': '파일이 선택되지 않았습니다.'
            }), 400
        
        # 파일 확장자 확인 (텍스트 파일만 허용)
        allowed_extensions = {'.txt', '.text', '.md', '.csv'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                'error': f'텍스트 파일(.txt, .text, .md, .csv)만 업로드 가능합니다. 현재 파일: {file_ext}'
            }), 400
        
        # 파일 읽기 (인코딩 자동 감지)
        try:
            # UTF-8 인코딩으로 시도
            text_content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            # UTF-8 실패 시 CP949 (한글 윈도우 기본 인코딩) 시도
            file.seek(0)  # 파일 포인터 초기화
            try:
                text_content = file.read().decode('cp949')
            except UnicodeDecodeError:
                return jsonify({
                    'error': '파일 인코딩을 읽을 수 없습니다. UTF-8 또는 CP949 인코딩을 사용해주세요.'
                }), 400
        
        # 텍스트가 비어있는지 확인
        if not text_content.strip():
            return jsonify({
                'error': '파일이 비어있습니다.'
            }), 400
        
        # 감정 분석 수행
        result = analyze_sentiment(text_content)
        
        # 에러가 있는 경우
        if 'error' in result:
            return jsonify(result), 500
        
        # 성공 응답
        return jsonify({
            'success': True,
            'filename': file.filename,
            'text_length': len(text_content),
            'result': result
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'처리 중 오류가 발생했습니다: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("=" * 50)
    print("감정 분석 서버가 시작됩니다...")
    print("=" * 50)
    print("\n사용 가능한 엔드포인트:")
    print("  1. GET  /          - API 사용 안내")
    print("  2. POST /analyze   - 텍스트 감정 분석")
    print("  3. POST /upload    - 파일 업로드 감정 분석")
    print("\n서버 주소: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
