from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLm-L6-v2')

def encode(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.array([])
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=False,
        convert_to_numpy=True
    )
    return embeddings