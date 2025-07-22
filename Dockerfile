FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir torch==2.2.2+cpu -f https://download.pytorch.org/whl/torch_stable.html && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
COPY models/all-MiniLM-L6-v2 /app/models/all-MiniLM-L6-v2

# Set environment variables for offline, CPU-only
ENV TRANSFORMERS_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1
ENV HF_HOME=/app/.cache/huggingface

# NOTE: Ollama cannot be run inside Docker easily (requires special permissions and hardware access).
# If you want to use the LLM approach, run Ollama on your host machine and ensure it is accessible from the container.

ENTRYPOINT ["python", "main.py"] 
