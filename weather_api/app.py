from flask import Flask, render_template, jsonify, request
import requests
import json

app = Flask(__name__)

# OpenWeatherMap API 설정
API_KEY = "532b43b6e382f182b0c43695a34f48ae"

@app.route('/')
def index():
    """메인 페이지 렌더링"""
    return render_template('index.html')

@app.route('/api/weather')
def get_weather():
    """
    위도와 경도를 받아 날씨 정보를 반환하는 API 엔드포인트
    쿼리 파라미터: lat (위도), lon (경도)
    """
    try:
        # 클라이언트로부터 위도, 경도 받기
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        
        if lat is None or lon is None:
            return jsonify({'error': '위도와 경도가 필요합니다.'}), 400
        
        # OpenWeatherMap API 호출 (현재 날씨)
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=kr"
        weather_response = requests.get(weather_url)
        
        if weather_response.status_code != 200:
            return jsonify({'error': '날씨 정보를 가져올 수 없습니다.'}), weather_response.status_code
        
        weather_data = weather_response.json()
        
        # 필요한 정보 추출 및 가공
        result = {
            'location': weather_data.get('name', '알 수 없음'),
            'description': weather_data['weather'][0]['description'],
            'icon': weather_data['weather'][0]['icon'],
            'temp': round(weather_data['main']['temp'], 1),
            'feels_like': round(weather_data['main']['feels_like'], 1),
            'humidity': weather_data['main']['humidity'],
            'pressure': weather_data['main']['pressure'],
            'wind_speed': round(weather_data['wind']['speed'], 1),
            'clouds': weather_data['clouds']['all'],  # 구름량 (%)
            'temp_min': round(weather_data['main']['temp_min'], 1),
            'temp_max': round(weather_data['main']['temp_max'], 1),
            'visibility': weather_data.get('visibility', 0) / 1000,  # km 단위로 변환
        }
        
        # 비 정보가 있으면 추가 (최근 1시간 강수량)
        if 'rain' in weather_data and '1h' in weather_data['rain']:
            result['rain'] = weather_data['rain']['1h']
        else:
            result['rain'] = 0
            
        # 눈 정보가 있으면 추가
        if 'snow' in weather_data and '1h' in weather_data['snow']:
            result['snow'] = weather_data['snow']['1h']
        else:
            result['snow'] = 0
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': f'서버 오류: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
