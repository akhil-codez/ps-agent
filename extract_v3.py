import pdfplumber
import sys

sys.stdout.reconfigure(encoding='utf-8')

with pdfplumber.open('C:\\Users\\akhia\\OneDrive\\Documents\\ps_agent\\panchayat_blueprint_v3.pdf') as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            print(f'--- Page {i+1} ---')
            print(text)
            print()
