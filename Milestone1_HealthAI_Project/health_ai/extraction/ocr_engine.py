import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\manog\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

def extract_text(image_path):
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)
