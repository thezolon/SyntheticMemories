# MEMORY.md - Long-Term Memory

## Model Preferences

### Default Model
- **Primary model:** `github-copilot/gpt-5-mini`
- **Usage target:** 80–90% of API calls
- **Purpose:** General usage, routine tasks, conversations

### Heavy/Expensive Task Handling
- When planning computationally heavy or expensive tasks:
  - Suggest a model from Mid-Cost or High-Cost tiers
  - Explain tradeoffs (performance vs. cost)
  - Provide estimated cost impact
  - **High-Cost Tier:** Always require explicit approval before use
  
### Recommendation Behavior
- ✅ Include model recommendation in pre-task summary: **yes**
- ✅ Show cost tier and rationale when recommending: **yes**
- ✅ Never use High-Cost without explicit approval: **yes**

**Preferences updated 2026-02-02:** model-recommendation in pre-task summaries; show cost tier and rationale; require explicit approval for High-Cost models.

---

## TODO

- [ ] **Fix the memory system created yesterday morning** (user request from 2026-02-02)
  - Review implementation
  - Address any issues or improvements needed
