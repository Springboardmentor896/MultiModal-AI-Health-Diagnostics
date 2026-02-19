import cv2
import pytesseract
import numpy as np
import os

def preprocess_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    img = cv2.imread(image_path)
    if img is None:
        return None

    img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh

def extract_text(image_path):
    processed_img = preprocess_image(image_path)
    if processed_img is None:
        return ""

    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
    
    return pytesseract.image_to_string(processed_img, config=custom_config)
