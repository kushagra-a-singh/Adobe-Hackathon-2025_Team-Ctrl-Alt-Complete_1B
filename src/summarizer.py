"""
summarizer.py: Refines relevant sections into sub-section summaries.
"""

import re
import subprocess
from typing import Dict, List


def _extractive_summary(section):
    #simple extractive: return first 2 sentences from section text
    text = section.get("text", "")
    sentences = re.split(r"(?<=[.!?]) +", text)
    summary = " ".join(sentences[:2]).strip()
    return summary if summary else text[:200]


def _ollama_summary(section, persona, job):
    prompt = f"""
You are an expert assistant. Given the following section from a document, a persona, and a job-to-be-done, write a concise summary (2-3 sentences) of the section, focusing on what is most relevant for the persona's job.\n\nSection: {section.get('section_title', '')}\nText: {section.get('text', '')}\nPersona: {persona}\nJob: {job}\n\nSummary:"""
    try:
        result = subprocess.run(
            [
                "ollama",
                "run",
                "gemma3:1b",
                "--format",
                "json",
            ],
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=20,
        )
        output = result.stdout.decode("utf-8").strip()
        #return the first 3 sentences or 400 chars
        summary = " ".join(re.split(r"(?<=[.!?]) +", output)[:3])
        return summary[:400]
    except Exception as e:
        return section.get("text", "")[:200]


def summarize_sections(
    sections: List[Dict], persona: str, job: str, approach: str = "nlp"
) -> List[Dict]:
    """
    Refines relevant sections into concise, context-aware sub-section summaries.
    Returns a list of dicts: {document, refined_text, page_number}
    """
    results = []
    for section in sections:
        if approach == "llm":
            refined = _ollama_summary(section, persona, job)
        else:
            refined = _extractive_summary(section)
        results.append(
            {
                "document": section["document"],
                "refined_text": refined,
                "page_number": section["page_number"],
            }
        )
    return results
