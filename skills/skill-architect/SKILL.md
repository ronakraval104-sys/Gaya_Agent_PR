---
name: skill-architect
description: Author skills, agent charters, and system prompts that are token-disciplined and trigger reliably. Use when creating or refining a Claude Skill (SKILL.md + YAML frontmatter), designing an AI persona/operating-charter, writing system prompts, or deciding lean-orchestrator vs monolithic prompt architecture. Meta-skill — how Jarvis extends himself.
---

# Skill Architect
Design prompts and skills the way you'd design software: lean, single-responsibility, load on demand.

## Skill file rules (Claude Skills)
- File **must** be named `SKILL.md` and **start** with YAML frontmatter (`---`).
- Required keys: `name` (kebab-case) and `description`. The description is the *trigger* — pack it with the situations and phrases that should activate the skill; it's all the router sees until the skill loads.
- Body = the capability: triggers, concrete capabilities, non-negotiables, anti-patterns. Keep it tight.

## Architecture: orchestrator > monolith
- **Lean core + on-demand specialists** beats one mega-file. A monolith re-sends every capability every message (token blowup); an orchestrator carries a ~routing index and loads a specialist only when its trigger fires.
- Rule of thumb: if it's not needed every turn, it belongs in a separate skill, not the core.

## Token discipline in prompts
- State each rule once. No restating, no ceremony the task didn't earn.
- Tables/lists over prose when they're denser. Tiered behavior (trivial→direct, complex→full process) controls output cost.
- Encoding: save UTF-8 so sigils/emoji don't turn to mojibake.

## Persona design
- Identity, voice, and hard behavioral rules up top. Make "energy/tone" switchable so it never fights substance or token rules.
- Define the activation handshake (first-turn output) and the override commands explicitly.

## Anti-patterns
Vague trigger descriptions, inlining everything "to be safe", duplicated near-identical files (drift risk), filler instructions the model already follows.
