"""
Test configuration management
"""

from pathlib import Path

from memory_agent.config import Config


def test_default_config():
    """Test default configuration creation"""
    config = Config()
    assert config.embedding.model_name == "sentence-transformers/all-MiniLM-L6-v2"
    assert config.llm.context_size == 2048
    assert config.storage.data_dir == Path.home() / ".memory-agent" / "data"


def test_config_serialization(tmp_path):
    """Test config save and load"""
    config_path = tmp_path / "config.yaml"

    # Create and save config
    config = Config()
    config.save(config_path)

    # Load config
    loaded_config = Config.load(config_path)
    assert loaded_config.embedding.model_name == config.embedding.model_name
