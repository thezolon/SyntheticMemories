"""
Embedding engine for converting text to vectors
"""

from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingEngine:
    """Handles text to vector conversion"""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu",
        batch_size: int = 32,
    ):
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self.model: Optional[SentenceTransformer] = None

    def _load_model(self):
        """Lazy load the model"""
        if self.model is None:
            self.model = SentenceTransformer(self.model_name, device=self.device)

    def embed(self, text: str) -> np.ndarray:
        """Convert single text to embedding"""
        self._load_model()
        return self.model.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Convert batch of texts to embeddings"""
        self._load_model()
        return self.model.encode(
            texts,
            batch_size=self.batch_size,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        self._load_model()
        return self.model.get_sentence_embedding_dimension()
