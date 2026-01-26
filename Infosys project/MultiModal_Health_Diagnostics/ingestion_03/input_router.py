import os
from ingestion_03.pdf_reader import read_pdf
from ingestion_03.image_reader import read_image
from ingestion_03.csv_reader import read_csv


def parse_input(file_path):
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return read_pdf(file_path)

    elif extension in [".png", ".jpg", ".jpeg"]:
        return read_image(file_path)

    elif extension == ".csv":
        return read_csv(file_path)

    else:
        raise ValueError("Unsupported file format")
