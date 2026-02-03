#!/usr/bin/env python3
"""
Download required models for Memory Agent
"""

import os
from pathlib import Path

from huggingface_hub import snapshot_download


def download_embedding_model():
    """Download sentence transformer model"""
    print("Downloading embedding model...")
    
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    cache_dir = Path.home() / ".memory-agent" / "models" / "embeddings"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    snapshot_download(
        repo_id=model_name,
        cache_dir=str(cache_dir),
        ignore_patterns=["*.msgpack", "*.h5", "*.ot"],
    )
    
    print(f"✓ Embedding model downloaded to {cache_dir}")


def download_llm_model():
    """Download LLM model (placeholder)"""
    print("\nLLM model download:")
    print("For the LLM, you have two options:")
    print("1. Download manually from: https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF")
    print("2. Use Ollama: ollama pull llama2")
    print("\nPlace GGUF models in: ~/.memory-agent/models/llm/")


def main():
    """Main setup"""
    print("Memory Agent - Model Download\n")
    
    try:
        download_embedding_model()
        download_llm_model()
        
        print("\n✓ Setup complete!")
        print("\nNext steps:")
        print("1. Optionally download an LLM model")
        print("2. Run: python src/main.py setup")
        print("3. Start using: python src/main.py add 'Your first memory'")
        
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        print("You may need to install: pip install huggingface-hub")


if __name__ == "__main__":
    main()
