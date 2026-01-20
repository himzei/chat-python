from deep_translator import GoogleTranslator

# 입력 파일과 출력 파일 경로 설정
input_file_path = "input_en.txt"
output_file_path = "output_kr.txt"

# 번역할 목표 언어 설정 (한국어: 'ko', 영어: 'en', 일본어: 'ja')
target_language = "ko"  # 한국어로 번역

# Google 번역기 초기화 (자동 언어 감지 -> 목표 언어)
# 'auto'를 사용하면 소스 언어를 자동으로 감지합니다 (한국어, 영어, 일본어 모두 지원)
translator = GoogleTranslator(source="auto", target=target_language)

try:
    # 입력 파일 읽기
    with open(input_file_path, "r", encoding="utf-8") as input_file:
        text = input_file.read()
    
    # 텍스트 번역 실행
    translated_text = translator.translate(text)
    
    # 번역된 텍스트를 출력 파일에 저장
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(translated_text)
    
    print("번역이 완료되었습니다!")
    
except FileNotFoundError:
    print(f"오류: '{input_file_path}' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")

