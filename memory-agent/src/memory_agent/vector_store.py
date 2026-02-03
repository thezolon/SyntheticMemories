"""
Vector store wrapper for Lance/FAISS
Initial implementation using FAISS for simplicity
"""

import json
from pathlib import Path
from typing import List, Optional

import faiss
import numpy as np


class VectorStore:
    """Vector database wrapper using FAISS"""

    def __init__(self, data_dir: str, dimension: int = 384):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.dimension = dimension

        self.index_path = self.data_dir / "faiss.index"
        self.metadata_path = self.data_dir / "metadata.json"

        # Initialize or load index
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path) as f:
                self.metadata_store = json.load(f)
        else:
            self.index = faiss.IndexFlatL2(dimension)
            self.metadata_store = {}

    def add(self, id: str, vector: np.ndarray, metadata: dict):
        """Add a vector with metadata"""
        # Ensure vector is correct shape
        if vector.ndim == 1:
            vector = vector.reshape(1, -1)

        # Add to FAISS index
        self.index.add(vector.astype("float32"))

        # Store metadata with index position
        position = self.index.ntotal - 1
        self.metadata_store[id] = {"position": position, "metadata": metadata}

        self._save()

    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[dict]:
        """Search for similar vectors"""
        if self.index.ntotal == 0:
            return []

        # Ensure query vector is correct shape
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        # Search FAISS index
        distances, indices = self.index.search(
            query_vector.astype("float32"), min(top_k, self.index.ntotal)
        )

        # Build results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            # Find metadata by position
            for mem_id, data in self.metadata_store.items():
                if data["position"] == idx:
                    results.append(
                        {
                            "id": mem_id,
                            "score": float(1.0 / (1.0 + dist)),  # Convert distance to similarity
                            "metadata": data["metadata"],
                        }
                    )
                    break

        return results

    def get(self, id: str) -> Optional[dict]:
        """Get a vector by ID"""
        if id in self.metadata_store:
            return self.metadata_store[id]
        return None

    def delete(self, id: str):
        """Delete a vector (soft delete - marks as deleted)"""
        if id in self.metadata_store:
            del self.metadata_store[id]
            self._save()

    def count(self) -> int:
        """Count total vectors"""
        return len(self.metadata_store)

    def _save(self):
        """Save index and metadata to disk"""
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, "w") as f:
            json.dump(self.metadata_store, f, indent=2)
