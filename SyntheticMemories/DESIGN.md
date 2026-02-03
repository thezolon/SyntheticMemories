# SyntheticMemories Design Document

## Overview

SyntheticMemories is a biologically-inspired memory system that implements three distinct memory types based on human cognitive architecture: **episodic**, **semantic**, and **procedural** memory. Memories are interconnected through associative links and governed by a retention and rehearsal mechanism inspired by spaced repetition and memory consolidation research.

---

## Core Memory Types

### 1. Episodic Memory
Episodic memories represent specific events or experiences bound to a particular time and context.

**Schema:**
```json
{
  "id": "uuid",
  "type": "episodic",
  "timestamp": "ISO8601",
  "content": {
    "description": "string",
    "location": "string (optional)",
    "participants": ["string (optional)"],
    "sensory_details": {
      "visual": "string (optional)",
      "auditory": "string (optional)",
      "emotional": "string (optional)"
    }
  },
  "tags": ["string"],
  "retention": {
    "strength": 1.0,
    "last_accessed": "ISO8601",
    "rehearsal_count": 0,
    "next_rehearsal": "ISO8601",
    "consolidated": false
  },
  "links": ["memory_id"]
}
```

**Example:**
```json
{
  "id": "ep-2026-02-01-meeting",
  "type": "episodic",
  "timestamp": "2026-02-01T14:30:00Z",
  "content": {
    "description": "Team meeting discussing Q1 goals",
    "location": "Conference Room B",
    "participants": ["Alice", "Bob", "Charlie"],
    "sensory_details": {
      "visual": "whiteboard filled with roadmap sketches",
      "emotional": "energized and optimistic"
    }
  },
  "tags": ["work", "planning", "team"],
  "retention": {
    "strength": 1.0,
    "last_accessed": "2026-02-01T14:30:00Z",
    "rehearsal_count": 0,
    "next_rehearsal": "2026-02-02T14:30:00Z",
    "consolidated": false
  },
  "links": ["sem-okr-framework", "ep-2026-01-15-kickoff"]
}
```

---

### 2. Semantic Memory
Semantic memories represent general knowledge, facts, and concepts independent of personal experience context.

**Schema:**
```json
{
  "id": "uuid",
  "type": "semantic",
  "created": "ISO8601",
  "updated": "ISO8601",
  "content": {
    "concept": "string",
    "definition": "string",
    "properties": {
      "key": "value"
    },
    "relationships": {
      "is_a": ["string"],
      "part_of": ["string"],
      "related_to": ["string"]
    }
  },
  "tags": ["string"],
  "retention": {
    "strength": 1.0,
    "last_accessed": "ISO8601",
    "rehearsal_count": 0,
    "next_rehearsal": "ISO8601",
    "consolidated": false
  },
  "links": ["memory_id"]
}
```

**Example:**
```json
{
  "id": "sem-okr-framework",
  "type": "semantic",
  "created": "2025-11-20T10:00:00Z",
  "updated": "2026-02-01T14:30:00Z",
  "content": {
    "concept": "OKR (Objectives and Key Results)",
    "definition": "A goal-setting framework for defining and tracking objectives and their outcomes",
    "properties": {
      "components": ["Objectives", "Key Results"],
      "cycle_length": "quarterly",
      "origin": "Intel, popularized by Google"
    },
    "relationships": {
      "is_a": ["goal-setting framework", "management methodology"],
      "related_to": ["KPIs", "agile planning"]
    }
  },
  "tags": ["business", "productivity", "management"],
  "retention": {
    "strength": 0.85,
    "last_accessed": "2026-02-01T14:30:00Z",
    "rehearsal_count": 3,
    "next_rehearsal": "2026-03-01T14:30:00Z",
    "consolidated": true
  },
  "links": ["ep-2026-02-01-meeting", "proc-run-okr-planning"]
}
```

---

### 3. Procedural Memory
Procedural memories represent "how-to" knowledge: skills, processes, and step-by-step instructions.

**Schema:**
```json
{
  "id": "uuid",
  "type": "procedural",
  "created": "ISO8601",
  "updated": "ISO8601",
  "content": {
    "skill": "string",
    "description": "string",
    "steps": [
      {
        "order": "integer",
        "action": "string",
        "details": "string (optional)"
      }
    ],
    "prerequisites": ["string (optional)"],
    "success_criteria": ["string (optional)"]
  },
  "tags": ["string"],
  "retention": {
    "strength": 1.0,
    "last_accessed": "ISO8601",
    "rehearsal_count": 0,
    "next_rehearsal": "ISO8601",
    "consolidated": false,
    "proficiency": 0.0
  },
  "links": ["memory_id"]
}
```

**Example:**
```json
{
  "id": "proc-run-okr-planning",
  "type": "procedural",
  "created": "2025-12-01T09:00:00Z",
  "updated": "2026-01-10T11:00:00Z",
  "content": {
    "skill": "Conducting OKR planning sessions",
    "description": "How to facilitate quarterly OKR planning with a team",
    "steps": [
      {
        "order": 1,
        "action": "Review previous quarter's OKRs",
        "details": "Assess completion rates and lessons learned"
      },
      {
        "order": 2,
        "action": "Brainstorm objectives",
        "details": "Focus on 3-5 ambitious but achievable goals"
      },
      {
        "order": 3,
        "action": "Define key results",
        "details": "2-5 measurable outcomes per objective"
      },
      {
        "order": 4,
        "action": "Validate and commit",
        "details": "Ensure alignment and team buy-in"
      }
    ],
    "prerequisites": ["Understanding of OKR framework"],
    "success_criteria": [
      "Clear, measurable key results defined",
      "Team consensus achieved",
      "Objectives aligned with company strategy"
    ]
  },
  "tags": ["process", "management", "planning"],
  "retention": {
    "strength": 0.92,
    "last_accessed": "2026-02-01T14:30:00Z",
    "rehearsal_count": 5,
    "next_rehearsal": "2026-03-03T14:30:00Z",
    "consolidated": true,
    "proficiency": 0.75
  },
  "links": ["sem-okr-framework", "ep-2026-02-01-meeting"]
}
```

