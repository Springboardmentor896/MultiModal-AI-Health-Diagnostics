import pdfplumber
import re
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

def extract_text_from_pdf(pdf_path):
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
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error reading image: {e}")
        return ""

def extract_text(file_path):
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
        return extract_text_from_image(file_path)
    else:
        print(f"Unsupported file format: {file_path}")
        return ""

def extract_parameters(text):
    params = {}
    
    patterns = {
        'hemoglobin': r'(?:hemoglobin|hb|hgb)[\s:]*(\d{1,2}\.?\d{0,2})',
        'wbc': r'(?:wbc|white blood cell|total leucocyte|tlc)[\s:]*(\d{1,2}\.?\d{0,2})',
        'rbc': r'(?:rbc|red blood cell)[\s:]*(\d{1,2}\.?\d{0,2})',
        'platelets': r'(?:platelet|plt)[\s:]*(\d{1,4}\.?\d{0,2})',
        'hematocrit': r'(?:hematocrit|hct|pcv)[\s:]*(\d{1,3}\.?\d{0,2})',
        'mcv': r'(?:mcv|mean corpuscular volume)[\s:]*(\d{1,3}\.?\d{0,2})',
        'mch': r'(?:mch|mean corpuscular hemoglobin)[\s:]*(\d{1,2}\.?\d{0,2})',
        'mchc': r'(?:mchc|mean corpuscular hemoglobin concentration)[\s:]*(\d{1,2}\.?\d{0,2})',
        'rdw': r'(?:rdw|red cell distribution width)[\s:]*(\d{1,2}\.?\d{0,2})',
        'glucose': r'(?:glucose|sugar|fbs|fasting blood sugar)[\s:]*(\d{1,3}\.?\d{0,2})',
        'triglycerides': r'(?:triglyceride|tg)[\s:]*(\d{1,4}\.?\d{0,2})',
        'cholesterol': r'(?:total cholesterol|cholesterol)[\s:]*(\d{1,4}\.?\d{0,2})',
        'hdl': r'(?:hdl|high density)[\s:]*(\d{1,4}\.?\d{0,2})',
        'ldl': r'(?:ldl|low density)[\s:]*(\d{1,4}\.?\d{0,2})',
        'creatinine': r'(?:creatinine|cre)[\s:]*(\d{1,2}\.?\d{0,2})',
        'bun': r'(?:bun|urea|blood urea nitrogen)[\s:]*(\d{1,3}\.?\d{0,2})',
        'calcium': r'(?:calcium|ca)[\s:]*(\d{1,2}\.?\d{0,2})',
        'potassium': r'(?:potassium|k\+)[\s:]*(\d{1,2}\.?\d{0,2})',
        'sodium': r'(?:sodium|na\+)[\s:]*(\d{1,4}\.?\d{0,2})',
        'albumin': r'(?:albumin)[\s:]*(\d{1,2}\.?\d{0,2})',
        'bilirubin': r'(?:bilirubin|bili)[\s:]*(\d{1,2}\.?\d{0,2})',
        'alt': r'(?:alt|sgpt)[\s:]*(\d{1,4}\.?\d{0,2})',
        'ast': r'(?:ast|sgot)[\s:]*(\d{1,4}\.?\d{0,2})',
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
    validated = {}
    
    ranges = {
        'hemoglobin': (5.0, 20.0),
        'wbc': (1.0, 50.0),
        'rbc': (2.0, 8.0),
        'platelets': (50.0, 1000.0),
        'hematocrit': (10.0, 60.0),
        'mcv': (50.0, 150.0),
        'mch': (20.0, 40.0),
        'mchc': (25.0, 40.0),
        'rdw': (10.0, 20.0),
        'glucose': (50.0, 500.0),
        'triglycerides': (0.0, 500.0),
        'cholesterol': (0.0, 400.0),
        'hdl': (0.0, 300.0),
        'ldl': (0.0, 300.0),
        'creatinine': (0.1, 5.0),
        'bun': (5.0, 100.0),
        'calcium': (5.0, 12.0),
        'potassium': (2.0, 7.0),
        'sodium': (120.0, 160.0),
        'albumin': (2.0, 6.0),
        'bilirubin': (0.0, 5.0),
        'alt': (1.0, 100.0),
        'ast': (1.0, 100.0),
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