!pip install PyMuPDF

import fitz  # PyMuPDF
import json
from datetime import datetime
from google.colab import files

#Upload PDFs
print("Upload 3 to 50 PDF files from any domain (travel, food, research, etc.)")
uploaded = files.upload()
pdf_files = [f for f in uploaded if f.endswith('.pdf')]

if len(pdf_files) < 3:
    raise Exception(" Please upload at least 3 PDFs.")
else:
    print(f" {len(pdf_files)} PDFs uploaded.")

#Extract Text from Each Page
def extract_pages(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        content = []
        for page_number, page in enumerate(doc, start=1):
            text = page.get_text().strip()
            content.append((page_number, text))
        return content
    except Exception as e:
        print(f" Error reading {pdf_path}: {e}")
        return []

#Keyword Relevance Scoring
def rank_relevance(text, keywords):
    text = text.lower()
    return sum(1 for kw in keywords if kw.lower() in text)

#Document Analyzer
def analyze_documents(file_list, persona, job, keywords):
    metadata = {
        "input_documents": file_list,
        "persona": persona,
        "job_to_be_done": job,
        "processing_timestamp": datetime.utcnow().isoformat()
    }

    extracted_sections = []
    subsection_analysis = []

    for filename in file_list:
        print(f" Processing: {filename}")
        pages = extract_pages(filename)

        for page_number, text in pages:
            score = rank_relevance(text, keywords)
            if score > 0:
                section_title = text.split('\n')[0][:80] or "Untitled Section"
                extracted_sections.append({
                    "document": filename,
                    "section_title": section_title,
                    "importance_rank": score,
                    "page_number": page_number
                })
                subsection_analysis.append({
                    "document": filename,
                    "refined_text": text[:500],
                    "page_number": page_number
                })

    # Sort by rank descending
    extracted_sections.sort(key=lambda x: -x["importance_rank"])

    return {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }



#Customize this for any domain
persona = "General Knowledge Explorer"
job = "Discover the most informative and useful insights from a large PDF collection"
keywords = [
    "summary", "insight", "key points", "overview", "introduction", "conclusion",
    "benefits", "recommendation", "findings", "analysis", "tip", "data", "review",
    "highlights", "core", "strategy", "planning", "impact", "results", "objective"
]



# Run analysis
result = analyze_documents(pdf_files, persona, job, keywords)

# Save and download JSON
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

files.download("output.json")
