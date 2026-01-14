import pdfplumber
import re
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_text_from_image(image_path):
    """Extract text from image using OCR"""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error reading image: {e}")
        return ""

def extract_text(file_path):
    """Auto-detect file type and extract text"""
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
        return extract_text_from_image(file_path)
    else:
        print(f"Unsupported file format: {file_path}")
        return ""

def extract_parameters(text):
    """Extract blood parameters from text"""
    params = {}
    
    patterns = {
        'hemoglobin': r'(?:hemoglobin|hb|hgb)[\s:]*(\d+\.?\d*)',
        'wbc': r'(?:wbc|white blood cell count|total leucocyte count|tlc)[\s:]*(\d+\.?\d*)',
        'rbc': r'(?:rbc|red blood cell count)[\s:]*(\d+\.?\d*)',
        'platelets': r'(?:platelet|plt)[\s:]*(\d+\.?\d*)',
        'glucose': r'(?:glucose|sugar)[\s:]*(\d+\.?\d*)',
    }
    
    text_lower = text.lower()
    for param, pattern in patterns.items():
        match = re.search(pattern, text_lower)
        if match:
            try:
                params[param] = float(match.group(1))
            except ValueError:
                params[param] = None
    
    return params

def validate(params):
    """Basic validation of extracted parameters"""
    validated = {}
    
    ranges = {
        'hemoglobin': (5.0, 20.0),
        'wbc': (1.0, 50.0),
        'rbc': (2.0, 8.0),
        'platelets': (50.0, 1000.0),
        'glucose': (50.0, 500.0),
    }
    
    for param, value in params.items():
        if param in ranges and value is not None:
            min_val, max_val = ranges[param]
            if min_val <= value <= max_val:
                validated[param] = value
            else:
                validated[param] = None
        else:
            validated[param] = value
    
    return validated