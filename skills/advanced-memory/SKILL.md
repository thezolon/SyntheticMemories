# Advanced Memory Skill

**Offline semantic memory system with vector search, importance scoring, and three-tier hierarchy.**

## What This Does

Gives OpenClaw persistent, searchable memory using:
- **LanceDB** for vector storage (offline, embedded)
- **Ollama** for embeddings (local, no API costs)
- **Importance scoring** (auto-curate what matters)
- **Three-tier hierarchy** (Global → User → Session)

## Architecture

```
Global Memory (tier=global)
  ├─ OpenClaw docs, skills, general knowledge
  └─ Shared across all users/sessions
  
User Memory (tier=user)
  ├─ Personal preferences, projects, people
  └─ Tied to specific user (e.g., "Zolon")
  
Session Memory (tier=session)
  ├─ Current conversation context
  └─ Temporary, can be promoted to user/global
```

## Usage

### Store a Memory

```bash
# High-importance user preference
advanced-memory store "User prefers dark UI themes" --tier=user --importance=8

# Session-specific context
advanced-memory store "Currently debugging 3CX Docker setup" --tier=session --importance=5

# Global knowledge
advanced-memory store "LanceDB is an embedded vector database" --tier=global --importance=9
```

### Recall Memories

```bash
# Semantic search (uses embeddings)
advanced-memory recall "what are the user's UI preferences?"

# Tier-specific search
advanced-memory recall "what Docker projects are active?" --tier=user

# Limit results
advanced-memory recall "VoIP" --limit=3
```

### Auto-Curate MEMORY.md

```bash
# Extract high-importance items from daily logs
advanced-memory curate --from=memory/2026-02-01.md --threshold=7

# Preview without writing
advanced-memory curate --from=memory/2026-02-01.md --threshold=7 --dry-run
```

### Service Management

```bash
# Start service
cd ~/.openclaw/workspace/skills/advanced-memory
docker compose up -d

# Check status
advanced-memory status

# View logs
docker compose logs -f advanced-memory

# Stop service
docker compose down
```

## API Reference

**Base URL:** `http://localhost:8768`

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
- `query` (required): Search query
- `tier` (optional): Filter by tier (global|user|session)
- `user_id` (optional): Filter by user
- `limit` (optional): Max results (default: 5)
- `min_importance` (optional): Minimum importance score

**Response:**
```json
{
  "results": [
    {
      "content": "User prefers dark themes",
      "tier": "user",
      "importance": 8,
      "similarity": 0.92,
      "metadata": { ... }
    }
  ],
  "query": "UI preferences",
  "count": 1
}
```

### POST /curate
Extract high-importance memories from a file and update MEMORY.md.

**Request:**
```json
{
  "source_file": "/home/zolon/.openclaw/workspace/memory/2026-02-01.md",
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

**File:** `config.yml`

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
    retention: forever
  user:
    retention: 1year
  session:
    retention: 30days
```

## Importance Scoring Guide

**0-3:** Noise (don't store)
- "okay", "got it", "thanks"

**4-6:** Context (store, low priority)
- Session-specific details
- Temporary decisions
- Work-in-progress notes

**7-8:** Important (curate to MEMORY.md)
- User preferences
- Project decisions
- Key learnings

**9-10:** Critical (always keep)
- Core identity facts
- Major milestones
- Security credentials (encrypted)

## Integration with OpenClaw

This skill is designed to **augment** (not replace) OpenClaw's built-in memory system:

1. **OpenClaw's `memory_search`** still works (searches MEMORY.md + daily files)
2. **Advanced Memory** adds semantic search and auto-curation
3. **Use both:** `memory_search` for quick text search, `advanced-memory recall` for semantic

### Recommended Workflow:

**During conversation:**
- Store important facts: `advanced-memory store "fact" --tier=user`
- Recall context: `advanced-memory recall "query"`

**During heartbeats:**
- Auto-curate daily logs: `advanced-memory curate --from=memory/$(date +%Y-%m-%d).md`

**Manual review:**
- Check what's been learned: `advanced-memory recall "everything about user preferences" --limit=20`

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
```bash
# Check memory count
advanced-memory status

# Verify embeddings stored
docker exec advanced-memory ls -lh /data/memory.lance
```

## Development

**Local development (without Docker):**

```bash
cd ~/.openclaw/workspace/skills/advanced-memory

# Install dependencies
pip install -r requirements.txt

# Run service
python service/memory_service.py

# Test
curl http://localhost:8768/health
```

## Future Enhancements

- [ ] Web UI (like Kairos session browser)
- [ ] Memory visualization (knowledge graph)
- [ ] Automatic importance scoring (ML-based)
- [ ] Memory decay (fade unimportant items over time)
- [ ] Cross-reference detection (link related memories)
- [ ] Export/import (backup/restore)
- [ ] Analytics dashboard (what has OpenClaw learned?)

---

**Status:** 🚧 In Development  
**Version:** 0.1.0  
**License:** MIT  
**Author:** Built for OpenClaw workspace
