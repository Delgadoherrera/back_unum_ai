#text_processing
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

