# YouTube 다운로더 (Flask 버전)

YouTube 동영상의 오디오와 비디오를 다운로드할 수 있는 웹 애플리케이션입니다.

## 기능

- 웹 브라우저에서 YouTube URL 입력
- 오디오 파일 (.m4a) 다운로드
- 비디오 파일 (.mp4) 다운로드
- 직관적이고 모던한 UI

## 설치 방법

1. 의존성 패키지 설치:
```bash
pip install -r requirements.txt
```

## 실행 방법

1. Flask 서버 실행:
```bash
python app.py
```

2. 웹 브라우저에서 다음 주소로 접속:
```
http://localhost:5000
```

3. YouTube URL을 입력하고 '다운로드 시작' 버튼을 클릭합니다.

4. 다운로드가 완료되면 오디오/비디오 다운로드 링크가 표시됩니다.

## 프로젝트 구조

```
youtube2voice/
├── app.py              # Flask 서버 메인 파일
├── main.py             # 커맨드라인 버전 (기존)
├── requirements.txt    # 필요한 패키지 목록
├── templates/          # HTML 템플릿 폴더
│   └── index.html      # 메인 페이지
├── audio/              # 오디오 파일 저장 폴더
└── video/              # 비디오 파일 저장 폴더
```

## 사용된 기술

- **Flask**: 웹 프레임워크
- **pytubefix**: YouTube 다운로드 라이브러리
- **HTML/CSS/JavaScript**: 프론트엔드

## 주의사항

- 다운로드된 파일은 `audio/` 및 `video/` 폴더에 저장됩니다.
- 저작권이 있는 콘텐츠는 개인적인 용도로만 사용하세요.
