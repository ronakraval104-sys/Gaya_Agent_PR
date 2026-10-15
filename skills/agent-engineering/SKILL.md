---
name: agent-engineering
description: Build LLM apps and AI agents in code — API wiring for Anthropic, Groq, and OpenAI; tool/function calling loops; voice I/O (STT/TTS); local vs cloud model serving; Python venv setup, dependency management, API-key handling, and simple deploys. Use when building, debugging, or wiring an AI agent/app, integrating an LLM SDK, or setting up the runtime around one.
---

# Agent Engineering
Build the machine around the model — cleanly, cheaply, and so it doesn't break when the base Python moves.

## Provider wiring
- **Anthropic** (`anthropic`): Messages API, `system` + `tools` (name/description/input_schema), tool-use loop, prompt caching for repeated context.
- **Groq** (`groq`): OpenAI-style `chat.completions`, free tier, `llama-3.3-70b-versatile` for tool use; tools as `{type:"function", function:{name,description,parameters}}`, results as `role:"tool"`.
- **OpenAI** (`openai`): same OpenAI tool schema; reuse the Groq path.
- Pick by need: Groq for free+fast, Claude when quality > cost. Keep a thin adapter so the brain is provider-swappable.

## Tool-use loop (the core pattern)
Send messages + tools → if `tool_calls`, execute each, append results, loop → else return final text. Keep a `TOOL_MAP` of name→function; convert one canonical tool schema to each provider's format.

## Voice I/O
- STT: `faster-whisper` (local, `int8` on CPU); record to wav, transcribe. VAD/silence-stop for natural turns.
- TTS: `edge-tts` (free neural voices) → mp3 → play via `sounddevice`/`soundfile`.

## Runtime hygiene (hard-won)
- Build venvs against a **stable installed Python**, not an auto-updating managed one — if the base Python version shifts, compiled wheels (pydantic_core, etc.) break with `ModuleNotFoundError`. Rebuild venv on version drift.
- `run.bat`: set key → activate venv → run → **`pause`** so error windows don't flash-close.
- Never commit/share API keys; load from env. Rotate anything leaked.

## Anti-patterns
Hardcoded keys, no error surface on crash, mixing provider message formats, assuming a moved venv still works.
