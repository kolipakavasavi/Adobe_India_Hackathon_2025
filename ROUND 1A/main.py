!pip install PyMuPDF
from google.colab import files
uploaded = files.upload()

# /app/extract_outline.py

import os
import json
import fitz  # PyMuPDF

def is_title_span(span, page_width):
    text = span["text"].strip()
    return (
        len(text.split()) >= 3 and
        span["size"] >= 20 and
        abs((span["bbox"][0] + span["bbox"][2]) / 2 - (page_width / 2)) < 100
    )

def classify_heading(span):
    size = span["size"]
    font = span["font"]
    text = span["text"].strip()
    is_bold = "Bold" in font or "bold" in font

    if size >= 20 and is_bold:
        return "H1"
    elif size >= 16 and is_bold:
        return "H2"
    elif size >= 13:
        return "H3"
    else:
        return None

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    outline = []
    title = None

    for page_number, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        page_width = page.rect.width

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue

                    if page_number == 1 and not title and is_title_span(span, page_width):
                        title = text

                    level = classify_heading(span)
                    if level:
                        outline.append({
                            "level": level,
                            "text": text,
                            "page": page_number
                        })

    if not title:
        title = doc.metadata.get("title") or os.path.basename(pdf_path)

    return {
        "title": title,
        "outline": outline
    }

result = extract_outline("file02.pdf")
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

from google.colab import files
files.download("output.json")

