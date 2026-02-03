# Contributing to Memory Agent

Thank you for your interest in contributing! Memory Agent is built on the principle that cognitive tools should be private, local, and community-driven.

## Getting Started

### 1. Fork & Clone
```bash
git clone https://github.com/yourusername/memory-agent.git
cd memory-agent
```

### 2. Set Up Development Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### 3. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Running Tests
```bash
pytest tests/ -v
```

### Code Formatting
```bash
# Format code
black src/ tests/
isort src/ tests/

# Check formatting
black --check src/ tests/
isort --check-only src/ tests/
```

### Linting
```bash
flake8 src/ tests/ --max-line-length=100
mypy src/
```

### Running Locally
```bash
python src/main.py --help
```

## Contribution Guidelines

### Code Style
- Follow PEP 8
- Use type hints where possible
- Keep functions focused and small
- Write docstrings for public APIs
- Line length: 100 characters max

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add audio transcription support
fix: resolve embedding dimension mismatch
docs: update installation instructions
test: add tests for vector store
refactor: simplify LLM interface
```

### Pull Requests
1. Update relevant documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md (if significant)
5. Reference related issues

PR template:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing done

## Checklist
- [ ] Tests pass
- [ ] Code formatted (black, isort)
- [ ] Documentation updated
```

## Areas for Contribution

### High Priority
- 🔴 Vector store implementation (Lance/FAISS)
- 🔴 LLM integration (llama.cpp)
- 🔴 Memory consolidation algorithms
- 🔴 Performance optimization

### Medium Priority
- 🟡 Web UI (Phase 5)
- 🟡 Audio transcription (Whisper)
- 🟡 Document parsing (PDF, DOCX)
- 🟡 Plugin system

### Good First Issues
- 🟢 Documentation improvements
- 🟢 Test coverage expansion
- 🟢 CLI enhancements
- 🟢 Example scripts

## Project Structure

```
memory-agent/
├── src/memory_agent/     # Core library
│   ├── cli.py            # CLI interface
│   ├── memory_manager.py # Core orchestrator
│   ├── embeddings.py     # Embedding engine
│   ├── vector_store.py   # Vector database
│   ├── llm.py            # LLM interface
│   ├── models.py         # Data models
│   └── config.py         # Configuration
├── tests/                # Test suite
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── data/, models/        # Runtime directories
```

## Testing Guidelines

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Aim for >80% coverage

### Integration Tests
- Test component interactions
- Use temporary directories for file operations
- Clean up after tests

### Performance Tests
- Benchmark critical paths
- Track query latency
- Monitor memory usage

Example test:
```python
def test_add_and_search_memory():
    manager = MemoryManager()
    
    # Add memory
    memory = manager.add_memory("Test content", tags=["test"])
    assert memory.id is not None
    
    # Search
    results = manager.search("test", limit=5)
    assert len(results) > 0
    assert results[0].memory.id == memory.id
```

## Documentation

### Code Documentation
- Docstrings for all public functions/classes
- Type hints for parameters and returns
- Include examples in docstrings

Example:
```python
def embed(self, text: str) -> np.ndarray:
    """
    Convert text to embedding vector.
    
    Args:
        text: Input text to embed
        
    Returns:
        Numpy array of shape (embedding_dim,)
        
    Example:
        >>> engine = EmbeddingEngine()
        >>> vec = engine.embed("Hello world")
        >>> vec.shape
        (384,)
    """
```

### User Documentation
- Update README.md for major features
- Add usage examples to docs/USAGE.md
- Keep ROADMAP.md current

## Privacy & Security

**Critical**: This project's core value is privacy.

### Do NOT:
- ❌ Add telemetry or analytics
- ❌ Make external API calls (unless optional)
- ❌ Log sensitive user data
- ❌ Include API keys or secrets

### Do:
- ✅ Keep all processing local
- ✅ Use placeholders for any tokens
- ✅ Document data storage locations
- ✅ Enable encrypted storage options

## Community

### Communication
- GitHub Issues for bugs and features
- Discussions for questions and ideas
- PRs for code contributions

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## Release Process

Maintainers will:
1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create GitHub release
4. Tag with semantic version (v0.1.0)

## Questions?

- Check existing issues and discussions
- Read the documentation
- Ask in GitHub Discussions
- Tag maintainers in PRs if stuck

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Memory Agent!** 🧠✨
