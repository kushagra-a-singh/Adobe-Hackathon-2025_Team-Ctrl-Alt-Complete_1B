# Approach Explanation: Adobe Hackathon 1B

## Problem Statement
Given a collection of PDFs (which may be organized in subfolders), a persona, and a job-to-be-done, extract and rank the most relevant sections and subsections for the persona’s needs, outputting structured JSON as per the challenge requirements.

## Methodology

### 1. PDF Text Extraction
- **Library:** PyMuPDF (`fitz`) is used for fast, reliable, and layout-aware text extraction.
- **Process:** Each PDF is parsed page by page. Text blocks, font sizes, and styles are analyzed to identify potential section headings and their hierarchy.
- **Recursive Search:** The pipeline automatically finds all PDFs in the collection folder, including any subfolders (e.g., a `PDFs/` subfolder).

### 2. Section & Subsection Detection
- **Heuristics:** Headings are detected using a combination of:
  - Font size and weight (larger/bolder text is likely a heading)
  - Position (top of page, left-aligned)
  - Common heading patterns (e.g., numbered, all-caps, bold)
- **Hierarchy:** Headings are classified into levels (H1, H2, H3) based on relative font size and style.
- **Section Extraction:** For each heading, the corresponding section text is extracted until the next heading of the same or higher level.

### 3. Persona & Task Understanding
- **Input:** Persona role and job-to-be-done are parsed from the `persona_job.json` file, which must be present in the root of each collection folder.

### 4. Dual Relevance Ranking Approaches
- **NLP Approach:**
  - Uses keyword overlap and optionally semantic embeddings (MiniLM, via sentence-transformers) to score section relevance.
  - Fast, lightweight, and fully offline. Suitable for most use cases and resource-constrained environments.
  - **Advanced NLP (Embeddings):**
    - If `sentence-transformers` is installed, the pipeline can use MiniLM embeddings for semantic similarity between the persona/job and each section.
    - This is enabled with the `--method embedding` flag (or `--method auto` if embeddings are available).
    - Embedding-based ranking is more robust for complex or nuanced tasks, as it captures meaning beyond simple keyword overlap.
- **LLM Approach:**
  - Uses Ollama (gemma3:1b) for advanced relevance ranking and abstractive summarization.
  - **IMPORTANT:** Ollama must be running on your host machine (not inside the Docker container). The container connects to Ollama's HTTP API at `localhost:11434`.
  - More accurate for nuanced or complex persona/job queries, but slower and requires Ollama.
  - Prompts are optimized for concise, numeric output to simplify parsing and ranking.

### 5. Subsection Analysis & Summarization
- **NLP Approach:**
  - Extractive: Selects the first 2 sentences or most relevant sentences from the section text.
  - (Optional) Uses semantic similarity to select the most relevant sentences/paragraphs.
- **LLM Approach:**
  - Abstractive: Uses Ollama (gemma3:1b) to generate a concise, context-aware summary tailored to the persona/job.
  - Prompts are optimized for short, focused summaries.

### 6. Output Construction
- **Schema:** Output JSON strictly follows the provided schema, including metadata, ranked sections, and refined subsection analysis.
- **Collection-based Output:** Each collection's output is written to its own output folder (e.g., `output/Collection1/analysis_output_<approach>_<method>.json`).
- **Top N Only:** Only the **top 5 most relevant sections and sub-sections** are included in the output, matching the challenge sample.
- **Output File Naming:** The output file is named according to the approach and method used (e.g., `analysis_output_nlp_keyword.json`).
- **Prints Output Path:** The script prints a summary including the output path on your host if you set the `HOST_INPUT_PATH` and `HOST_OUTPUT_PATH` environment variables in your Docker run command.

### 7. Performance & Constraints
- **Offline:** All models and dependencies are included in the Docker image; no internet access is required at runtime.
- **Efficiency:** The pipeline is optimized for ≤60s processing time for 3–5 documents, and ≤1GB model size.
- **Dockerization:** The solution is fully containerized for reproducibility and ease of evaluation.

## How to Use (PowerShell)
- Select which collection to process by mapping the desired collection's input and output folders in your Docker run command, and set the environment variables for host paths:
  ```powershell
  docker run --rm `
    -v ${PWD}/input/Collection1:/app/input:ro `
    -v ${PWD}/output/Collection1:/app/output `
    -e HOST_INPUT_PATH="${PWD}/input/Collection1" `
    -e HOST_OUTPUT_PATH="${PWD}/output/Collection1" `
    --network none adobe-hackathon-1b:latest `
    --approach nlp --method embedding
  ```
- The pipeline will auto-detect all PDFs (recursively) and use the persona/job JSON in that collection.

## Troubleshooting
- **LLM Mode (Ollama):**
  - If you get connection errors in LLM mode, make sure Ollama is running on your host and listening on the default port (`localhost:11434`).
  - See https://ollama.com for installation instructions.

## Why This Approach?
- **Accuracy:** Combines structural heuristics, semantic similarity, and LLM reasoning for robust section detection and ranking.
- **Efficiency:** Uses lightweight, high-performance models suitable for CPU-only, offline environments.
- **Flexibility:** User can select between NLP and LLM approaches via a simple flag, enabling trade-offs between speed and accuracy. Advanced NLP (embeddings) can be enabled for better semantic matching.
- **Generality:** Works across diverse document types, personas, and tasks without hardcoding.

---
This methodology ensures the solution is accurate, efficient, and generalizable, meeting all challenge requirements. 
