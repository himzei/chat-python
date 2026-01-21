import pytesseract 
from PIL import Image

# Tesseract 실행 파일 경로 설정
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 이미지 파일 열기
image = Image.open("image.jpg")

# 한글 OCR 수행 (image_to_string으로 순수 텍스트 추출)
# config 옵션: PSM 6은 단일 텍스트 블록으로 인식
text = pytesseract.image_to_string(image, lang="kor", config="--psm 6")

# 결과 출력
print(text)