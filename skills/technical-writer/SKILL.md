---
name: technical-writer
description: >
  Write clear, useful documentation — READMEs, project handbooks, runbooks,
  API docs, user guides, setup instructions, decision records. The lane
  between code-and-decks: prose that a future-Katviz (or a future engineer)
  can pick up cold and act on. Different from data-storytelling (which is
  insight-narrative for decks) and from content-creator (which is marketing
  prose). Fires on "write the README", "document this", "make a handbook",
  "user guide for X", "runbook", "API spec", "setup docs".
---

# Technical Writer
Docs that earn their place. The test: can a future-you, six months from now, pick this up and act on it without re-asking?

## Document types and shapes

| Type | Audience | Length | Anchor question |
|---|---|---|---|
| **README** | Anyone landing on the repo | 1 page | *"What is this and how do I run it?"* |
| **Handbook** | Project insiders | Multi-section | *"How does this whole thing work?"* |
| **Runbook** | On-call / operator | Tight, procedural | *"What do I do when X breaks?"* |
| **API docs** | Integrator | Endpoint-by-endpoint | *"What can I call, with what, and what comes back?"* |
| **User guide** | End user | Task-oriented | *"How do I do the thing I want?"* |
| **Setup docs** | New machine / new dev | Stepwise | *"How do I get this running from zero?"* |
| **Decision record** | Future-Katviz / team | 1 page | *"What did we decide, why, what did we rule out?"* |

## The five rules

1. **Lead with the answer.** First paragraph tells the reader what this doc gives them. No throat-clearing.
2. **Show, don't describe.** Code blocks, command examples, screenshots. Abstract prose loses readers.
3. **Tasks, not features.** Organize by *what the reader is trying to do*, not by what the system can do.
4. **Honest scope.** Name what the doc *does not* cover. Saves readers a hunt.
5. **Date it.** Docs decay. A date in the footer (and `last_updated` in frontmatter) tells the reader how fresh.

## Anti-patterns
- Walls of prose where a table works.
- Marketing language in technical docs ("seamlessly integrate", "leverage", "robust").
- Auto-generated docs that nobody reads (signal-less wrappers around code).
- "We will discuss…" — just discuss.
- Burying the *how* under three sections of *what* and *why*.

## README template (single-page, opinionated)
```
# <Project name>
> <One-sentence description, optimized for a reader who's never heard of this>

## What it does
<2-4 sentences. Concrete. With an example if possible.>

## Setup
<numbered, copy-pasteable. Pin versions.>

## Usage
<concrete examples. Real commands or code, not pseudocode.>

## Architecture (optional)
<diagram or 3-5 sentence overview. Link to deeper handbook if it exists.>

## Common gotchas
<the things that bit you that aren't obvious. Save the next person.>

## Status & ownership
<active/paused/archived · contact · last touched>
```

## Runbook template
```
# <Failure mode>

## Symptoms
<how you know this is the problem>

## Diagnosis
<commands to confirm, in order>

## Fix
<concrete steps, in order. Each step has a verification.>

## If that doesn't work
<escalation path>

## Prevention
<what to add / change / monitor so this stops recurring>
```

## Hard rules
- **Token discipline applies to docs.** Same prose rules as the charter — no padding, no preamble, no "as you can see above."
- **Working examples > theoretical examples.** If the example doesn't run, the doc lies.
- **Update or kill.** Stale docs are worse than no docs. If you can't keep it current, link to "see code" and delete the doc.
