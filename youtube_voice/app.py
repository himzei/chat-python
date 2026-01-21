from flask import Flask, render_template, request, send_file, jsonify
from pytubefix import YouTube
import os
from pathlib import Path

app = Flask(__name__)

# 다운로드 폴더 설정
AUDIO_FOLDER = "audio"
VIDEO_FOLDER = "video"

# 폴더가 없으면 생성
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)


@app.route('/')
def index():
    """메인 페이지 렌더링"""
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
    """YouTube URL을 받아서 오디오와 비디오 다운로드"""
    try:
        # URL 가져오기
        url = request.json.get('url')
        
        # URL 유효성 검사
        if not url:
            return jsonify({'error': 'URL을 입력해주세요.'}), 400
        
        # YouTube 객체 생성
        yt = YouTube(url)
        video_title = yt.title
        
        # 오디오 스트림 다운로드
        audio_stream = yt.streams.filter(only_audio=True).first()
        if audio_stream is None:
            return jsonify({'error': '오디오 스트림을 찾지 못했습니다.'}), 404
        
        audio_file_path = audio_stream.download(output_path=AUDIO_FOLDER)
        audio_filename = os.path.basename(audio_file_path)
        
        # 비디오 스트림 다운로드
        video_stream = yt.streams.filter(only_video=True).first()
        if video_stream is None:
            return jsonify({'error': '비디오 스트림을 찾지 못했습니다.'}), 404
        
        video_file_path = video_stream.download(output_path=VIDEO_FOLDER)
        video_filename = os.path.basename(video_file_path)
        
        return jsonify({
            'success': True,
            'title': video_title,
            'audio_file': audio_filename,
            'video_file': video_filename
        })
        
    except Exception as error:
        return jsonify({'error': f'다운로드 중 오류가 발생했습니다: {str(error)}'}), 500


@app.route('/download-file/<file_type>/<filename>')
def download_file(file_type, filename):
    """다운로드된 파일을 사용자에게 제공"""
    try:
        # 파일 타입에 따라 폴더 선택
        if file_type == 'audio':
            folder = AUDIO_FOLDER
        elif file_type == 'video':
            folder = VIDEO_FOLDER
        else:
            return jsonify({'error': '잘못된 파일 타입입니다.'}), 400
        
        file_path = os.path.join(folder, filename)
        
        # 파일 존재 여부 확인
        if not os.path.exists(file_path):
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as error:
        return jsonify({'error': f'파일 다운로드 중 오류가 발생했습니다: {str(error)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
