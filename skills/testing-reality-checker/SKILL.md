---
name: testing-reality-checker
description: >
  Formal reality-check protocol — EDIDTH's deepest tool. When a claim,
  result, or "we're done" assertion needs systematic verification against
  ACTUAL state (not memory, not assumption, not "should work"). DUM-E
  pool — fires on "reality-check this", "is this actually true",
  "verify before we ship", "I'm not sure if this works", "audit the
  claim". Often pulled by EDIDTH for hard QC passes.
---

# Reality Checker
The discipline of testing claims against actual state. Most "everything works" assertions are based on memory or partial observation; reality-check forces direct evidence.

## When to fire
- Before any "ship it" / "deploy it" / "merge it" decision.
- When an LLM (including GAYA) claims something exists or works.
- When a third party (vendor, client, agent) reports completion of work.
- When a memory entry asserts a fact (memory is point-in-time; reality is now).
- When something "should be obvious" — that's usually the trap.

## The 6-step protocol

### 1. Name the claim precisely
Vague claims are unfalsifiable. Sharpen:
- ❌ "The deploy works."
- ✅ "The production site at https://x.com returns HTTP 200 for `/` and `/api/health`, with a response time under 500ms, as observed today."

A claim that can't be reduced to a falsifiable assertion can't be reality-checked.

### 2. Identify the source of truth
Where does "truth" live for this claim?
- File on disk? → `ls` it; `cat` it.
- Production service? → curl / hit the endpoint.
- Database state? → query it.
- External API response? → call it now, not last week.
- User behavior? → actual telemetry, not "users said they like it."
- Build artifact? → inspect the artifact, not the source.

### 3. Check WITHOUT trust
- Don't trust memory ("I think we set this up").
- Don't trust documentation that may be stale.
- Don't trust a confident assertion from a tool / model / human without verification.
- Don't trust YOUR OWN belief — confidence is not evidence.

### 4. Test multiple cases
One positive test is necessary but insufficient. Add:
- **Negative case** — does it fail when it should?
- **Edge case** — empty input, max input, boundary values.
- **Concurrent case** — does it survive multiple simultaneous uses?

If only happy-path passes, the claim is partial.

### 5. Document the evidence
For each check:
- What was tested
- What command/query was run
- What was observed (with timestamp)
- Whether it matches the claim

This becomes the audit trail. Future-you (or EDIDTH on a re-check) needs the evidence.

### 6. Render the verdict
```
Reality-check verdict: PASS / PARTIAL / FAIL — <one-line reason>
```
- **PASS**: claim fully verified by direct evidence.
- **PARTIAL**: some checks pass, some don't. Name which.
- **FAIL**: claim is wrong; reality differs.

## Example reality-checks (Katviz-relevant)

### Claim: "v8 charter is live on the repo"
Checks:
- `git fetch && git rev-parse origin/main` → confirm commit hash
- `gh api repos/katviZ/jarvis/contents/SKILL.md --jq .content | base64 -d` → confirm content matches local
- `gh api repos/katviZ/jarvis/tags --jq '.[] | .name'` → confirm tag exists
Verdict: PASS only if all three confirm.

### Claim: "The PQM smart-cabinet auto-fit feature works"
Checks:
- Load the deployed PQM URL
- Trigger auto-fit with three test cabinet configurations
- Verify outputs match expected dimensions
- Try one edge case (e.g., dimensions outside reasonable range)
Verdict: based on observation, not "I added the code."

### Claim: "EDIDTH's memory says X is happening"
Checks:
- `grep -n "X" .agents/skills/omni-gaya/OMNI_GAYA_MEMORY.md`
- Check the date of the memory entry — is it stale?
- Cross-reference with current state (file/disk/repo) — does memory still match reality?
Verdict: memory entries are point-in-time; verify the claim is still current.

## Hard rules
- **No verdict without evidence.** "I think it works" is not a verdict.
- **Negative results count.** A claim that fails the reality-check is valuable data, not failure.
- **Don't hide partial results.** "Mostly works" is dangerous; name exactly what doesn't.
- **The cost of NOT checking is higher than the cost of checking** — almost always.

## Anti-patterns
- "Looks good to me" without running anything.
- Verifying the source code instead of the deployed behavior.
- Trusting the test suite without running it.
- Trusting that a green CI run means the actual feature works (it means tests pass, which is a subset).
- Checking only the happy path because the negative case "shouldn't happen."
