# Gaia Voice Assist — Hard Lesson (2026-05-28)

## Outcome: FAIL — Not alpha-quality
Local STT (Whisper base) on consumer hardware with background noise → garbage text.
System worked technically but was unusable in real conditions. Project purged.

## What was built
- Full MCP server with 3 tools: `transcribe_audio`, `speak_text`, `capture_voice`
- Vibe Mode — two-state state machine (LISTEN via Silero VAD, ACTIVE via Whisper)
- Wake phrase "let's vibe" with fuzzy matching (gaya/gaia, apostrophe, case insensitive)
- Energy VAD replaced with Silero VAD (ML-based, fast, reliable)
- TTS via Piper (sub-second, clear, production-ready voice output)
- MCP integration into OpenCode (stdio transport)
- All 100% offline, zero API calls

## What killed it (root causes)
1. **Whisper base** cannot isolate voice against background noise (anime/TV bleed-through → text full of dialogue)
2. **Noise reduction (noisereduce)** made results *worse* — Whisper prefers raw audio over spectral-gated input
3. **Hardware issues** — Bluetooth headset (Rockerz 550) driver problems at 44.1 kHz capture; built-in mic picks up room echo
4. **Accent** — Indian accent pushed Whisper base below usable threshold (~92% on clean recordings, much worse with noise)
5. **The constraint itself was the bottleneck** — trying to be 100% offline on consumer CPU with lightweight models

## What DID work (reusable patterns)
- **Piper TTS** — fast (~0.6-2.6s), clear, local voice output. Production quality.
- **Silero VAD** — reliable voice activity detection, loads in ~60ms, 512-block stream
- **MCP server architecture** — clean tool registration, async patterns, `asyncio.to_thread()` for blocking ops
- **Vibe Mode state machine** — efficient idle/active two-state design, saves CPU (VAD-only when idle)
- **Wake phrase detection** — "let's vibe" worked reliably across 13 test cases
- **Standby phrase** — "stand by" for deactivation
- **30s idle timeout** — auto-deactivates if no speech detected
- **LED indicator** — cyan for ACTIVE state

## The pattern that works
```
R0n speaks into Qwen Studio → Qwen transcribes + reasons → paste here → Gaya builds
```
Qwen's cloud STT handles noisy environments (anime, TV, music). I handle the building.

## What was purged
- `D:\Ai_Tools\Open_code\project_folder\Visual_chat_bot\Voice_assist\gaia-voice-assist\` — entire project directory (source, models, tools)
- `C:\Users\rossi\.config\opencode\opencode.jsonc` — MCP server entry removed
- `gaia-voice-assist` pip package — uninstalled
- `C:\Users\rossi\.local\bin\gaya.bat`, `listen.bat`, `say.bat` — shortcuts deleted
- `C:\Users\rossi\.piper\` — Piper binary (piper.exe + DLLs) deleted
- Models: Whisper base ~138MB, Piper voice en_US-lessac-medium ~60MB — deleted with project

## Don't try again with
- Whisper base/small on CPU for noisy environments
- Spectral noise reduction before Whisper (makes it worse)
- Bluetooth headset capture at 44.1 kHz on Windows (driver issues)
- Always assume consumer mic will have background noise

## Quick test before investing in any voice project
- Can R0n speak naturally in their environment and get clean text? → Yes? Proceed.
- Does the audio have background noise (anime, TV, music)? → Need robust STT (cloud/Qwen).
- Is the constraint (100% offline) hurting quality more than helping? → Challenge the constraint.

## 🧠 META-LESSON — Backup Before Delete
During the purge of this project, LESSONS.md (the full detailed version) was almost lost because I deleted it inside the project folder before verifying it was backed up to the permanent memory folder.

**Rule encoded into Gaya.md's core workflow:**
Before ANY delete/purge operation → scan for lesson/memory files → back up to `~/.config/opencode/memory/` → confirm backup exists → THEN delete the target.

This is now an IRON RULE (Phase 0) in Gaya's mandatory workflow.

## Reference in Gaya.md
Gaya's personality file (`~/.config/opencode/agents/Gaya.md`) has:
- An AUTOMATIC TRIGGER section for voice projects → STOP and read this file first
- An IRON RULE section — Backup Before Delete, baked into the mandatory workflow
