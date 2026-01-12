import os
import pdfplumber
import pytesseract
from PIL import Image
import pandas as pd


def ingest_blood_report(file_path):
    """
    Reads a blood report file and returns extracted text.
    Supports CSV, PDF, and image files.
    """

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        return _read_csv(file_path)

    elif ext == ".pdf":
        return _read_pdf(file_path)

    elif ext in [".png", ".jpg", ".jpeg"]:
        return _read_image(file_path)

    else:
        raise ValueError(f"Unsupported file format: {ext}")



def _read_csv(file_path):
    """
    Reads CSV and converts it to text format for parsing
    """
    df = pd.read_csv(file_path)

    lines = []
    for _, row in df.iterrows():
        lines.append(" ".join(str(v) for v in row.values))

    return "\n".join(lines)


def _read_pdf(file_path):
    """
    Extracts text from PDF using pdfplumber
    """
    text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text.strip()


def _read_image(file_path):
    """
    Extracts text from image using pytesseract (OCR)
    """
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text.strip()
