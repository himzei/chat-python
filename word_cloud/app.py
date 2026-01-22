from flask import Flask, request, render_template, send_file, jsonify
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # GUI 백엔드 없이 사용하기 위해
import io
import os
from datetime import datetime
import uuid
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # 업로드된 파일 저장 폴더
app.config['OUTPUT_FOLDER'] = 'outputs'   # 생성된 워드클라우드 이미지 저장 폴더
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 최대 파일 크기 16MB

# 필요한 폴더 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# 한글 폰트 경로 설정 (Windows 기본 폰트)
FONT_PATH = 'C:/Windows/Fonts/malgun.ttf'

# 감정 분석 모델 로드 (앱 시작 시 한 번만 로드)
print("감정 분석 모델을 로드하는 중...")
try:
    sentiment_tokenizer = AutoTokenizer.from_pretrained("beomi/kcbert-base")
    sentiment_model = AutoModelForSequenceClassification.from_pretrained("beomi/kcbert-base", num_labels=2)
    print("감정 분석 모델 로드 완료!")
except Exception as e:
    print(f"감정 분석 모델 로드 실패: {str(e)}")
    sentiment_tokenizer = None
    sentiment_model = None

def crawl_website(url):
    """
    웹사이트 URL에서 텍스트를 크롤링하는 함수
    
    Args:
        url: 크롤링할 웹사이트 URL
    
    Returns:
        str: 추출된 텍스트 내용
    """
    try:
        # URL 유효성 검사
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = 'https://' + url
        
        # HTTP 요청 헤더 설정 (봇 차단 방지)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 웹페이지 요청 (타임아웃 10초)
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # HTTP 오류 확인
        
        # 인코딩 설정
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding or 'utf-8'
        
        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 불필요한 태그 제거 (script, style, meta 등)
        for tag in soup(['script', 'style', 'meta', 'link', 'noscript', 'iframe', 'svg']):
            tag.decompose()
        
        # 텍스트 추출
        text = soup.get_text(separator=' ', strip=True)
        
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        # 텍스트가 비어있는지 확인
        if not text.strip():
            raise Exception('웹페이지에서 텍스트를 추출할 수 없습니다.')
        
        return text.strip()
    
    except requests.exceptions.Timeout:
        raise Exception('웹페이지 요청 시간이 초과되었습니다.')
    except requests.exceptions.ConnectionError:
        raise Exception('웹페이지에 연결할 수 없습니다. URL을 확인해주세요.')
    except requests.exceptions.HTTPError as e:
        raise Exception(f'HTTP 오류 발생: {e.response.status_code}')
    except Exception as e:
        raise Exception(f'웹 크롤링 중 오류 발생: {str(e)}')

def analyze_sentiment(text):
    """
    텍스트의 감정을 분석하는 함수
    
    Args:
        text: 분석할 텍스트
    
    Returns:
        dict: 감정 분석 결과 (polarity, positive_prob, negative_prob)
    """
    # 모델이 로드되지 않은 경우 None 반환
    if sentiment_tokenizer is None or sentiment_model is None:
        return None
    
    try:
        # 텍스트가 너무 긴 경우 앞부분만 사용 (512 토큰 제한)
        # 실제로는 문장 단위로 나누어 분석하는 것이 더 정확하지만, 
        # 간단하게 앞부분만 사용
        max_length = 500  # 토큰화 전 문자 수 제한
        if len(text) > max_length:
            text = text[:max_length]
        
        # 토큰화 및 모델 입력 준비
        inputs = sentiment_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        # 감정 분석 수행
        with torch.no_grad():
            outputs = sentiment_model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)
        
        # 0: 부정, 1: 긍정
        positive_prob = probs[0][1].item()  # 긍정 확률
        negative_prob = probs[0][0].item()  # 부정 확률
        polarity = (positive_prob - 0.5) * 2  # -1(부정) ~ 1(긍정)로 변환
        
        return {
            'polarity': round(polarity, 3),
            'positive_prob': round(positive_prob, 3),
            'negative_prob': round(negative_prob, 3)
        }
    
    except Exception as e:
        # 감정 분석 실패 시 None 반환 (워드클라우드 생성은 계속 진행)
        print(f"감정 분석 중 오류 발생: {str(e)}")
        return None

