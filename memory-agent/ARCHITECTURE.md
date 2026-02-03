# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                   (CLI / Web UI / API)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                     Memory Manager                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Ingestion  │  │   Retrieval  │  │  Generation  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
┌────────▼──────┐ ┌──▼──────────┐ ┌▼────────────────┐
│   Embedding   │ │ Vector Store│ │  LLM Interface  │
│    Engine     │ │ (Lance/FAISS)│ │  (llama.cpp)    │
└───────────────┘ └──────────────┘ └─────────────────┘
         │            │                    │
         └────────────┼────────────────────┘
                      │
              ┌───────▼────────┐
              │  Storage Layer │
              │  (Local Files) │
              └────────────────┘
```

## Core Components

### 1. Memory Manager

**Responsibility**: Orchestrates all memory operations

**Key Functions**:
- `ingest(content, metadata)`: Store new memories
- `query(query_text, filters)`: Retrieve relevant memories
- `synthesize(query, memories)`: Generate contextual responses
- `consolidate()`: Summarize and compress old memories

**Implementation**:
- Central coordinator between components
- Manages transaction boundaries
- Handles error recovery
- Implements caching strategies

### 2. Embedding Engine

**Responsibility**: Convert text to vector representations

**Models**:
- Primary: `sentence-transformers/all-MiniLM-L6-v2` (lightweight, fast)
- Alternative: `BAAI/bge-small-en-v1.5` (better quality)
- Future: Multilingual support

**Features**:
- Batch processing for efficiency
- CPU/GPU auto-detection
- Model caching
- Dimension reduction options

**API**:
```python
class EmbeddingEngine:
    def embed(self, text: str) -> np.ndarray
    def embed_batch(self, texts: List[str]) -> np.ndarray
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float
```

### 3. Vector Store

**Responsibility**: Efficient similarity search

**Technology Options**:
- **Lance** (preferred): Modern columnar format, fast, versioned
- **FAISS**: Battle-tested, GPU support
- **Chromadb**: Simple, embedded option

**Index Strategy**:
- IVF (Inverted File Index) for large datasets
- HNSW for medium datasets
- Flat index for small datasets (<10k memories)

**Schema**:
```python
{
    "id": "uuid",
    "vector": "float32[384]",  # Embedding dimension
    "content": "text",
    "metadata": {
        "timestamp": "datetime",
        "source": "string",
        "tags": ["string"],
        "summary": "text"
    }
}
```

### 4. LLM Interface

**Responsibility**: Local language model operations

**Supported Backends**:
- **llama.cpp** (primary): Fast, CPU-optimized
- **Ollama**: User-friendly, good for prototyping
- **Transformers**: Flexible, more dependencies

**Models** (quantized):
- Default: `Llama-3.2-3B-Instruct-Q4_K_M.gguf` (~2GB)
- Alternative: `Mistral-7B-Instruct-v0.3-Q4_K_M.gguf` (~4GB)

**Operations**:
- Summarization
- Query expansion
- Contextual generation
- Classification/tagging

**API**:
```python
class LLMInterface:
    def generate(self, prompt: str, max_tokens: int) -> str
    def summarize(self, text: str, max_length: int) -> str
    def extract_keywords(self, text: str) -> List[str]
```

### 5. Audio Processing

**Responsibility**: Transcribe audio to text

**Technology**:
- **faster-whisper**: Optimized Whisper implementation
- Models: `tiny` (fast) to `medium` (accurate)

**Pipeline**:
1. Audio input (file or stream)
2. Preprocessing (normalization, VAD)
3. Transcription with timestamps
4. Speaker diarization (optional)
5. Store with audio metadata

### 6. Storage Layer

**Responsibility**: Persistent data management

**Structure**:
```
data/
├── vectors/           # Lance vector database
├── raw/               # Original content (optional)
├── cache/             # Embeddings cache
└── metadata.db        # SQLite for structured queries
```

**Features**:
- Incremental backups
- Compression (zstd)
- Encryption at rest (optional)
- Export to portable formats

## Data Flow

### Ingestion Flow

```
Input → Preprocessing → Chunking → Embedding → Storage
  ↓                                              ↓
