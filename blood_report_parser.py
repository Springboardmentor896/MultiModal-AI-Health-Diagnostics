import pdfplumber
import re
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

NUMBER_PATTERN = r"(\d{1,5}(?:,\d{3})*(?:\.\d{1,2})?)"

def _normalize_text(raw: str) -> str:
    return (
        raw.lower()
        .replace("mgldl", "mg/dl")
        .replace("mg/dl.", "mg/dl")
        .replace("mail", "mg/dl")
        .replace("ail", "g/dl")
        .replace("lakhsicumm", " lakhs ")
        .replace("cells/cumm", " cells cumm ")
        .replace("cellscumm", " cells cumm ")
        .replace("plateletcount", "platelet count")
        .replace("total leukocyte count", "total leukocyte")
        .replace("total leucocyte count", "total leucocyte")
        .replace("lac/cumm", " lac ")
        .replace("lakh/cumm", " lakh ")
        .replace("lakhs/cumm", " lakhs ")
        .replace("lakh / cumm", " lakh ")
        .replace("lakhs / cumm", " lakhs ")
        .replace("lac / cumm", " lac ")
    )


def _parse_numeric(value_str: str) -> float:
    return float(value_str.replace(",", ""))


def _apply_scaling(param: str, value: float, unit_word) -> float:
    lakh_words = {"lakh", "lakhs", "lac", "lacs", "million", "millions"}

    if param == "platelets":
        if unit_word and unit_word in lakh_words:
            platelet_lakh = value
        else:
            if value >= 20_000:  
                platelet_lakh = value / 100_000.0
            else:
                platelet_lakh = value
                if platelet_lakh > 10:
                    platelet_lakh = platelet_lakh / 10.0
                if platelet_lakh > 10:
                    platelet_lakh = platelet_lakh / 10.0
        return platelet_lakh

    if param == "wbc":
        if unit_word and unit_word in lakh_words:
            return value * 100_000
        return value

    return value


def _postprocess_value(param: str, value: float) -> float:
    if param == "hemoglobin" and value > 25:
        value = value / 10.0
    if param == "cholesterol" and value > 800:
        value = value / 10.0
    if param == "glucose" and value > 600:
        value = value / 10.0
    return value

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

    number = NUMBER_PATTERN
    count_unit = r"\s*(lakh|lakhs|lac|lacs|million|millions)?"

    patterns = {
        'hemoglobin': rf'(?:hemoglobin|hb|hgb)[^\d]*{number}',
        'wbc': rf'(?:wbc|white blood cell|total leucocyte|total leukocyte|tlc)[^\d]*{number}{count_unit}',
        'rbc': rf'(?:rbc|red blood cell)[^\d]*{number}',
        'platelets': rf'(?:platelet|plt)[^\d]*{number}{count_unit}',
        'hematocrit': rf'(?:hematocrit|hct|pcv)[^\d]*{number}',
        'mcv': rf'(?:mcv|mean corpuscular volume)[^\d]*{number}',
        'mch': rf'(?:mch|mean corpuscular hemoglobin)[^\d]*{number}',
        'mchc': rf'(?:mchc|mean corpuscular hemoglobin concentration)[^\d]*{number}',
        'rdw': rf'(?:rdw|red cell distribution width)[^\d]*{number}',
        'glucose': rf'(?:glucose|sugar|fbs|fasting blood sugar)[^\d]*{number}',
        'triglycerides': rf'(?:triglyceride|tg)[^\d]*{number}',
        'cholesterol': rf'(?:total cholesterol|cholesterol)[^\d]*{number}',
        'hdl': rf'(?:hdl|high density)[^\d]*{number}',
        'ldl': rf'(?:ldl|low density)[^\d]*{number}',
        'creatinine': rf'(?:creatinine|cre)[^\d]*{number}',
        'bun': rf'(?:bun|urea|blood urea nitrogen)[^\d]*{number}',
        'calcium': rf'(?:calcium|ca)[^\d]*{number}',
        'potassium': rf'(?:potassium|k\+)[^\d]*{number}',
        'sodium': rf'(?:sodium|na\+)[^\d]*{number}',
        'albumin': rf'(?:albumin)[^\d]*{number}',
        'bilirubin': rf'(?:bilirubin|bili)[^\d]*{number}',
        'alt': rf'(?:alt|sgpt)[^\d]*{number}',
        'ast': rf'(?:ast|sgot)[^\d]*{number}',
    }

    text_norm = _normalize_text(text)
    for param, pattern in patterns.items():
        match = re.search(pattern, text_norm)
        if match:
            try:
                raw_val = _parse_numeric(match.group(1))
                unit_word = match.group(2) if match.lastindex and match.lastindex >= 2 else None
                scaled_val = _apply_scaling(param, raw_val, unit_word)
                params[param] = _postprocess_value(param, scaled_val)
            except (ValueError, IndexError):
                params[param] = None

    return params

def validate(params):
    validated = {}
    
    ranges = {
        'hemoglobin': (12.0, 15.0),  
        'wbc': (4000.0, 10500.0),    
        'rbc': (3.8, 4.8),           
        'platelets': (1.5, 4.1),
        'hematocrit': (36.0, 46.0),  
        'mcv': (82.0, 92.0),         
        'mch': (27.0, 32.0),         
        'mchc': (31.5, 34.5),        
        'rdw': (11.6, 14.0),         
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