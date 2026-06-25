# Lessons Learned — Project Folder

**Last updated:** 19-Jun-2026

## How to Use
- Add new lessons at the TOP
- Be specific: code snippets, paths, error messages
- Include what went wrong AND what fixed it

---

## [20-Jun-2026] Freeze Causes + Bob→Tvashtar
- **DB bloat is #1 freeze cause** — 1.46 GB opencode.db with 67k events, 67k messages/parts. The `event` table is 1.15 GB alone. Prune by keeping last 20 sessions, deleting old ones with CASCADE.
- **Skill path variables don't expand on Windows** — `${HOME}` and `${PROJECT_ROOT}` produce paths like `D:\project\${HOME}\.agents\skills`. Fix: use absolute paths with forward slashes (`C:/Users/rossi/.agents/skills`).
- **Bob renamed to Tvashtar** — The Divine Craftsman persona. All system files updated: config (agent key), persona, protocol, agents, memory, context.
- **OLLAMA_KEEP_ALIVE=0** — Set as permanent user env var. Models release VRAM immediately after inference instead of holding it for 5 minutes.
- **@opencode-ai/plugin@local** — Hardcoded in OpenCode binary app.asar, not in config. Cannot fix. Accept as startup delay.
- **VCS watcher on node_modules** — OpenCode binary limitation. `.opencode/.gitignore` has `node_modules` but VCS doesn't respect it. Cannot fix from config.

## [19-Jun-2026] MoE Memory Architecture
- Created per-agent persona files in `~/.config/opencode/memory/`
- Created session-thread.md for cross-agent handoff
- Created `.opencode/` in project root for project-level context
- Key principle: always read thread + local context before any action
- Update protocol: refresh all memories every 3-5 milestones

## [19-Jun-2026] Ollama Model Names
- `qwen3:4b` does NOT exist as a model name — must use `qwen3:4b-instruct-2507-q4_K_M`
- `qwen/qwen3-4b-instruct-2507` is the HuggingFace path, NOT the Ollama name
- Ollama models from HF need GGUF format — safetensors won't pull directly
- Official Ollama library names are often verbose but reliable

## [19-Jun-2026] PowerShell + Ollama
- Polling progress from Ollama in PowerShell produces ANSI escape noise in output
- The "NativeCommandError" on successful commands is just PowerShell being noisy
- Check `ollama list` to verify instead of parsing pull output
