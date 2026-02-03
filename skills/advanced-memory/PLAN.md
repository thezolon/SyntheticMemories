# Advanced Memory Enhancement Plan

**Goal:** Expand advanced-memory skill with local GPU-powered features while maintaining 100% offline operation.

## Phase 1: LLM-Powered Importance Scoring ✅ PRIORITY

**Why:** Replace keyword-based scoring with actual language understanding for better curation.

**Tasks:**
- [ ] Add Ollama LLM client to importance_scorer.py
- [ ] Create scoring prompt template
- [ ] Use lightweight model (phi-3.5-mini or qwen2.5:7b)
- [ ] Add config option to toggle LLM vs keyword scoring
- [ ] Benchmark speed (should be <2s per item)
- [ ] Test on sample memories
- [ ] Update curate command to use LLM scoring

**Expected improvement:** 30-50% better accuracy in identifying important content.

---

## Phase 2: Whisper Audio Transcription Container ✅ PRIORITY

**Why:** Store and search spoken context (voice memos, meeting recordings, audio notes).

**Tasks:**
- [ ] Create whisper-transcribe service directory
- [ ] Write Dockerfile (openai/whisper base image or faster-whisper)
- [ ] Create FastAPI service for transcription
- [ ] Expose REST endpoint: POST /transcribe (upload audio file)
- [ ] Configure docker-compose.yml with GPU support
- [ ] Add model selection (tiny/base/small/medium - balance speed vs accuracy)
- [ ] Test with sample audio file
- [ ] Add CLI script: `advanced-memory transcribe <audio-file>`
- [ ] Auto-store transcriptions as memories with audio metadata
- [ ] Document supported formats (mp3, wav, m4a, etc.)

**Models to test:**
- `whisper-tiny` - Fast, good for quick notes
- `whisper-base` - Balanced
- `whisper-small` - Better accuracy, still fast on GPU

**Integration points:**
- Upload audio → transcribe → auto-score importance → store if threshold met
- Store audio file path as metadata for reference
- Optional: store audio embeddings for semantic audio search

---

## Phase 3: Question Answering (RAG)

**Why:** Answer questions using stored memories instead of just returning raw results.

**Tasks:**
- [ ] Create /ask endpoint
- [ ] Implement RAG pipeline:
  - Embed query → search memories → format context → send to LLM
- [ ] Use mid-size model (llama3.1:8b or qwen2.5:7b)
- [ ] Add conversation history support (multi-turn Q&A)
- [ ] Return sources (which memories were used)
- [ ] Add CLI: `advanced-memory ask "question"`
- [ ] Web UI: Add "Ask" tab with chat interface
- [ ] Test with complex queries

**Example:**
```
User: "What VoIP projects am I working on?"
System: 
  1. Searches memories for VoIP
  2. Finds: 3CX self-hosting, Google Voice number
  3. Sends to LLM: "Based on these memories, answer..."
  4. Returns: "You're planning to self-host 3CX in Docker and have a Google Voice number..."
```

---

## Phase 4: Auto-Summarization

**Tasks:**
- [ ] Add /summarize endpoint
- [ ] Long memory → LLM → concise summary
- [ ] Store both full + summary versions
- [ ] Use summary for display in UI
- [ ] Add "expand" button to show full content
- [ ] Batch summarize existing memories

---

## Phase 5: Memory Enrichment

**Tasks:**
- [ ] Auto-extract entities (people, projects, tools, dates)
- [ ] Generate tags/categories using LLM
- [ ] Detect memory relationships (references, dependencies)
- [ ] Add graph view in UI (memory connections)
- [ ] Store structured metadata (entity types, relationships)

---

## Phase 6: Vision Support (llava:7b)

**Tasks:**
- [ ] Add image embedding support
- [ ] Create /store-image endpoint
- [ ] Use llava to generate image descriptions
- [ ] Store both image embedding + text description
- [ ] Search images semantically
- [ ] Web UI: display thumbnails
- [ ] Support screenshot workflow (clipboard → memory)

---

## Phase 7: Memory Consolidation

**Tasks:**
- [ ] Detect duplicate/similar memories (cosine similarity)
- [ ] Suggest merges in UI
- [ ] LLM-powered merge (combine related memories)
- [ ] Automatic deduplication job (weekly cron)
- [ ] Archive old/stale memories

---

## Phase 8: Advanced Analytics

**Tasks:**
- [ ] Memory timeline visualization
- [ ] Top topics (cluster analysis)
- [ ] Importance distribution graph
- [ ] Growth over time chart
- [ ] Search heatmap (what you search for most)

---

## Implementation Order

**Week 1:**
1. ✅ Phase 1: LLM Importance Scoring (2-3 hours)
2. ✅ Phase 2: Whisper Transcription (3-4 hours)

**Week 2:**
3. Phase 3: Question Answering (4-5 hours)
4. Phase 4: Auto-Summarization (2-3 hours)

**Week 3+:**
5. Phase 5-8: As needed/requested

---

## Success Criteria

- [ ] All features work 100% offline (no cloud API calls)
- [ ] GPU utilization stays under 50% during normal operations
- [ ] Response times remain <5s for interactive operations
- [ ] Memory database can scale to 10,000+ items
- [ ] All features accessible via CLI + Web UI
- [ ] Comprehensive error handling and logging

---

## Notes

**Hardware Available:**
- Dual RTX 5060 Ti (32GB VRAM total)
- AMD Ryzen 9 9900X3D (24 threads)
- 91GB RAM
- 80+ local Ollama models

**Models to Use:**
- **Embeddings:** nomic-embed-text (current), snowflake-arctic-embed-m-long (upgrade option)
- **Importance scoring:** phi-3.5-mini, qwen2.5:7b
- **Q&A/Summarization:** llama3.1:8b, qwen2.5:7b
- **Vision:** llava:7b
- **Transcription:** whisper-small (will add)

**Constraints:**
- Keep container footprint reasonable (<10GB per service)
- All services must be Docker-based (survive OpenClaw updates)
- CLI + Web UI for all features
- Maintain fast response times (human-interactive)
