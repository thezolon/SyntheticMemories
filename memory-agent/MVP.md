# MVP Specification

## Goal

Build a minimal but functional cognitive memory system that demonstrates core value: **store text memories and retrieve them semantically**.

## Scope

### In Scope ✅
- Text-only ingestion (no audio/documents in MVP)
- Semantic search using embeddings
- CLI interface
- Local storage (Lance vector database)
- Basic LLM-powered summarization
- Simple metadata (timestamp, tags)

### Out of Scope ❌
- Web UI (Phase 5)
- Audio transcription (Phase 3)
- Document parsing (Phase 3)
- Advanced query features (Phase 2)
- API server (Phase 5)
- Multi-user support

## User Stories

### Story 1: Store a Memory
```bash
$ memory add "Had lunch with Sarah at Cafe Luna. She mentioned the new project deadline is March 15th."
✓ Memory saved (id: mem_abc123)
```

### Story 2: Search Memories
```bash
$ memory search "project deadline"

Found 3 memories:

[1] Had lunch with Sarah at Cafe Luna. She mentioned the new project deadline...
    📅 2 days ago | 🏷️ meetings

[2] John said the project deadline might be extended...
    📅 1 week ago | 🏷️ work

[3] Project planning session - discussed aggressive deadline...
    📅 2 weeks ago | 🏷️ meetings, planning
```

### Story 3: Get Details
```bash
$ memory show mem_abc123

Memory: mem_abc123
Created: 2026-01-31 14:23:15
Tags: meetings, work

Had lunch with Sarah at Cafe Luna. She mentioned the new project deadline 
is March 15th. She's concerned about the timeline but thinks it's doable 
if we get the designs finalized by end of week.
```

### Story 4: Ask Questions (LLM-Powered)
```bash
$ memory ask "When is the project deadline?"

Based on your memories:
The project deadline is March 15th, as mentioned by Sarah during your 
lunch at Cafe Luna 2 days ago.

Sources: mem_abc123
```

## Technical Requirements

### 1. Core Components

#### Memory Storage
- **Vector Database**: Lance
- **Format**: Columnar (Parquet-compatible)
- **Schema**:
  ```python
  {
      "id": str,           # Unique identifier
      "content": str,      # The memory text
      "embedding": [float], # 384-dim vector
      "timestamp": datetime,
      "tags": [str],       # User-provided tags
      "metadata": dict     # Extensible
  }
  ```

#### Embedding Engine
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Hardware**: CPU-only (GPU optional)
- **Batch size**: 32

#### LLM Interface
- **Model**: `Llama-3.2-3B-Instruct` (Q4_K_M quantized)
- **Backend**: llama-cpp-python
- **Context window**: 2048 tokens
- **Use cases**: Summarization, Q&A

### 2. CLI Commands

```bash
memory add <text>              # Add a memory
memory add --file <path>       # Add from file
memory add --tag <tag> <text>  # Add with tags

memory search <query>          # Semantic search
memory search --limit 10       # Return more results

memory show <id>               # Show full memory

memory ask <question>          # LLM-powered Q&A

memory list                    # List recent memories
memory list --tag <tag>        # Filter by tag

memory delete <id>             # Delete a memory

memory stats                   # Show statistics
```

### 3. Performance Targets

- **Ingestion**: <2 seconds per memory
- **Search**: <1 second for top 10 results
- **Q&A**: <5 seconds for response
- **Capacity**: Support 10,000 memories without degradation

### 4. Data Storage

```
~/.memory-agent/
├── data/
│   ├── vectors/           # Lance database
│   └── metadata.db        # SQLite for quick lookups
├── models/                # Downloaded models
│   ├── embeddings/
│   └── llm/
├── config.yaml            # User configuration
└── logs/
    └── memory-agent.log
```

## Implementation Plan

### Week 1: Foundation
- [x] Project setup
- [ ] Set up virtual environment
- [ ] Install dependencies
- [ ] Create basic project structure
- [ ] Configure logging