def create_wordcloud(text, width=800, height=400):
    """
    텍스트로부터 워드클라우드 이미지를 생성하는 함수
    
    Args:
        text: 워드클라우드를 생성할 텍스트
        width: 이미지 너비 (기본값: 800)
        height: 이미지 높이 (기본값: 400)
    
    Returns:
        BytesIO: 워드클라우드 이미지 데이터
    """
    try:
        # 워드클라우드 생성
        wordcloud = WordCloud(
            width=width,
            height=height,
            background_color='white',
            colormap="plasma",
            font_path=FONT_PATH,  # 한글 폰트 경로 지정
            max_words=100,  # 최대 단어 개수
            relative_scaling=0.5  # 단어 크기 비율 조정
        ).generate(text)
        
        # 이미지로 변환
        plt.figure(figsize=(width/100, height/100))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout(pad=0)
        
        # BytesIO에 이미지 저장
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()  # 메모리 해제
        
        img_buffer.seek(0)
        return img_buffer
    
    except Exception as e:
        raise Exception(f"워드클라우드 생성 중 오류 발생: {str(e)}")

@app.route('/')
def index():
    """메인 페이지 - 파일 업로드 폼"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    텍스트 파일을 업로드하고 워드클라우드를 생성하는 엔드포인트
    """
    try:
        # 파일 업로드 확인
        if 'file' not in request.files:
            return jsonify({'error': '파일이 업로드되지 않았습니다.'}), 400
        
        file = request.files['file']
        
        # 파일명 확인
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
        
        # 파일 확장자 확인 (텍스트 파일만 허용)
        allowed_extensions = {'.txt', '.text', '.md'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': '텍스트 파일(.txt, .text, .md)만 업로드 가능합니다.'}), 400
        
        # 파일 읽기
        try:
            # UTF-8 인코딩으로 시도
            text_content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            # UTF-8 실패 시 CP949 (한글 윈도우 기본 인코딩) 시도
            file.seek(0)  # 파일 포인터 초기화
            try:
                text_content = file.read().decode('cp949')
            except UnicodeDecodeError:
                return jsonify({'error': '파일 인코딩을 읽을 수 없습니다. UTF-8 또는 CP949 인코딩을 사용해주세요.'}), 400
        
        # 텍스트가 비어있는지 확인
        if not text_content.strip():
            return jsonify({'error': '파일이 비어있습니다.'}), 400
        
        # 워드클라우드 생성
        img_buffer = create_wordcloud(text_content)
        
        # 감정 분석 수행
        sentiment_result = analyze_sentiment(text_content)
        
        # 고유한 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f'wordcloud_{timestamp}_{unique_id}.png'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # 이미지 파일로 저장
        with open(output_path, 'wb') as f:
            f.write(img_buffer.read())
        
        # 응답 데이터 준비
        response_data = {
            'success': True,
            'message': '워드클라우드가 성공적으로 생성되었습니다.',
            'download_url': f'/download/{output_filename}',
            'filename': output_filename
        }
        
        # 감정 분석 결과가 있으면 추가
        if sentiment_result:
            response_data['sentiment'] = sentiment_result
        
        # 다운로드 링크 반환
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/crawl', methods=['POST'])
def crawl_url():
    """
    웹사이트 URL을 크롤링하고 워드클라우드를 생성하는 엔드포인트
    """
    try:
        # JSON 데이터 확인
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL이 제공되지 않았습니다.'}), 400
        
        url = data['url'].strip()
        
        # URL이 비어있는지 확인
        if not url:
            return jsonify({'error': 'URL을 입력해주세요.'}), 400
        
        # 웹사이트 크롤링
        text_content = crawl_website(url)
        
        # 텍스트가 비어있는지 확인
        if not text_content.strip():
            return jsonify({'error': '웹페이지에서 텍스트를 추출할 수 없습니다.'}), 400
        
        # 워드클라우드 생성
        img_buffer = create_wordcloud(text_content)
        
        # 감정 분석 수행
        sentiment_result = analyze_sentiment(text_content)
        
        # 고유한 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f'wordcloud_{timestamp}_{unique_id}.png'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # 이미지 파일로 저장
        with open(output_path, 'wb') as f:
            f.write(img_buffer.read())
        
        # 응답 데이터 준비
        response_data = {
            'success': True,
            'message': '워드클라우드가 성공적으로 생성되었습니다.',
            'download_url': f'/download/{output_filename}',
            'filename': output_filename
        }
        
        # 감정 분석 결과가 있으면 추가
        if sentiment_result:
            response_data['sentiment'] = sentiment_result
        
        # 다운로드 링크 반환
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """
    생성된 워드클라우드 이미지를 다운로드하는 엔드포인트
    """
    try:
        # 파일 경로 생성
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        # 파일 존재 확인
        if not os.path.exists(file_path):
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
        
        # 파일 다운로드
        return send_file(
            file_path,
            mimetype='image/png',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': f'다운로드 중 오류가 발생했습니다: {str(e)}'}), 500

if __name__ == '__main__':
    print("워드클라우드 생성 서버가 시작됩니다...")
    print("브라우저에서 http://localhost:5000 을 열어주세요.")
    app.run(debug=True, host='0.0.0.0', port=5000)
