# Adobe Hackathon Challenge 1B: Persona-Driven Document Intelligence

## Overview
This project analyzes a dynamic collection of PDFs and extracts the most relevant sections and sub-sections based on a given persona and their job-to-be-done. It outputs a single structured JSON file with ranked sections and refined content, as required by the Adobe India Hackathon Round 1B.

## Directory Structure
```
.
├── input/
│   ├── Collection1/
│   │   ├── PDFs/
│   │   │   ├── doc1.pdf
│   │   │   ├── doc2.pdf
│   │   │   └── ...
│   │   └── persona_job.json  #includes persona + job-to-be-done
│   ├── Collection2/
│   │   ├── PDFs/
│   │   │   └── ...
│   │   └── persona_job.json
│   └── ...
│
├── output/
│   ├── Collection1/
│   │   ├── analysis_output_nlp_keyword.json
│   │   ├── analysis_output_nlp_embedding.json
│   │   └── analysis_output_llm.json
│   ├── Collection2/
│   │   └── analysis_output_<approach>_<method>.json
│   └── ...
│
├── models/
│   └── all-MiniLM-L6-v2/
│       ├── config.json
│       ├── model.safetensors
│       ├── tokenizer.json
│       ├── vocab.txt
│       └── ...
│
├── src/
│   ├── extractor.py    #PDF section extractor logic
│   ├── analyzer.py     #persona + job-based relevance analyzer
│   ├── summarizer.py   #sub-section text refinement
│   └── utils.py        #shared helpers: parsing, ranking, etc.
│
├── main.py   #entrypoint: loads input, runs pipeline, writes output
├── requirements.txt
├── Dockerfile
├── download_allminilml6v2.py
├── README.md
└── approach_explanation.md
```

## How to Run (PowerShell)
1. Place your PDFs (in any subfolder structure) and `persona_job.json` in each `input/CollectionX/` directory.
2. Build the Docker image:
   ```powershell
   docker build --platform linux/amd64 -t adobe-hackathon-1b:latest .
   ```
3. Run the solution for a specific collection (replace `Collection1` as needed):
   - **NLP (Keyword Overlap, Fast, Offline):**
     ```powershell
     docker run --rm `
       -v ${PWD}/input/Collection1:/app/input:ro `
       -v ${PWD}/output/Collection1:/app/output `
       -e HOST_INPUT_PATH="${PWD}/input/Collection1" `
       -e HOST_OUTPUT_PATH="${PWD}/output/Collection1" `
       --network none adobe-hackathon-1b:latest `
       --approach nlp --method keyword
     ```
   - **NLP with Embeddings (Semantic with sentence-transformers):**
     ```powershell
     docker run --rm `
       -v ${PWD}/input/Collection1:/app/input:ro `
       -v ${PWD}/output/Collection1:/app/output `
       -e HOST_INPUT_PATH="${PWD}/input/Collection1" `
       -e HOST_OUTPUT_PATH="${PWD}/output/Collection1" `
       --network none adobe-hackathon-1b:latest `
       --approach nlp --method embedding
     ```
   - **LLM (Ollama, gemma3:1b):**
     ```powershell
     # IMPORTANT: Ollama must be running on your host (not inside Docker)
     # The container will connect to Ollama's HTTP API at localhost:11434
     docker run --rm `
       -v ${PWD}/input/Collection1:/app/input:ro `
       -v ${PWD}/output/Collection1:/app/output `
       -e HOST_INPUT_PATH="${PWD}/input/Collection1" `
       -e HOST_OUTPUT_PATH="${PWD}/output/Collection1" `
       --network none adobe-hackathon-1b:latest `
       --approach llm
     ```
   - The output will be written to `output/Collection1/analysis_output_<approach>_<method>.json` (e.g., `analysis_output_nlp_keyword.json`).
   - The script will print a summary including the output path on your host.

## Input/Output Format
- **Input:**
  - PDFs: Any number (3–10) in each collection folder (can be in subfolders)
  - `persona_job.json`:
    ```json
    {
      "persona": "PhD Researcher in Computational Biology",
      "job_to_be_done": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
    }
    ```
- **Output:**
  - Only the **top 5 most relevant sections and sub-sections** are included in the output, matching the challenge sample.
  - Output file is named according to the approach and method used (see above).

## Dual-Approach Pipeline
- **NLP Approach:**
  - Fast, lightweight, fully offline.
  - Uses keyword overlap and (optionally) semantic embeddings (MiniLM) for section ranking and extractive summarization.
  - To use embeddings, install `sentence-transformers` and run with `--method embedding`.
- **LLM Approach:**
  - Uses Ollama (gemma3:1b) for advanced relevance ranking and abstractive summarization.
  - **Ollama must be running on your host machine** (not inside the Docker container). The container connects to Ollama's HTTP API at `localhost:11434`.
  - More accurate for complex tasks, but slower.

## Troubleshooting
- **LLM Mode (Ollama):**
  - If you get connection errors in LLM mode, make sure Ollama is running on your host and listening on the default port (`localhost:11434`).
  - See https://ollama.com for installation instructions.

## Dependencies
- Python 3.8+
- PyMuPDF (fitz)
- (Optional, for advanced NLP) sentence-transformers (`all-MiniLM-L6-v2`)
- (Optional, for LLM) Ollama with `gemma3:1b` model (must be running on host)

## Approach
See `approach_explanation.md` for methodology and design choices. 
