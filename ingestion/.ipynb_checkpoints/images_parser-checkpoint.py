import cv2
import pytesseract
import numpy as np
import os

def preprocess_image(image_path):
    """
    Advanced preprocessing to handle medical scans.
    1. Upscales image (fixes missing decimals).
    2. Thresholds to black/white (fixes shadows).
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    # Load image
    img = cv2.imread(image_path)
    if img is None:
        return None

    # 1. UPSCALING (Critical for decimals like 4.5 vs 45)
    # We resize to 2x or 3x depending on resolution, but 2x is usually safe.
    img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)

    # 2. Convert to Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Denoising (Removes salt-and-pepper noise from scans)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

    # 4. Binarization (Otsu's Threshold)
    # This turns everything into strict Black (Text) and White (Background)
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh

def extract_text(image_path):
    """
    Extracts raw text with layout preservation.
    """
    processed_img = preprocess_image(image_path)
    if processed_img is None:
        return ""

    # --psm 6: Assume a single uniform block of text (Table mode)
    # preserve_interword_spaces: Helps separate 'Value' from 'Unit' columns
    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
    
    return pytesseract.image_to_string(processed_img, config=custom_config)