### Week 2: Storage & Embeddings
- [ ] Implement Lance vector store wrapper
- [ ] Implement embedding engine
- [ ] Create memory schema
- [ ] Add memory ingestion
- [ ] Write unit tests

### Week 3: Retrieval & CLI
- [ ] Implement semantic search
- [ ] Build CLI with Typer
- [ ] Add search command
- [ ] Add list/show commands
- [ ] Add delete command

### Week 4: LLM Integration & Polish
- [ ] Integrate llama.cpp
- [ ] Implement Q&A functionality
- [ ] Add memory stats
- [ ] Error handling & validation
- [ ] Documentation & examples
- [ ] Integration tests

## Code Structure

```
memory-agent/
├── src/
│   ├── memory_agent/
│   │   ├── __init__.py
│   │   ├── cli.py              # CLI interface (Typer)
│   │   ├── memory_manager.py   # Core orchestrator
│   │   ├── embeddings.py       # Embedding engine
│   │   ├── vector_store.py     # Lance wrapper
│   │   ├── llm.py              # LLM interface
│   │   ├── models.py           # Pydantic models
│   │   └── config.py           # Configuration
│   └── main.py                 # Entry point
├── tests/
│   ├── test_embeddings.py
│   ├── test_vector_store.py
│   ├── test_memory_manager.py
│   └── test_cli.py
├── scripts/
│   ├── download_models.py      # Download required models
│   └── setup.py                # Initial setup
└── docs/
    └── USAGE.md                # User guide
```

## Dependencies (MVP)

```
# Core
python>=3.10

# Vector & Embeddings
pylance>=0.10.0
sentence-transformers>=2.3.0

# LLM
llama-cpp-python>=0.2.0

# CLI & Utilities
typer>=0.9.0
rich>=13.0.0
pydantic>=2.0.0
pyyaml>=6.0

# Data
numpy>=1.24.0
pandas>=2.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
```

## Success Criteria

### Functional
- ✅ User can add memories via CLI
- ✅ User can search memories semantically
- ✅ Search returns relevant results (top-3 accuracy >80%)
- ✅ User can ask questions and get answers
- ✅ All data stored locally

### Technical
- ✅ Query latency <1s
- ✅ Support 10k memories
- ✅ Zero external API calls
- ✅ Test coverage >70%

### User Experience
- ✅ Simple, intuitive CLI
- ✅ Clear error messages
- ✅ Fast enough to use daily
- ✅ Reliable (no data loss)

## Demo Scenario

```bash
# Install
pip install memory-agent
memory setup

# Add some memories
memory add "Meeting with Alice about Q1 planning. She wants to focus on customer retention."
memory add "Read an article about RAG systems. Key insight: retrieval quality matters more than model size."
memory add "Coffee with Bob. He recommended trying the new Italian place downtown."

# Search
memory search "what did Alice say about Q1?"
# Returns: Meeting with Alice about Q1 planning...

# Ask
memory ask "What restaurants were recommended?"
# Returns: Bob recommended trying the new Italian place downtown...

# Stats
memory stats
# Total memories: 3
# Storage used: 245 KB
# Average query time: 0.3s
```

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Model downloads slow | High | Cache models, provide offline installers |
| Embedding quality poor | High | Test multiple models, allow swapping |
| Lance learning curve | Medium | Simple wrapper, fallback to FAISS |
| LLM hallucinations | Medium | Return sources, allow source verification |
| Performance on large datasets | Low | Not expected in MVP (<10k memories) |

## Next Steps After MVP

1. **User Testing**: Get feedback from 5-10 users
2. **Performance Profiling**: Identify bottlenecks
3. **Documentation**: Write comprehensive user guide
4. **Phase 2 Planning**: Prioritize next features based on feedback

---

**Target Completion**: End of Week 4 (2026-02-28)
