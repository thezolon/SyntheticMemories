# OpenClaw Advanced Memory

**Offline semantic memory system for OpenClaw using LanceDB and Ollama**

Give your OpenClaw agent persistent, searchable memory with vector embeddings—completely offline, no API costs.

## Features

- 🧠 **Semantic search** - Find memories by meaning, not just keywords
- 🔒 **100% offline** - Uses local Ollama for embeddings (no cloud APIs)
- 💾 **Persistent storage** - LanceDB vector database
- 📊 **Importance scoring** - Automatically prioritizes what matters
- 🏗️ **Three-tier hierarchy** - Global → User → Session memory organization
- 🐳 **Docker-based** - Isolated service that survives OpenClaw updates
- 🛠️ **CLI tools** - Easy integration with OpenClaw workflows

## How It Works

```
User Query ("what are my UI preferences?")
          ↓
   Ollama Embedding (nomic-embed-text)
          ↓
   LanceDB Vector Search
          ↓
   Semantic Results ("User prefers dark themes")
```

**Example:**
```bash
# Store a memory
advanced-memory store "User prefers dark UI themes" --tier user

# Semantic recall
advanced-memory recall "design preferences"

# Returns:
# - "User prefers dark themes" (similarity: 452.6)
```

The system finds related memories even if the exact words don't match—that's the power of vector embeddings!

## Architecture

### Components

- **FastAPI Service** - REST API + WebSocket server (port 8768)
- **LanceDB** - Embedded vector database (no separate server needed)
- **Ollama** - Local embedding generation (`nomic-embed-text` model)
- **CLI Scripts** - Shell wrappers for easy integration

### Memory Tiers

```
GLOBAL (tier=global)
  ├─ System knowledge, tools, capabilities
  └─ Shared across all users/sessions
  
USER (tier=user)
  ├─ Personal preferences, projects, people
  └─ Tied to specific user (e.g., "zolon")
  
SESSION (tier=session)
  ├─ Current conversation context
  └─ Temporary, can be promoted to user/global
```

### Importance Scoring (0-10)

- **0-3:** Noise (not stored) - "okay", "thanks", simple acknowledgments
- **4-6:** Context (stored, low priority) - session details, work-in-progress
- **7-8:** Important (curated to MEMORY.md) - user preferences, key decisions
- **9-10:** Critical (always kept) - core facts, major milestones

## Prerequisites

- Docker + Docker Compose
- Ollama installed locally
- `nomic-embed-text` model pulled: `ollama pull nomic-embed-text`
- jq (for CLI scripts)

## Installation

### 1. Clone the Repository

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/thezolon/openclaw-advanced-memory.git advanced-memory
cd advanced-memory
```

### 2. Build and Start Service

```bash
docker compose build
docker compose up -d
```

### 3. Verify Health

```bash
curl http://localhost:8768/health | jq .
```

Expected output:
```json
{
  "status": "healthy",
  "ollama_connected": true,
  "embedding_model": "nomic-embed-text",
  "db_path": "/data/memory.lance",
  "memory_count": 0
}
```

### 4. (Optional) Install CLI Globally

```bash
sudo ln -s ~/.openclaw/workspace/skills/advanced-memory/scripts/advanced-memory /usr/local/bin/advanced-memory
```

## Usage

### Store Memories

```bash
# Basic storage (auto-scored importance)
advanced-memory store "User prefers dark themes" --tier user

# Manual importance score
advanced-memory store "Critical security note" --tier global --importance 9

# With user ID
advanced-memory store "Meeting scheduled for 3pm" --tier session --user alice
```

### Recall Memories (Semantic Search)

```bash
# Find by meaning
advanced-memory recall "what are the user's design preferences?"

# Tier-specific search
advanced-memory recall "what Docker projects are active?" --tier user

# Limit results
advanced-memory recall "VoIP" --limit 3

# Minimum importance threshold
advanced-memory recall "important decisions" --min-importance 7
```

### Auto-Curate Daily Logs

Extract high-importance items from daily markdown files and append to MEMORY.md:

```bash
# Curate yesterday's notes
advanced-memory curate --from memory/2026-02-01.md --threshold 7

# Preview without writing
advanced-memory curate --from memory/2026-02-01.md --dry-run
```

### Service Management

```bash
# Check status
advanced-memory status

# View logs
docker compose logs -f advanced-memory

# Restart service
docker compose restart

# Stop service
docker compose down
```

## API Reference

Base URL: `http://localhost:8768`

### POST /store

Store a new memory with embedding and importance score.

**Request:**
```json
{
  "content": "User prefers dark themes",
  "tier": "user",
  "user_id": "zolon",
  "importance": 8,
  "metadata": {
    "source": "conversation",
    "timestamp": "2026-02-01T08:00:00Z"
  }
}
```

