import argparse
import json
import os

from src.analyzer import rank_sections_by_relevance
from src.extractor import extract_sections_from_pdf
from src.summarizer import summarize_sections
from src.utils import get_pdf_files, load_persona_job

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"


def main():
    parser = argparse.ArgumentParser(description="Persona-driven PDF analyzer")
    parser.add_argument(
        "--approach",
        choices=["nlp", "llm"],
        default="nlp",
        help="Choose analysis approach: nlp (default) or llm (Ollama)",
    )
    parser.add_argument(
        "--method",
        choices=["auto", "keyword", "embedding"],
        default="auto",
        help="For NLP: choose 'keyword' (overlap), 'embedding' (semantic, needs sentence-transformers), or 'auto' (prefer embedding if available)",
    )
    args = parser.parse_args()
    approach = args.approach
    method = args.method

    #load persona and job
    persona_job_path = os.path.join(INPUT_DIR, "persona_job.json")
    persona_job = load_persona_job(persona_job_path)
    persona = persona_job["persona"]
    job = persona_job["job_to_be_done"]
    if isinstance(persona, dict):
        persona = " ".join(str(v) for v in persona.values())
    if isinstance(job, dict):
        job = " ".join(str(v) for v in job.values())

    #load all PDFs
    pdf_files = get_pdf_files(INPUT_DIR)
    all_sections = []
    for pdf_path in pdf_files:
        sections = extract_sections_from_pdf(pdf_path)
        for s in sections:
            s["document"] = os.path.basename(pdf_path)
        all_sections.extend(sections)

    TOP_N = 5  #limit output to top 5 as per sample output

    #rank sections by relevance
    ranked_sections, actual_method = rank_sections_by_relevance(
        all_sections, persona, job, approach=approach, method=method
    )
    ranked_sections = ranked_sections[:TOP_N]

    #summarize top sections
    subsection_analysis = summarize_sections(
        ranked_sections, persona, job, approach=approach
    )
    subsection_analysis = subsection_analysis[:TOP_N]

    #prepare output JSON
    output = {
        "metadata": {
            "input_documents": [os.path.basename(f) for f in pdf_files],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": __import__("datetime")
            .datetime.utcnow()
            .isoformat(),
        },
        "extracted_sections": [
            {
                "document": s["document"],
                "section_title": s["section_title"],
                "importance_rank": i + 1,
                "page_number": s["page_number"],
            }
            for i, s in enumerate(ranked_sections)
        ],
        "subsection_analysis": subsection_analysis,
    }

    #write output
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if approach == "llm":
        output_file = f"analysis_output_llm.json"
    else:
        output_file = f"analysis_output_{approach}_{actual_method}.json"
    output_path = os.path.join(OUTPUT_DIR, output_file)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    #print summary
    #trying to get the collection name from the input path(host-side)
    input_env = os.environ.get("HOST_INPUT_PATH", None)
    output_env = os.environ.get("HOST_OUTPUT_PATH", None)
    if input_env:
        collection_name = os.path.basename(os.path.normpath(input_env))
    else:
        #fallback: try to infer from /app/input mount
        collection_name = os.path.basename(os.path.normpath(INPUT_DIR))
    if output_env:
        host_output_path = os.path.join(output_env, output_file)
    else:
        #fallback: print the container path
        host_output_path = output_path
    print(f"[INFO] Collection '{collection_name}' processed.")
    print(f"[INFO] {len(pdf_files)} PDF files analyzed.")
    print(
        f"[INFO] Approach: {approach.upper()} | Method: {actual_method.upper() if approach == 'nlp' else 'N/A'}"
    )
    print(f"[INFO] Output saved as: {host_output_path}")


if __name__ == "__main__":
    main()
