"""
Configuration management for Memory Agent
"""

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class EmbeddingConfig(BaseModel):
    """Embedding model configuration"""

    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = "cpu"
    batch_size: int = 32


class LLMConfig(BaseModel):
    """LLM configuration"""

    model_path: Optional[str] = None
    context_size: int = 2048
    n_threads: Optional[int] = None
    n_gpu_layers: int = 0


class StorageConfig(BaseModel):
    """Storage configuration"""

    data_dir: Path = Field(default_factory=lambda: Path.home() / ".memory-agent" / "data")
    models_dir: Path = Field(default_factory=lambda: Path.home() / ".memory-agent" / "models")


class Config(BaseModel):
    """Main configuration"""

    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        """Load configuration from file"""
        if path is None:
            path = Path.home() / ".memory-agent" / "config.yaml"

        if path.exists():
            with open(path) as f:
                data = yaml.safe_load(f)
                # Convert string paths back to Path objects
                if "storage" in data:
                    if "data_dir" in data["storage"]:
                        data["storage"]["data_dir"] = Path(data["storage"]["data_dir"])
                    if "models_dir" in data["storage"]:
                        data["storage"]["models_dir"] = Path(data["storage"]["models_dir"])
                return cls(**data)

        return cls()

    def save(self, path: Optional[Path] = None):
        """Save configuration to file"""
        if path is None:
            path = Path.home() / ".memory-agent" / "config.yaml"

        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert Path objects to strings for YAML serialization
        data = self.model_dump()
        data["storage"]["data_dir"] = str(data["storage"]["data_dir"])
        data["storage"]["models_dir"] = str(data["storage"]["models_dir"])

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
