from gtts import gTTS
import os
import uuid
from pathlib import Path

# 생성된 음성 파일을 저장할 디렉토리
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)  # 디렉토리가 없으면 생성


def text_to_speech_korean(text: str) -> str:
    """
    주어진 한글 텍스트를 gTTS를 이용해 음성 파일로 변환하고 파일 경로 반환
    
    Args:
        text: 변환할 한글 텍스트
        
    Returns:
        생성된 음성 파일의 경로 (상대 경로)
        
    Raises:
        ValueError: 텍스트가 비어있을 때
        RuntimeError: 음성 변환 중 오류 발생 시
    """
    # 에러 처리: 비어 있는 문자열이면 예외 발생
    if not text or not text.strip():
        raise ValueError("읽을 텍스트가 비어 있습니다.")
    
    # 텍스트 길이 제한 (gTTS는 약 5000자까지 지원)
    if len(text) > 5000:
        raise ValueError("텍스트가 너무 깁니다. (최대 5000자)")
    
    try:
        # 고유한 파일명 생성 (중복 방지)
        file_id = str(uuid.uuid4())
        output_file_path = OUTPUT_DIR / f"{file_id}.mp3"
        
        # gTTS를 사용하여 한글 텍스트를 음성으로 변환
        # lang='ko': 한국어 설정
        tts = gTTS(text=text, lang='ko', slow=False)
        
        # 파일로 저장
        tts.save(str(output_file_path))
        
        # 상대 경로 반환 (다운로드 시 사용)
        return str(output_file_path)
        
    except Exception as e:
        # 파일 생성 실패 시 에러 메시지와 함께 예외 발생
        raise RuntimeError(f"음성 파일 생성 중 오류가 발생했습니다: {str(e)}")


if __name__ == "__main__":
    # 테스트용 문장: 이 부분의 문장을 바꾸어 사용하시면 됩니다.
    sample_text: str = "안녕하세요. 구글 텍스트 투 스피치를 이용한 한글 음성 합성 예제입니다."

    try:
        file_path = text_to_speech_korean(sample_text)
        print(f"음성 파일이 생성되었습니다: {file_path}")
    except Exception as error:
        # 개발 및 디버깅용 에러 출력
        print(f"오류가 발생했습니다: {error}")

