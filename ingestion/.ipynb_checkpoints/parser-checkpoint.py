import os
import json
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image

def parse_input(file, file_type):
    temp_path = f"temp_upload.{file_type}"
    with open(temp_path, "wb") as f:
        f.write(file.getbuffer())

    try:
        if file_type == "pdf":
            return _parse_pdf(temp_path)
        elif file_type == "image":
            return _parse_image(temp_path)
        elif file_type == "csv":
            return _parse_csv(temp_path)
        elif file_type == "json":
            return _parse_json(temp_path)
        else:
            raise ValueError(f"Unsupported file format: {file_type}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
def _parse_pdf(path):
    all_text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)
    return "\n".join(all_text)

def _parse_image(path):
    img = Image.open(path)
    return pytesseract.image_to_string(img)

def _parse_csv(path):
    df = pd.read_csv(path)
    return df.to_string(index=False)

def _parse_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return json.dumps(data, indent=2)