Metadata Extraction                         Index Update
```

1. **Input**: Text, audio, or document
2. **Preprocessing**: Clean, normalize, detect language
3. **Chunking**: Split into semantic units (~500 tokens)
4. **Embedding**: Convert to vectors
5. **Storage**: Store vectors + metadata
6. **Index Update**: Update search index

### Retrieval Flow

```
Query → Embedding → Vector Search → Reranking → Context Assembly
                                          ↓
                                    LLM Generation → Response
```

1. **Query**: Natural language question
2. **Embedding**: Convert query to vector
3. **Vector Search**: Find top-k similar memories (k=20-50)
4. **Reranking**: Use cross-encoder or metadata filters
5. **Context Assembly**: Compile top results
6. **LLM Generation**: Synthesize answer with context
7. **Response**: Return answer + sources

## Technology Stack

### Core
- **Python 3.10+**: Main language
- **Lance**: Vector database
- **llama-cpp-python**: LLM inference
- **sentence-transformers**: Embeddings
- **faster-whisper**: Audio transcription

### Supporting
- **SQLite**: Metadata storage
- **FastAPI**: API server (optional)
- **Typer**: CLI framework
- **Rich**: Terminal UI
- **Pydantic**: Data validation

### Optional
- **Gradio**: Web UI prototype
- **PyTorch**: Custom model loading
- **FAISS**: Alternative vector store
- **Celery**: Background task processing

## Performance Considerations

### Latency Targets
- Ingestion: <5s per document
- Query: <1s for results
- Synthesis: <3s for response

### Scalability
- **Small**: <10k memories, flat index, ~1GB RAM
- **Medium**: <100k memories, IVF index, ~4GB RAM
- **Large**: <1M memories, GPU recommended, ~16GB RAM

### Optimization Strategies
1. **Lazy Loading**: Load models on demand
2. **Caching**: Cache embeddings and frequent queries
3. **Batch Processing**: Group operations
4. **Quantization**: Use INT8/Q4 models
5. **Index Tuning**: Optimize for query patterns

## Security & Privacy

### Threat Model
- **In Scope**: Local data protection, encryption at rest
- **Out of Scope**: Network attacks (no network component)

### Mitigations
- No telemetry or external calls
- Optional encryption (AES-256)
- Secure deletion (overwrite)
- Memory isolation
- Audit logging

### Data Retention
- User-controlled retention policies
- Automatic expiration options
- Soft delete with recovery window
- Full purge capability

## Extension Points

### Plugin Architecture
```python
class MemoryPlugin:
    def on_ingest(self, content, metadata): ...
    def on_query(self, query, results): ...
    def on_generate(self, prompt, response): ...
```

### Custom Embeddings
- Bring your own embedding model
- Domain-specific fine-tuning
- Multi-modal embeddings

### Custom Retrieval
- Hybrid search (vector + keyword)
- Graph-based retrieval
- Temporal decay functions

## Deployment

### Local Development
```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
python scripts/download_models.py
python src/main.py
```

### Production (Single User)
- Systemd service for background operation
- Periodic consolidation jobs
- Automated backups

### Multi-User (Future)
- Isolated data directories per user
- User authentication layer
- Resource quotas

## Monitoring & Debugging

### Metrics
- Query latency (p50, p95, p99)
- Index size growth
- Cache hit rates
- Model inference time

### Logging
- Structured JSON logs
- Configurable log levels
- Separate audit log for data operations

### Debug Tools
- Memory inspector (view stored embeddings)
- Query explainer (why these results?)
- Performance profiler

---

**Next Steps**: See [MVP.md](MVP.md) for the minimal implementation plan.