**Response:**
```json
{
  "success": true,
  "memory_id": "mem_1234567890",
  "importance": 8,
  "tier": "user"
}
```

### GET /recall

Semantic search across stored memories.

**Query Parameters:**
- `query` (required) - Search query
- `tier` (optional) - Filter by tier (global|user|session)
- `user_id` (optional) - Filter by user
- `limit` (optional) - Max results (default: 5)
- `min_importance` (optional) - Minimum importance score

**Example:**
```bash
curl "http://localhost:8768/recall?query=design+preferences&tier=user&limit=3"
```

**Response:**
```json
{
  "results": [
    {
      "content": "User prefers dark themes",
      "tier": "user",
      "importance": 8,
      "similarity": 452.63,
      "timestamp": "2026-02-01T08:00:00Z"
    }
  ],
  "query": "design preferences",
  "count": 1
}
```

### POST /curate

Extract high-importance memories from a file and update MEMORY.md.

**Request:**
```json
{
  "source_file": "/path/to/memory/2026-02-01.md",
  "threshold": 7,
  "dry_run": false
}
```

**Response:**
```json
{
  "extracted": 5,
  "appended_to_memory": true,
  "items": [
    {
      "content": "User wants to self-host 3CX in Docker",
      "importance": 8
    }
  ]
}
```

### GET /health

Service health check.

**Response:**
```json
{
  "status": "healthy",
  "ollama_connected": true,
  "embedding_model": "nomic-embed-text",
  "db_path": "/data/memory.lance",
  "memory_count": 142
}
```

## Configuration

Edit `config.yml` to customize behavior:

```yaml
service:
  port: 8768
  host: 0.0.0.0

ollama:
  host: http://host.docker.internal:11434
  model: nomic-embed-text
  timeout: 30

lancedb:
  path: /data/memory.lance
  
memory:
  default_tier: user
  importance_threshold: 5  # Min importance to store
  curate_threshold: 7      # Min importance for MEMORY.md
  
tiers:
  global:
    retention_days: -1  # Forever
  user:
    retention_days: 365
  session:
    retention_days: 30
```

## Integration with OpenClaw

### From Agent Code (via exec)

```javascript
// Store a memory
await exec(`advanced-memory store "User wants X" --tier user`);

// Recall context
const result = await exec(`advanced-memory recall "what does user want?"`);
const memories = JSON.parse(result.stdout);

// Auto-curate during heartbeat
await exec(`advanced-memory curate --from memory/${today}.md --threshold 7`);
```

### Heartbeat Integration Example

Add to `HEARTBEAT.md`:

```markdown
## Memory Maintenance

Every heartbeat:
- Curate yesterday's log if not done: `advanced-memory curate --from memory/YYYY-MM-DD.md`
```

## Troubleshooting

### Service won't start

```bash
# Check Ollama is running
ollama list

# Check Docker logs
docker compose logs advanced-memory

# Verify port availability
netstat -tuln | grep 8768
```

### Embeddings failing

```bash
# Test Ollama directly
curl http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "test"
}'

# Pull embedding model if missing
ollama pull nomic-embed-text
```

### Poor recall results

Check if memories are being stored:
```bash
advanced-memory status

# Should show memory_count > 0
```

### Database corruption

Reset the database (destroys all memories):
```bash
docker compose down
sudo rm -rf data/memory.lance
docker compose up -d
```

## Performance

- **Storage:** ~1-2ms per memory (including embedding generation)
- **Recall:** ~10-50ms for semantic search across 1000+ memories
- **Embedding model:** `nomic-embed-text` (274MB, 768-dimensional vectors)
- **Database size:** ~1KB per memory (vector + metadata)

## Roadmap

- [ ] Web UI for browsing memories (like Kairos session browser)
- [ ] Memory visualization (knowledge graph)
- [ ] Automatic importance scoring via ML
- [ ] Memory decay (fade unimportant items over time)
- [ ] Cross-reference detection (link related memories)
- [ ] Export/import (backup/restore)
- [ ] Analytics dashboard ("What has OpenClaw learned?")
- [ ] Multi-user support with isolated contexts

## License

MIT

## Credits

Built for [OpenClaw](https://openclaw.ai) - The open-source AI agent framework.

Uses:
- [LanceDB](https://lancedb.github.io/lancedb/) - Fast embedded vector database
- [Ollama](https://ollama.ai/) - Local LLM and embedding server
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework

## Contributing

This is a personal workspace skill, but if you find it useful and want to contribute:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

Questions? Issues? Open a GitHub issue or find me on the [OpenClaw Discord](https://discord.com/invite/clawd).

---

**Built with ❤️ for better AI memory**
