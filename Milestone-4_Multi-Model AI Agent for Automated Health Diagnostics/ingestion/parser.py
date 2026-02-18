"""
Input Interface & Parser: accepts blood reports in PDF, image (PNG), or JSON.
"""
import io
import json
import re

def _read_file_bytes(file) -> bytes:
    """Read bytes from file (Streamlit UploadedFile or path)."""
    if hasattr(file, "read"):
        file.seek(0)
        return file.read()
    with open(file, "rb") as f:
        return f.read()

def _pdf_to_text(data: bytes) -> str:
    """Extract text from PDF. Uses PyMuPDF if available, else OCR via pdf2image + pytesseract."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=data, filetype="pdf")
        parts = []
        for page in doc:
            parts.append(page.get_text())
        doc.close()
        text = "\n".join(parts).strip()
        if text and len(text) > 50:
            return text
    except Exception:
        pass
    # Fallback: render PDF to images and OCR
    try:
        from pdf2image import convert_from_bytes
        import pytesseract
        images = convert_from_bytes(data)
        return "\n".join(pytesseract.image_to_string(img) for img in images)
    except Exception:
        pass
    return ""

def _image_to_text(data: bytes) -> str:
    """Extract text from PNG/image using OCR. Tries multiple PSM modes if first returns little text."""
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(io.BytesIO(data))
        # Try PSM 6 (block), 4 (single column), 3 (auto), then default
        for psm in ("6", "4", "3", ""):
            try:
                config = f"--psm {psm}" if psm else None
                text = pytesseract.image_to_string(img, config=config) if config else pytesseract.image_to_string(img)
                text = (text or "").strip()
                if len(text) >= 30:
                    return text
                if text and psm == "6":
                    return text
            except Exception:
                continue
        text = (pytesseract.image_to_string(img) or "").strip()
        return text
    except Exception:
        return ""

def _json_to_data(data: bytes):
    """Parse JSON and return decoded structure (dict/list)."""
    text = data.decode("utf-8", errors="replace")
    return json.loads(text)

def parse_input(file, fmt: str = None):
    """
    Parse uploaded file into text (for PDF/PNG) or structured data (for JSON).
    file: file-like with .read() or path. For Streamlit, use the uploaded file object.
    fmt: "pdf" | "png" | "json" | None (infer from filename or content).
    Returns: str for PDF/PNG (raw text for extractor), dict for JSON (may be passed to extractor as-is).
    """
    data = _read_file_bytes(file)
    if not data:
        return "" if fmt != "json" else {}

    if fmt is None and hasattr(file, "name"):
        name = (file.name or "").lower()
        if name.endswith(".json"):
            fmt = "json"
        elif name.endswith(".pdf"):
            fmt = "pdf"
        elif name.endswith(".png") or name.endswith(".jpg") or name.endswith(".jpeg"):
            fmt = "png"

    if fmt == "json":
        return _json_to_data(data)
    if fmt == "pdf":
        return _pdf_to_text(data)
    if fmt in ("png", "jpg", "jpeg", "image"):
        return _image_to_text(data)

    # Auto-detect: try JSON first
    try:
        return _json_to_data(data)
    except Exception:
        pass
    # Then try PDF
    if data[:4] == b"%PDF":
        return _pdf_to_text(data)
    # Default to image OCR
    return _image_to_text(data)
