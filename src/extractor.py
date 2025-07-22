"""
extractor.py: Extracts section headings (H1/H2/H3) and page numbers from PDFs using layout and semantic cues.
"""

import re
from typing import Dict, List
import fitz


def extract_sections_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Extracts section headings (H1/H2/H3) with page numbers from a PDF.
    Returns a list of dicts: {section_title, level, page_number, text}
    """
    doc = fitz.open(pdf_path)
    headings = []
    font_sizes = []
    #first pass: collect all font sizes
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        font_sizes.append(s["size"])
    if not font_sizes:
        return []
    #heuristic: H1 = largest, H2 = 2nd largest, H3 = 3rd largest font sizes
    unique_sizes = sorted(list(set(font_sizes)), reverse=True)
    size_to_level = {}
    if len(unique_sizes) > 0:
        size_to_level[unique_sizes[0]] = "H1"
    if len(unique_sizes) > 1:
        size_to_level[unique_sizes[1]] = "H2"
    if len(unique_sizes) > 2:
        size_to_level[unique_sizes[2]] = "H3"
    
    #second pass: extract headings
    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"].strip()
                        if not text or len(text) < 3:
                            continue
                        size = s["size"]
                        level = size_to_level.get(size)
                        #semantic cue: all-caps, numbered or bold
                        is_heading = False
                        if level:
                            is_heading = True
                        elif (
                            re.match(r"^[A-Z][A-Z\s\d\-\.]+$", text)
                            and len(text.split()) < 10
                        ):
                            is_heading = True
                            level = "H2"
                        elif re.match(r"^(\d+\.|[IVX]+\.)", text):
                            is_heading = True
                            level = "H3"
                        if is_heading:
                            headings.append(
                                {
                                    "section_title": text,
                                    "level": level or "H3",
                                    "page_number": page_num,
                                    "text": text,
                                }
                            )
    return headings
