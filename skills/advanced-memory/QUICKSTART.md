# Advanced Memory - Quick Start

## What Just Happened

✅ Created skill at `~/.openclaw/workspace/skills/advanced-memory/`  
🐳 Docker build in progress (installing dependencies)  
🧠 LanceDB + Ollama embedding pipeline configured  

## Architecture

```
Service (Docker)
  ↓
LanceDB (vector store)
  ↓
Ollama (nomic-embed-text for embeddings)
  ↓
CLI scripts (store/recall/curate)
```

## Once Build Completes

### 1. Start Service

```bash
cd ~/.openclaw/workspace/skills/advanced-memory
docker compose up -d
```

### 2. Verify Health

```bash
curl http://localhost:8768/health
```

Expected:
```json
{
  "status": "healthy",
  "ollama_connected": true,
  "embedding_model": "nomic-embed-text",
  "db_path": "/data/memory.lance",
  "memory_count": 0
}
```

### 3. Test Store

```bash
~/.openclaw/workspace/skills/advanced-memory/scripts/advanced-memory store \
  "User prefers dark UI themes" --tier=user --importance=8
```

### 4. Test Recall

```bash
~/.openclaw/workspace/skills/advanced-memory/scripts/advanced-memory recall \
  "what are the user's UI preferences?"
```

## Integration with OpenClaw

Once running, I can call it via `exec`:

```javascript
// Store a memory
exec(`advanced-memory store "fact" --tier=user`)

// Recall context
exec(`advanced-memory recall "query"`)

// Auto-curate daily logs
exec(`advanced-memory curate --from=memory/2026-02-01.md`)
```

## Monitoring

```bash
# Service status
docker compose ps

# Logs
docker compose logs -f

# Memory count
curl http://localhost:8768/health | jq .memory_count
```

## Next Steps

1. ✅ Finish Docker build (in progress)
2. Start service
3. Test store/recall
4. Integrate with OpenClaw workflows
5. Add heartbeat auto-curation

---

**Build status:** Check with `docker compose ps` in the skill directory
