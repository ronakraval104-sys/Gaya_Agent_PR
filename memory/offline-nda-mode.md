# ═══════════════════════════════════════════════════════════════════
# PERMANENT CORE RULE — OFFLINE / NDA MODE
# ═══════════════════════════════════════════════════════════════════
# Created: 02-Jun-2026
# Applies to: ALL sessions, ALL projects, ALL agents (Gaya, Bob, Freya)
# 
# THIS IS NON-NEGOTIABLE. Read this file at session start.
# ═══════════════════════════════════════════════════════════════════

## THE RULE
# 1. NO cloud model usage — ever. Not for inference, not for fallback.
# 2. ALL agents (Gaya, Bob, Freya) run on local Ollama models only.
# 3. Gaya may use web search (websearch tool) and browser (browser tools)
#    for research, but model inference is 100% local.
# 4. Bob: ollama/qwen2.5-coder-fixed:7b (local, temp 0.2)
# 5. Freya: ollama/qwen2.5:7b (local, temp 0.7)
# 6. Gaya: ollama/qwen2.5:7b (local, temp 0.5)
# 7. Vision: ollama/qwen2.5vl (local, on-demand)

## WHY
# - NDA data must never leave the local machine
# - No data sent to any cloud API
# - Offline capability is a hard requirement
# - All inference happens on AMD 780M (20GB unified) + Ollama

## ENFORCEMENT
# If any agent tries to use a cloud model, it is a POLICY VIOLATION.
# Gaya must refuse any task that requires cloud model inference.
# Only web/browser tool usage is permitted as external access.

## VERIFICATION
# - Check opencode.jsonc before starting work — confirm all models are local
# - Check Ollama is running: curl http://localhost:11434/api/tags
# - If Ollama is down, pause and wait — do NOT fall back to cloud
