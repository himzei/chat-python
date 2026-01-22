import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                                       
image = Image.open("images/test.jpg")


text = pytesseract.image_to_string(image, lang="kor", config="--psm 6")

print(text)