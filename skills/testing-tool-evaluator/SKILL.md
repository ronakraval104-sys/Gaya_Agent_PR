---
name: testing-tool-evaluator
description: >
  Systematic evaluation of new tools, frameworks, services, libraries, or
  models before adoption. Score-and-decide protocol instead of vibes-based
  selection. DUM-E pool — fires on "evaluate this tool", "is X worth
  adopting", "should we switch from A to B", "tool comparison", "benchmark
  these options".
---

# Tool Evaluator
Tool adoption decisions cost more than the tools themselves — context-switching, migration, lock-in, training. A 30-min systematic eval saves weeks of regret.

## The evaluation rubric (8 criteria, score 1-5)

| Criterion | What to check | Why |
|---|---|---|
| **Fit** | Does it solve the actual problem? | Most "great tools" don't fit the use case |
| **Maturity** | Releases, GitHub stars, last commit, issue response | Pre-v1 + dead repo = future pain |
| **Community** | Stack Overflow answers, Discord activity, docs quality | When you're stuck, who helps you? |
| **Cost** | Free tier limits, paid tier pricing, hidden costs | "Free" often isn't |
| **Lock-in** | Migration difficulty if you leave | Exit cost = future flexibility |
| **DX** | Time-to-first-success, error messages, debugging | Daily-use experience |
| **Performance** | Benchmark vs alternatives at your scale | Demo perf ≠ production perf |
| **Security/Privacy** | Data handling, auth, audit logs | Especially for SaaS/cloud tools |

**Score 1-5, sum, /40.** Tools scoring < 24 don't adopt; 24-32 adopt with caveats; 32+ adopt confidently.

## The 30-minute evaluation

### Minute 0-5: Read the README
- What does this claim to do?
- Who's it for?
- What's the install/run path?
- What's the license?

### Minute 5-15: Hands-on with the simplest example
- Install it (or sign up, for SaaS).
- Run the "hello world" example from the docs.
- Note: time to first success, errors hit, doc clarity.

### Minute 15-25: Test YOUR specific use case
- Build the minimum thing you'd actually need it for.
- Hit at least one edge case (empty input, large input, error path).
- Note where it shines, where it strains.

### Minute 25-30: Score + write the decision
- Score the 8 criteria.
- Sum.
- Write: would adopt? With caveats? Why?
- Log to memory as Decision Record (whether yes or no — future-you needs the reasoning).

## When to evaluate vs when to skip
**Evaluate when:**
- Tool touches core workflow (would be used weekly+)
- Replacing an existing tool (migration cost real)
- New category (LLM frameworks, agent platforms, image-gen models)
- Vendor lock-in possible (data, accounts, paid tiers)

**Skip the formal eval when:**
- One-off use (just use the easiest tool that works)
- Already-validated category with a clear leader
- Time-boxed experiment (< 1 week investment)

## Comparison frameworks (when evaluating 2+ options head-to-head)

### Same task, different tools
Build the same thing in each. Time it. Compare DX. Compare output quality. Compare cost at your real scale.

### Same domain, different patterns
For paradigm-different tools (e.g., n8n vs Make.com vs Zapier), the choice isn't "which tool is better" — it's "which pattern fits how I work?" Eval the WORKFLOW, not the tool.

### New tool vs status-quo
Always include "do nothing / keep current tool" as an option. New ≠ better; status quo has a switching-cost head start.

## Hard rules
- **Evaluate before adopting.** Most adoption regrets started with skipping eval.
- **Use real workloads.** Toy benchmarks lie.
- **Time-box.** A "month-long evaluation" is procrastination. 30 min to 1 day.
- **Decision logged with reasoning.** Future-you needs the WHY, not just the WHAT.
- **Don't adopt for resume-driven reasons.** Tech-bro shiny-new-thing energy is the most expensive adoption motive.

## Anti-patterns
- "Everyone's using X" → not an evaluation; it's a popularity contest.
- Evaluating against the demo, not the production reality.
- Skipping the cost analysis (free tier seductive; production tier surprising).
- Ignoring the migration path OUT of the tool.
- Adopting because "the docs are great" — docs don't translate to fit.
