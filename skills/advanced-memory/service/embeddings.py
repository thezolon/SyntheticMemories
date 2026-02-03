"""Ollama embedding client for local vector generation."""

import ollama
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Client for generating embeddings using local Ollama."""
    
    def __init__(self, host: str = "http://localhost:11434", model: str = "nomic-embed-text"):
        self.host = host
        self.model = model
        self.client = ollama.Client(host=host)
        logger.info(f"Initialized Ollama client: {host} (model: {model})")
    
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = self.client.embeddings(
                model=self.model,
                prompt=text
            )
            embedding = response['embedding']
            # Convert to float32 for LanceDB compatibility
            embedding = [float(x) for x in embedding]
            logger.debug(f"Generated embedding for text (len={len(text)}, dim={len(embedding)})")
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embeddings.append(self.embed(text))
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings
    
    def health_check(self) -> bool:
        """
        Check if Ollama is reachable and the model is available.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Test with simple embedding
            self.embed("health check")
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
