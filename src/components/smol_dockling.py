import pdfplumber
import requests
import os
import dateparser
import re

DUCKLING_URL = os.getenv("DUCKLING_URL", "http://duckling:8000/parse")

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def call_duckling(text, locale="en_US"):
    try:
        response = requests.post(DUCKLING_URL, data={
            "text": text,
            "locale": locale
        })
        return response.json()
    except Exception as e:
        return [{"error": str(e)}]

def fallback_parse(text):
    results = []
    
    # Dates
    for match in re.finditer(r"\b(?:\d{1,2}[/-])?(?:\d{1,2}[/-])?\d{2,4}\b", text):
        parsed = dateparser.parse(match.group())
        if parsed:
            results.append({
                "body": match.group(),
                "start": match.start(),
                "value": parsed.isoformat(),
                "dim": "time"
            })

    # Numbers
    for match in re.finditer(r"\b\d+(?:,\d{3})*(?:\.\d+)?\b", text):
        results.append({
            "body": match.group(),
            "start": match.start(),
            "value": float(match.group().replace(",", "")),
            "dim": "number"
        })

    return results

def extract_entities_from_pdf(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    # entities = call_duckling(text)
    # if not entities or 'error' in entities[0]:
    #     entities = fallback_parse(text)
    return text
