"""
utils.py: Shared helpers for parsing, ranking, and NLP tasks.
"""

import json
import os

def load_persona_job(json_path: str) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_pdf_files(input_dir: str) -> list:
    pdf_files = []
    for root, _, files in os.walk(input_dir):
        for f in files:
            if f.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, f))
    return pdf_files
