import cv2
import pytesseract
import numpy as np
import os

def preprocess_image(image_path):
    """
    Loads and cleans an image for optimal OCR accuracy.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    img = cv2.imread(image_path)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

    return denoised

def extract_text(image_path):
    """
    Main entry point for OCR. Returns raw string.
    """
    try:
        processed_img = preprocess_image(image_path)
        
        custom_config = r'--oem 3 --psm 6'
        
        raw_text = pytesseract.image_to_string(processed_img, config=custom_config)
        return raw_text
    except Exception as e:
        print(f"Error in extract_text: {e}")
        return ""
