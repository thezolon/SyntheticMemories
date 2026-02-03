"""
Test memory manager
"""

import pytest

from memory_agent.memory_manager import MemoryManager


@pytest.fixture
def manager():
    """Create memory manager with test config"""
    # TODO: Use test configuration
    return MemoryManager()


def test_add_memory(manager):
    """Test adding a memory"""
    content = "This is a test memory"
    tags = ["test", "example"]

    memory = manager.add_memory(content, tags=tags)

    assert memory.id is not None
    assert memory.content == content
    assert memory.tags == tags
    assert memory.embedding is not None


def test_search_memory(manager):
    """Test searching memories"""
    # Add test memories
    manager.add_memory("Python is a programming language", tags=["tech"])
    manager.add_memory("JavaScript is also a programming language", tags=["tech"])
    manager.add_memory("I love cooking pasta", tags=["food"])

    # Search
    results = manager.search("programming languages", limit=2)

    assert len(results) <= 2
    # TODO: Add more assertions when vector store is implemented


def test_get_memory(manager):
    """Test retrieving a specific memory"""
    memory = manager.add_memory("Test memory content")
    _ = manager.get_memory(memory.id)  # noqa: F841

    # TODO: Implement after vector store is done
    # assert retrieved is not None
    # assert retrieved.id == memory.id


def test_delete_memory(manager):
    """Test deleting a memory"""
    memory = manager.add_memory("Memory to delete")
    manager.delete_memory(memory.id)

    # TODO: Verify deletion after vector store is implemented