---

## Memory Links

Links represent associative connections between memories, enabling network-based retrieval and context-aware recall.

**Schema:**
```json
{
  "id": "uuid",
  "type": "link",
  "created": "ISO8601",
  "source_id": "memory_id",
  "target_id": "memory_id",
  "relationship": "string",
  "strength": 1.0,
  "bidirectional": true
}
```

**Relationship Types:**
- `triggered_by`: One memory recalls another
- `related_to`: General association
- `exemplifies`: Episodic example of semantic concept
- `uses`: Procedural memory uses semantic knowledge
- `occurred_during`: Temporal co-occurrence
- `caused_by`: Causal relationship

**Example:**
```json
{
  "id": "link-001",
  "type": "link",
  "created": "2026-02-01T14:35:00Z",
  "source_id": "ep-2026-02-01-meeting",
  "target_id": "sem-okr-framework",
  "relationship": "exemplifies",
  "strength": 0.95,
  "bidirectional": true
}
```

---

## Retention and Rehearsal System

The memory system implements a **two-stage retention model** inspired by human memory consolidation:

### Short-Term Memory
- **Half-life:** 7 days (default)
- Newly created memories start with `strength = 1.0`
- Strength decays exponentially if not accessed or rehearsed

### Long-Term Memory (Consolidated)
- **Half-life:** 90 days (default)
- Memories transition to consolidated state after sufficient rehearsals
- More resistant to decay

### Decay Formula
```
strength(t) = strength_0 * (0.5) ^ (days_elapsed / half_life)
```

### Rehearsal Schedule
Memories are scheduled for review at increasing intervals (spaced repetition):

**Default intervals (days after creation/last rehearsal):**
```
[1, 7, 30]
```

- **Day 1:** First review (reinforces initial encoding)
- **Day 7:** Second review (moves toward consolidation)
- **Day 30:** Third review (solidifies long-term retention)

After the third rehearsal, a memory is marked as `consolidated: true` and transitions to the long-term half-life.

### Rehearsal Effects
Each rehearsal:
1. Resets decay timer (`last_accessed = now`)
2. Increases `rehearsal_count`
3. Boosts `strength` (optional: add +0.1, capped at 1.0)
4. Schedules next rehearsal based on interval array
5. After completing the schedule, marks memory as consolidated

### Configuration Defaults
```json
{
  "retention_config": {
    "short_half_life_days": 7,
    "long_half_life_days": 90,
    "rehearsal_intervals_days": [1, 7, 30],
    "consolidation_threshold": 3,
    "strength_boost_per_rehearsal": 0.1,
    "decay_check_interval_hours": 24
  }
}
```

---

## Implementation Notes

### Memory Creation
1. Generate unique ID
2. Set `strength = 1.0`
3. Set `last_accessed = now`
4. Set `next_rehearsal = now + rehearsal_intervals[0]`
5. Store with `consolidated = false`

### Memory Access
1. Update `last_accessed = now`
2. Optionally boost `strength` slightly
3. Propagate activation to linked memories (optional)

### Rehearsal Processing
Run periodic job (e.g., daily):
1. Query memories where `next_rehearsal <= now`
2. For each:
   - Increment `rehearsal_count`
   - Update `last_accessed = now`
   - Boost `strength`
   - If `rehearsal_count >= consolidation_threshold`, set `consolidated = true`
   - Schedule next rehearsal or mark as complete

### Decay Processing
Run periodic job (e.g., daily):
1. For each memory:
   - Calculate days since `last_accessed`
   - Apply decay formula based on half-life (short or long)
   - Update `strength`
   - Optionally prune memories below threshold (e.g., strength < 0.1)

---

## Example Workflow

### Day 0: User learns about OKRs
1. Create semantic memory `sem-okr-framework` with strength 1.0
2. Schedule first rehearsal for Day 1

### Day 1: First rehearsal
1. System prompts review of OKR concept
2. Update `last_accessed`, `rehearsal_count = 1`, `strength = 1.0` (boosted)
3. Schedule next rehearsal for Day 8 (1 + 7)

### Day 8: Second rehearsal
1. User reviews OKR definition
2. Update `rehearsal_count = 2`
3. Schedule next rehearsal for Day 38 (8 + 30)

### Day 38: Third rehearsal & consolidation
1. User reviews OKR concept again
2. Update `rehearsal_count = 3`
3. Mark `consolidated = true`
4. Memory now uses long-term half-life (90 days)

### Ongoing
- Memory decays slowly over 90-day half-life
- Each access resets decay timer
- Strong associative links keep related memories active

---

## Future Enhancements
- **Adaptive rehearsal intervals** based on individual memory performance
- **Importance weighting** (critical memories rehearse more frequently)
- **Cluster-based retrieval** (activate memory neighborhoods)
- **Emotion-weighted encoding** (emotional events = stronger initial strength)
- **Forgetting simulation** (intentional pruning of low-strength memories)

---

## References
- Ebbinghaus forgetting curve
- Spaced repetition research (Pimsleur, SuperMemo)
- Human memory systems (Tulving's episodic/semantic distinction)
- Memory consolidation theory (Dudai, McGaugh)
