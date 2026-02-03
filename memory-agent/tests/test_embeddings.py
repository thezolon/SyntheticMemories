"""
Test embedding engine
"""

import numpy as np
import pytest

from memory_agent.embeddings import EmbeddingEngine


@pytest.fixture
def engine():
    """Create embedding engine"""
    return EmbeddingEngine()


def test_single_embedding(engine):
    """Test single text embedding"""
    text = "This is a test sentence"
    embedding = engine.embed(text)

    assert isinstance(embedding, np.ndarray)
    assert embedding.shape[0] == 384  # Default model dimension
    assert embedding.dtype == np.float32


def test_batch_embedding(engine):
    """Test batch embedding"""
    texts = [
        "First sentence",
        "Second sentence",
        "Third sentence",
    ]
    embeddings = engine.embed_batch(texts)

    assert embeddings.shape == (3, 384)


def test_similarity(engine):
    """Test similarity calculation"""
    text1 = "The cat sat on the mat"
    text2 = "The cat is sitting on the mat"
    text3 = "The dog ran in the park"

    emb1 = engine.embed(text1)
    emb2 = engine.embed(text2)
    emb3 = engine.embed(text3)

    # Similar sentences should have higher similarity
    sim_similar = engine.similarity(emb1, emb2)
    sim_different = engine.similarity(emb1, emb3)

    assert sim_similar > sim_different
    assert 0 <= sim_similar <= 1
    assert 0 <= sim_different <= 1
