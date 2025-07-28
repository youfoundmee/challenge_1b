import fitz  # PyMuPDF
import re
import string
from collections import Counter

# Default set of relevance keywords — adjustable for persona-specific use
RELEVANT_KEYWORDS = {
    "group", "friends", "budget", "affordable", "activities", "things to do",
    "nightlife", "restaurants", "hotels", "packing", "tips", "itinerary",
    "local attractions", "places to visit", "transport", "adventure",
    "entertainment", "coastal", "culinary"
}

def normalize_text(text):
    """Lowercase and remove non-alphanumeric characters (except space)."""
    text = text.lower().strip()
    return re.sub(r'[^a-z0-9 ]+', '', text)

def score_heading(text, keywords=RELEVANT_KEYWORDS):
    """Score heading based on keyword presence and brevity."""
    text_clean = normalize_text(text)
    score = 0
    for keyword in keywords:
        if keyword in text_clean:
            score += 3
    if len(text.split()) <= 10:
        score += 2
    return score

def is_valid_heading(text):
    """Check if a line of text qualifies as a valid section heading."""
    if not text:
        return False
    text = text.strip()
    
    if re.fullmatch(r'[.\-–—•\s]{5,}', text):  # Only symbols
        return False
    if re.fullmatch(r'\d+[.)]?', text):       # Numbered list entry
        return False
    if re.fullmatch(r'[IVXLCDM]+\.', text):   # Roman numeral list
        return False
    if len(text) <= 3:
        return False
    if text.lower().startswith("table of contents"):
        return False
    if len(text.split()) > 18:
        return False
    return True

def extract_headings(doc, keywords=RELEVANT_KEYWORDS):
    """
    Extract top-scoring unique headings from a PDF document.

    Returns: List of dicts with heading text, page number, size, score, and importance rank.
    """
    headings = []
    seen = set()
    body_font_sizes = Counter()

    for page_num in range(len(doc)):
        blocks = doc[page_num].get_text("dict")['blocks']
        for block in blocks:
            for line in block.get("lines", []):
                if not line.get("spans"):
                    continue
                span = line["spans"][0]
                text = span.get("text", "").strip()
                if not is_valid_heading(text):
                    continue
                font_size = round(span.get("size", 0))
                body_font_sizes[font_size] += 1
                norm = normalize_text(text)
                if norm in seen:
                    continue
                seen.add(norm)
                heading = {
                    "text": text,
                    "page": page_num + 1,
                    "score": score_heading(text, keywords),
                    "size": font_size
                }
                headings.append(heading)

    # Sort headings by score descending, then by page number ascending
    headings.sort(key=lambda x: (-x["score"], x["page"]))
    
    # Assign importance rank to top 5
    for idx, h in enumerate(headings[:5]):
        h["importance_rank"] = idx + 1
    return headings[:5]

def extract_text_from_page(doc, page_number):
    """
    Extract and clean main body text from a given PDF page.
    Filters out short lines and numeric-only elements.
    """
    if not (1 <= page_number <= len(doc)):
        return ""
    
    text = doc[page_number - 1].get_text("text")
    paragraphs = [
        p.strip()
        for p in text.split("\n")
        if len(p.strip()) > 40 and not p.strip().isdigit()
    ]
    return " ".join(paragraphs)
