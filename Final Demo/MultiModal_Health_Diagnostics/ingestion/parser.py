"""
Parser Module
Handles different file formats: PDF, Image, CSV, Text
"""

import PyPDF2
import pytesseract
from PIL import Image, ImageEnhance
import csv
import io
import os

# ============================================
# TESSERACT CONFIGURATION - Direct Path
# ============================================
if os.name == 'nt':  # Windows
    # Set direct path (no PATH environment variable needed)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    print("✓ Tesseract configured at: C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
# ============================================


def parse_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # If no text extracted (scanned PDF), try OCR
        if not text.strip():
            print("PDF has no text, attempting OCR...")
            text = ocr_pdf(file_path)
        
        return text
    except Exception as e:
        raise Exception(f"PDF parsing error: {str(e)}")


def ocr_pdf(file_path):
    """OCR for scanned PDFs"""
    try:
        from pdf2image import convert_from_path
        
        print("Converting PDF to images for OCR...")
        images = convert_from_path(file_path, dpi=300)
        
        text = ""
        for i, image in enumerate(images):
            print(f"Processing page {i+1}...")
            page_text = pytesseract.image_to_string(image, lang='eng')
            text += f"\n--- Page {i+1} ---\n{page_text}\n"
        
        return text
    except Exception as e:
        return f"OCR failed: {str(e)}"


def parse_image(file_path):
    """Extract text from image using OCR"""
    try:
        print(f"Opening image: {file_path}")
        
        # Open image
        img = Image.open(file_path)
        
        # Preprocess image for better OCR
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        print("Enhancing image for better OCR...")
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        print("Extracting text with Tesseract...")
        
        # Extract text using Tesseract
        # --psm 6: Assume a single uniform block of text
        text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')
        
        if not text.strip():
            return "No text could be extracted from the image. Please ensure the image is clear and contains readable text."
        
        print(f"Extracted {len(text)} characters")
        return text
        
    except Exception as e:
        raise Exception(f"Image parsing error: {str(e)}")


def parse_csv(file_path):
    """Extract text from CSV file"""
    try:
        text = ""
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                text += ' '.join(row) + "\n"
        return text
    except Exception as e:
        raise Exception(f"CSV parsing error: {str(e)}")
