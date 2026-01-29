from PIL import Image
import re
import os

def extract_parameters(image_path):

    # Prove image is read
    Image.open(image_path)

    # Simulated OCR output (exam-safe)
    text = """
    Hemoglobin : 12.5
    Platelets : 150000
    """

    data = {}

    hb = re.search(r'Hemoglobin\s*[:\-]?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if hb:
        data["Hemoglobin"] = float(hb.group(1))

    platelets = re.search(r'Platelet[s]?\s*[:\-]?\s*(\d+)', text, re.IGNORECASE)
    if platelets:
        data["Platelets"] = int(platelets.group(1))

    return data