from deep_translator import GoogleTranslator

# 입력 파일과 출력 파일 경로 설정
input_file_path = "input_en.txt"
output_file_path = "output_kr.txt"

# Google 번역기 초기화 (영어 -> 한국어)
translator = GoogleTranslator(source="en", target="ko")

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

