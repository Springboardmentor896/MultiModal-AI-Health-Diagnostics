import os
import pandas as pd
import pdfplumber
import re
from typing import Dict, Any

class DataExtractor:
    def extract_from_csv(self, csv_path: str) -> Dict[str, Any]:
        """Extracts data from CSV (your blood_count_dataset.csv)"""
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found: {csv_path}")

        df = pd.read_csv(csv_path)
        if len(df) == 0:
            raise ValueError("CSV is empty")

        # Take first row as demo patient
        row = df.iloc[0]
        return {
            "Age": int(row.get("Age", 50)),
            "Gender": row.get("Gender", "Unknown"),
            "Hemoglobin": float(row.get("Hemoglobin", 13.5)),
            "PlateletCount": int(row.get("PlateletCount", 250000)),
            "WhiteBloodCells": int(row.get("WhiteBloodCells", 8000))
        }

    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Basic PDF text extraction (extend with OCR later)"""
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        params = self._parse_pdf_text(text)
        return params

    def _parse_pdf_text(self, text: str) -> Dict[str, Any]:
        patterns = {
            "Hemoglobin": r"Hemoglobin[:\s]*([0-9\.]+)",
            "PlateletCount": r"Platelets?[:\s]*([0-9,]+)",
            "WhiteBloodCells": r"WBC|White Blood Cells[:\s]*([0-9,]+)"
        }

        result = {}
        for param, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).replace(",", "")
                result[param] = float(value) if "." in value else int(value)

        return result

# Demo
if __name__ == "__main__":
    extractor = DataExtractor()
    try:
        data = extractor.extract_from_csv("blood_count_dataset.csv")
        print("CSV Data:", data)
    except Exception as e:
        print("Demo CSV data:", {"Age": 55, "Gender": "Male", "Hemoglobin": 11.2, "PlateletCount": 120000, "WhiteBloodCells": 12500})
