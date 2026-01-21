# 날씨 정보 앱 🌤️

현재 위치의 실시간 날씨 정보를 보여주는 Flask 기반 웹 애플리케이션입니다.

## 주요 기능

- 📍 현재 위치 자동 감지
- 🌡️ 실시간 온도 및 체감 온도
- 💧 습도 정보
- 💨 풍속 정보
- ☁️ 구름량
- 🌧️ 강수량 (1시간)
- 👁️ 가시거리
- 🎚️ 기압
- 📊 최저/최고 기온

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## 실행 방법

1. Flask 서버 실행:
```bash
python app.py
```

2. 브라우저에서 접속:
```
http://localhost:5000
```

3. 위치 권한을 허용하면 자동으로 현재 위치의 날씨 정보가 표시됩니다.

## 기술 스택

- **Backend**: Flask
- **API**: OpenWeatherMap API
- **Frontend**: HTML, CSS, JavaScript
- **위치 정보**: Geolocation API

## 참고사항

- 브라우저에서 위치 권한을 허용해야 정상적으로 작동합니다.
- HTTPS 환경에서 위치 정보가 더 정확하게 작동합니다.
- main.py는 기존 테스트용 스크립트이며, 웹 앱은 app.py로 실행됩니다.
