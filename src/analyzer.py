"""
analyzer.py: Matches extracted sections against persona + job, ranks by relevance.
"""

import json
import os
import re

#when we are using Ollama, import subprocess for local model calls
import subprocess
from typing import Dict, List, Tuple

try:
    from sentence_transformers import SentenceTransformer, util

    _EMBEDDING_MODEL = SentenceTransformer("models/all-MiniLM-L6-v2")
    _HAS_EMBEDDINGS = True
except ImportError:
    _HAS_EMBEDDINGS = False
    _EMBEDDING_MODEL = None


def _nlp_score(section, persona, job):
    #simple keyword overlap between section title/text and persona/job
    text = (section.get("section_title", "") + " " + section.get("text", "")).lower()
    persona_job = (persona + " " + job).lower()
    #tokenize and count overlap
    text_words = set(re.findall(r"\w+", text))
    pj_words = set(re.findall(r"\w+", persona_job))
    overlap = len(text_words & pj_words)
    return overlap


def _embedding_score(section, persona, job):
    #use MiniLM embeddings for semantic similarity
    if not _HAS_EMBEDDINGS:
        return _nlp_score(section, persona, job)
    text = section.get("section_title", "") + ". " + section.get("text", "")
    persona_job = persona + ". " + job
    emb1 = _EMBEDDING_MODEL.encode(persona_job, convert_to_tensor=True)
    emb2 = _EMBEDDING_MODEL.encode(text, convert_to_tensor=True)
    score = float(util.pytorch_cos_sim(emb1, emb2).item())
    return score


def _ollama_score(section, persona, job):
    #use Ollama(gemma3:1b) to score relevance
    prompt = f"""
You are an expert assistant. Given the following section from a document, a persona, and a job-to-be-done, rate the relevance of the section to the persona's job on a scale of 1 (not relevant) to 10 (highly relevant).\n\nSection: {section.get('section_title', '')}\nText: {section.get('text', '')}\nPersona: {persona}\nJob: {job}\n\nRespond with only the number (1-10)."
    """
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
            timeout=10,
        )
        output = result.stdout.decode("utf-8").strip()
        match = re.search(r"([1-9]|10)", output)
        if match:
            return int(match.group(1))
        return 1
    except Exception as e:
        return 1


def rank_sections_by_relevance(
    sections: List[Dict],
    persona: str,
    job: str,
    approach: str = "nlp",
    method: str = "auto",
) -> Tuple[List[Dict], str]:  
    """
    Ranks sections based on relevance to persona and job-to-be-done.
    If approach is 'nlp', method can be 'auto', 'keyword', or 'embedding'.
    Returns a list of dicts with importance_rank.
    """
    if approach == "llm":
        for section in sections:
            section["relevance_score"] = _ollama_score(section, persona, job)
        actual_method = "llm"
    else:
        use_embedding = (method == "embedding") or (
            method == "auto" and _HAS_EMBEDDINGS
        )
        for section in sections:
            if use_embedding:
                section["relevance_score"] = _embedding_score(section, persona, job)
            else:
                section["relevance_score"] = _nlp_score(section, persona, job)
        actual_method = "embedding" if use_embedding else "keyword"
    #sort by score descending
    ranked = sorted(sections, key=lambda x: x["relevance_score"], reverse=True)
    
    for i, s in enumerate(ranked):
        s["importance_rank"] = i + 1
    return ranked, actual_method
