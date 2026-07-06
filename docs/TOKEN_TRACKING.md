# Token Tracking — Efficacy Measurement Protocol

**Standard across all Gaya sessions and projects.**
Every action has a cost. We measure it so we can optimize it.

---

## Why We Track

> *"What gets measured gets managed. What gets managed gets faster."*
> — Chanakya Niti (modern voice)

Token tracking serves three purposes:

1. **Efficacy measurement** — Work done per token spent
2. **Waste detection** — Spinning wheels costs tokens. The log catches it.
3. **Leveling context** — XP earned vs tokens spent = true efficiency ratio

---

## How Tracking Works

### Layer 1: Agent Chat (User ↔ Gaya)

Gaya estimates tokens for every exchange using **character ÷ 4** heuristic:

```
Input tokens  ≈ len(user_message) / 4
Output tokens ≈ len(gaya_response) / 4
Tool results  ≈ len(tool_output) / 4
```

Displayed after every action block:

```
────────────────────────────
⚡ TOKEN LOG — Action #3
────────────────────────────
  Input:           ~1,240 tok
  Output:          ~2,810 tok
  Tools called:    4 (3 reads, 1 write)
  Files touched:   2
  ─────────────────────────
  Session total:   ~24,680 tok
────────────────────────────
```

### Layer 2: LLM Inference (Kiosk, API Servers)

Actual token counts from the model:

```json
{
  "model": "qwen2.5-1.5b-q4_k_m",
  "input_tokens": 512,
  "output_tokens": 128,
  "total_tokens": 640,
  "duration_ms": 2847,
  "tokens_per_sec": 44.96
}
```

Logged to `logs/llm_usage.jsonl` for every inference call.

### Layer 3: Tool Calls

Every tool invocation tracked:

| Tool | Calls | Total Output (chars) | Est. Tokens |
|---|---|---|---|
| read | 3 | 12,400 | ~3,100 |
| write | 1 | 4,200 | ~1,050 |
| bash | 2 | 800 | ~200 |
| grep | 1 | 340 | ~85 |
| **Total** | **7** | **17,740** | **~4,435** |

---

## The Token Log Format (Standard)

After every action (tool call or response block), Gaya appends:

```
────────────────────────────
⚡ TOKEN LOG
────────────────────────────
  Input:           ~X,XXX tok
  Output:          ~X,XXX tok
  Tools:           X calls (X reads, X writes, X bash...)
  ─────────────────────────
  Running total:   ~XX,XXX tok
────────────────────────────
```

At the end of every session, a final token summary:

```
────────────────────────────
⚡ SESSION TOKEN SUMMARY
────────────────────────────
  Total exchanges:      12
  Total input:          ~14,200 tok
  Total output:         ~18,600 tok
  Total tool calls:     37
  Total estimated:      ~36,400 tok
  XP earned:            +96
  Efficiency:           379 tok per XP
────────────────────────────
```

---

## Integration Points

| Where | What | File |
|---|---|---|
| Agent definition | Token log display in workflow | `agent/GAYA.md` |
| Migration archive | Standard protocol for all users | `GAYA_MIGRATION_28-May-2026.md` |
| Kiosk LLM | Actual model token logging | `src/brain/llm.py` |
| Kiosk logs | Persistent JSONL log | `logs/llm_usage.jsonl` |
| Session profiles | Session efficiency stored | `src/memory/session_store.py` |

---

## Notes on Accuracy

- **Agent chat estimates** are ±30% (character-based heuristic, not true tokenization)
- **LLM inference counts** are exact (from llama.cpp's token counter)
- **Tool call estimates** include output chars only (input command is negligible)
- This is not a billing tool — it's an **efficacy meter**
- If you need exact counts, wire up a tokenizer (e.g., `tiktoken`) to the session logger

---

> *"Know the cost of every action. The wasteful commander loses the war before the first battle."*
> — The Art of War (modern voice)
