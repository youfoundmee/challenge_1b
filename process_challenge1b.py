import os
import json
import fitz  # PyMuPDF
from datetime import datetime
from pdf_helpers import extract_headings, extract_text_from_page

PERSONA = "Travel Planner"
JOB_TO_BE_DONE = "Plan a trip of 4 days for a group of 10 college friends."

def process_collection(collection_folder):
    output = {
        "metadata": {
            "input_documents": [],
            "persona": PERSONA,
            "job_to_be_done": JOB_TO_BE_DONE,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    for filename in sorted(os.listdir(collection_folder)):
        if not filename.lower().endswith(".pdf"):
            continue

        filepath = os.path.join(collection_folder, filename)
        doc = fitz.open(filepath)
        output["metadata"]["input_documents"].append(filename)

        headings = extract_headings(doc)
        for h in headings:
            output["extracted_sections"].append({
                "document": filename,
                "section_title": h["text"],
                "importance_rank": h["importance_rank"],
                "page_number": h["page"]
            })

        # Collect text per unique page for this doc
        pages_done = set()
        for h in headings:
            page_num = h["page"]
            if (filename, page_num) in pages_done:
                continue
            pages_done.add((filename, page_num))
            page_text = extract_text_from_page(doc, page_num)
            if page_text:
                output["subsection_analysis"].append({
                    "document": filename,
                    "refined_text": page_text,
                    "page_number": page_num
                })

    # Save output JSON
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: py process_challenge1b.py <collection_folder>")
        return
    collection_path = sys.argv[1]
    process_collection(collection_path)

if __name__ == "__main__":
    main()
