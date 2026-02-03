# Contributing Guide

Thank you for your interest in contributing to the OpenClaw workspace monorepo!

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/your-username/workspace.git
cd workspace
git remote add upstream https://github.com/original-org/workspace.git
```

### 2. Bootstrap Environment

```bash
./scripts/bootstrap.sh
source venv/bin/activate
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

## Project Structure

```
workspace/
├── memory-agent/       # Core memory agent package
│   ├── src/           # Source code
│   ├── tests/         # Test suite
│   └── docs/          # Project documentation
├── SyntheticMemories/ # Memory architecture research
├── skills/            # Agent capability modules
├── scripts/           # Build and utility scripts
├── docs/              # Monorepo documentation
└── CI_RUNS/           # CI execution logs
```

## Coding Standards

### Python (memory-agent and skills)

We use:
- **Black** for code formatting (100 char line length)
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all checks:
```bash
cd memory-agent
black src tests
isort src tests
flake8 src tests
mypy src
```

Or use the pre-commit hook (recommended):
```bash
pip install pre-commit
pre-commit install
```

### Code Style Guidelines

- Use type hints for function signatures
- Write docstrings for public functions (Google style)
- Keep functions focused and under 50 lines
- Prefer explicit over implicit
- Use meaningful variable names

Example:
```python
def retrieve_memories(
    query: str,
    limit: int = 10,
    threshold: float = 0.7
) -> list[Memory]:
    """Retrieve memories matching the query.
    
    Args:
        query: The search query string
        limit: Maximum number of results to return
        threshold: Minimum similarity score (0-1)
        
    Returns:
        List of Memory objects sorted by relevance
        
    Raises:
        ValueError: If limit is negative or threshold out of range
    """
    ...
```

## Testing

### Running Tests

```bash
# Run all tests
cd memory-agent
pytest

# Run with coverage
pytest --cov=memory_agent --cov-report=html

# Run specific test file
pytest tests/test_memory.py

# Run specific test
pytest tests/test_memory.py::test_store_memory
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures for common setup
- Aim for 80%+ code coverage

Example test:
```python
import pytest
from memory_agent.memory import MemoryStore

@pytest.fixture
def memory_store(tmp_path):
    """Create a temporary memory store for testing."""
    return MemoryStore(data_dir=tmp_path)

def test_store_and_retrieve(memory_store):
    """Test storing and retrieving a memory."""
    memory_store.store("Test memory content")
    results = memory_store.search("test")
    assert len(results) > 0
    assert "Test memory" in results[0].content
```

## Documentation

### Code Documentation

- All public functions/classes need docstrings
- Use Google-style docstrings
- Include type hints
- Add usage examples for complex functions

### Project Documentation

- Update relevant README.md when adding features
- Add/update docs/ markdown files for major changes
- Keep ARCHITECTURE.md up to date
- Document breaking changes in commit messages

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build process or auxiliary tool changes

**Examples:**
```
feat(memory-agent): add semantic search with embeddings

Implement vector-based semantic search using sentence transformers.
Supports similarity threshold and result ranking.

Closes #123
```

```
fix(skills): resolve homeassistant connection timeout

Increase default timeout from 5s to 30s for slower networks.

Fixes #456
```

### Commit Best Practices

- Keep commits atomic (one logical change per commit)
- Write clear, descriptive messages
- Reference issues/PRs when relevant
- Squash fixup commits before merging

## Pull Request Process

### 1. Before Submitting

- [ ] Run all tests: `pytest`
- [ ] Run linters: `black`, `isort`, `flake8`, `mypy`
- [ ] Update documentation if needed
- [ ] Add tests for new features
- [ ] Ensure CI passes locally

### 2. Submit PR

1. Push your branch to your fork
2. Open PR against `main` branch
3. Fill out the PR template:
   - Describe the changes
   - Link related issues
   - Add screenshots for UI changes
   - Note breaking changes

### 3. Review Process

- Maintainers will review within 2-3 days
- Address feedback in new commits
- Once approved, maintainers will merge
- PRs are typically squash-merged

### 4. After Merge

- Delete your branch
- Pull latest main: `git pull upstream main`
- Update your fork: `git push origin main`

## Adding New Skills

Skills are modular agent capabilities. To add a new skill:

### 1. Create Skill Directory

```bash
mkdir skills/your-skill
cd skills/your-skill
```

### 2. Create SKILL.md

```markdown
# Your Skill

Description of what the skill does.

## Commands

- `command-name`: Description
- `another-command`: Description

## Configuration

Required environment variables or config files.

## Examples

Usage examples.
```

### 3. Implement Skill Logic

Create the necessary Python modules, scripts, or configuration.

### 4. Document in Main README

Add skill to the skills list in root README.md.

### 5. Submit PR

Follow the PR process above.

## Release Process

Releases are handled by maintainers:

1. Update version in `memory-agent/pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
4. Push tag: `git push origin v0.2.0`
5. CI builds and publishes packages

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Chat**: Join our Discord/Slack (if available)
- **Security**: Email security@example.com for vulnerabilities

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the best outcome for the project
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in:
- GitHub contributors page
- CHANGELOG.md for significant contributions
- Special thanks in release notes

Thank you for contributing! 🎉
