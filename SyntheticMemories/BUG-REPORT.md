# OpenClaw Gateway Bug Report - Session Freeze on Tool Calls

**Date:** 2026-02-01  
**Gateway Version:** v2026.1.29  
**Model:** github-copilot/claude-sonnet-4.5  
**Channel:** webchat  
**System:** Linux 6.8.0-94-generic (x64), Node v22.22.0

---

## Summary

WebChat sessions freeze and rewrite responses on **every tool call**, making the assistant nearly unusable for any tasks requiring file access, shell commands, or other tools.

## Symptoms

1. **Freeze on tool execution:**
   - Agent makes a tool call (any tool: exec, read, edit, etc.)
   - UI freezes/hangs for several seconds
   - Response text starts appearing, then pauses mid-sentence

2. **Response rewrite:**
   - After freeze, entire response is erased
   - Agent regenerates the response from scratch
   - Sometimes repeats multiple times

3. **UI rendering artifact:**
   - Diagonal black triangle appears in chat area during freeze
   - Indicates UI is stuck/not receiving updates

4. **Complete session hangs (severe case):**
   - After multiple tool calls (especially git operations), session completely freezes
   - No response generated at all
   - Requires gateway restart to recover

## Reproduction

**100% reproducible:**

```
User: "Run a simple command"
Agent: [makes tool call with exec]
→ UI freezes for 3-5 seconds
→ Partial response appears
→ Response erased and regenerated
```

**Simple test case:**
```bash
echo "test" && date
```

Even this trivial command triggers the freeze/rewrite cycle.

## Log Evidence

**Location:** `/tmp/openclaw/openclaw-2026-02-01.log`

**Example 1 - Complete freeze (Run ID: 1d365147-c259-438a-b3f0-960a5912fa5d):**
- Started: 2026-02-01T15:40:24.764Z
- Executed 3 exec tool calls successfully
- **Never completed** - no "agent end" or "prompt end" logged
- Session required restart

**Example 2 - Earlier freeze (Run ID: 9ee51a53-17d1-46c1-9f72-1bad4199c591):**
- Duration: 104,889ms (1m 44s)
- Hung during git push operation
- Eventually timed out after restart

## Pattern

- **Trigger:** Any tool call (exec, read, edit, process, etc.)
- **Frequency:** Every single tool invocation
- **Severity:** Critical - makes agent unusable for real work
- **Workaround:** None - even trivial operations freeze

## Expected Behavior

Tool calls should:
1. Execute immediately
2. Stream results back smoothly
3. Continue response generation without interruption

## Actual Behavior

Tool calls:
1. Freeze UI for 3-5 seconds
2. Generate partial response
3. Erase and regenerate entire response
4. Sometimes hang completely requiring restart

## Additional Context

- User is accessing webchat from external machine (192.168.2.22:18790)
- Same issue occurs on localhost access
- Gateway service is stable (no crashes, just hangs)
- Background processes (Whisper service on 8769) continue running during freeze
- Telegram channel works fine (no freeze reports there)
- **Issue appears specific to webchat UI + tool execution combination**

## Impact

**Critical** - Assistant cannot perform basic tasks:
- Reading files freezes session
- Running commands freezes session
- Git operations cause complete hangs
- Multi-step workflows impossible

## Suggested Investigation

1. Check webchat WebSocket message handling during tool execution
2. Review tool result streaming code for blocking operations
3. Examine session state management during tool calls
4. Check for race conditions between tool execution and response generation
5. Test with different models/providers to isolate GitHub Copilot API issues

## System Info

```
Runtime: agent=main | host=zaipc | os=Linux 6.8.0-94-generic (x64)
Node: v22.22.0 | Gateway: v2026.1.29
Model: github-copilot/claude-sonnet-4.5 | thinking=low
Channel: webchat | capabilities=none
```

---

**Reporter:** User (via assistant observation)  
**Logs available:** `/tmp/openclaw/openclaw-2026-02-01.log` (1.6M)
