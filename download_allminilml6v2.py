import os

from sentence_transformers import SentenceTransformer

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models", "all-MiniLM-L6-v2")
os.makedirs(MODEL_DIR, exist_ok=True)

print(f"downloading 'all-MiniLM-L6-v2' to {MODEL_DIR} ...")
model = SentenceTransformer("all-MiniLM-L6-v2")
model.save(MODEL_DIR)
print("download complete")
