"""
LLM interface using llama.cpp
Supports both llama-cpp-python and Ollama backends
"""

import os
from typing import Optional


class LLMInterface:
    """Local LLM interface with multiple backend support"""

    def __init__(
        self,
        model_path: Optional[str] = None,
        context_size: int = 2048,
        n_threads: Optional[int] = None,
        n_gpu_layers: int = 0,
        backend: str = "auto",  # auto, llama-cpp, or ollama
    ):
        self.model_path = model_path
        self.context_size = context_size
        self.n_threads = n_threads or os.cpu_count()
        self.n_gpu_layers = n_gpu_layers
        self.backend = backend
        self.model = None
        self._backend_type = None

    def _load_model(self):
        """Lazy load the model"""
        if self.model is not None:
            return

        # Auto-detect backend
        if self.backend == "auto":
            if self.model_path and os.path.exists(self.model_path):
                self._backend_type = "llama-cpp"
            else:
                self._backend_type = "ollama"
        else:
            self._backend_type = self.backend

        # Load based on backend
        if self._backend_type == "llama-cpp":
            self._load_llama_cpp()
        elif self._backend_type == "ollama":
            self._load_ollama()

    def _load_llama_cpp(self):
        """Load model using llama-cpp-python"""
        try:
            from llama_cpp import Llama

            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.context_size,
                n_threads=self.n_threads,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False,
            )
        except ImportError:
            raise RuntimeError(
                "llama-cpp-python not installed. Install with: pip install llama-cpp-python"
            )

    def _load_ollama(self):
        """Load model using Ollama"""
        try:
            import ollama

            self.model = ollama
        except ImportError:
            raise RuntimeError(
                "Ollama not available. Install with: pip install ollama\n"
                "Or install the Ollama CLI: https://ollama.ai"
            )

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate text from prompt"""
        self._load_model()

        if self._backend_type == "llama-cpp":
            output = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=0.7,
                stop=["</s>", "\n\n\n"],
            )
            return output["choices"][0]["text"].strip()

        elif self._backend_type == "ollama":
            response = self.model.generate(
                model="llama2", prompt=prompt, options={"num_predict": max_tokens}  # Default model
            )
            return response["response"].strip()

        return "LLM backend not configured. Set model_path or install Ollama."

    def summarize(self, text: str, max_length: int = 200) -> str:
        """Summarize text"""
        prompt = f"""Summarize the following text in {max_length} words or less.

Text:
{text}

Summary:"""
        return self.generate(prompt, max_tokens=max_length * 2)

    def answer_question(self, question: str, context: str, max_tokens: int = 300) -> str:
        """Answer a question given context"""
        prompt = f"""Answer the question based on the context provided.

Context:
{context}

Question: {question}

Answer:"""
        return self.generate(prompt, max_tokens=max_tokens)

    def extract_keywords(self, text: str) -> list[str]:
        """Extract keywords from text"""
        prompt = f"""Extract 5-10 important keywords from this text.
Return only the keywords, comma-separated.

Text: {text}

Keywords:"""
        result = self.generate(prompt, max_tokens=100)
        # Parse comma-separated keywords
        keywords = [k.strip() for k in result.split(",")]
        return [k for k in keywords if k][:10]
