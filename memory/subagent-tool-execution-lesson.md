# 🛠️ Subagent Tool Execution — Permanent Lesson

## Problem
When using `task` tool with `bob`, `Bob`, `freya`, or `Freya` subagent types, the agents return JSON describing tool calls but **never actually execute them**.

Example failure output:
```json
{"name": "write", "arguments": {"content": "...", "filePath": "..."}}
```

## Root Cause
1. **Ollama v0.24.0 had broken tool calling** — returned JSON string in `content` field instead of proper `tool_calls`. Fixed by upgrading to **v0.30.0**.
2. **Qwen 2.5 Coder 7B template uses wrong bracket format** — trained on `[tool_call]` format but Ollama default template uses `<tool_call>`. Fixed by creating `qwen2.5-coder-fixed:7b` model with modified template.
3. **Subagent type routing** — The `bob`/`freya` subagent types in opencode don't properly execute tool calls from local models. Only the `general` type works for tool execution.

## Verified Working Setup
- Ollama: **v0.30.0** (upgraded from v0.24.0)
- Bob's model: **qwen2.5-coder-fixed:7b** (tool-call patched)
- Freya's model: **qwen2.5-coder-fixed:7b** (same model, temp 0.7)
- Agent type for tool execution: **`general`** (NOT `bob`/`freya`)

## Fixed Model Creation
```powershell
# Export, patch, create fixed model
ollama show qwen2.5-coder:7b --modelfile > Modelfile
(Get-Content Modelfile) -replace '<tool_call>', '[tool_call]' -replace '</tool_call>', '[/tool_call]' | Set-Content Modelfile-fixed
ollama create qwen2.5-coder-fixed:7b -f Modelfile-fixed
```

## Working Pattern for Bob/Freya Tool Tasks
Since `bob`/`freya` types can't execute tools, use `general` type with their personality injected:

```text
task to general agent:
  "You are Bob the Builder — a no-nonsense implementation agent.
   [task instructions with tool calls]"
```

## Verification Test
```powershell
# Quick API test to confirm model works
curl -X POST http://localhost:11434/v1/chat/completions -d '{
  "model": "qwen2.5-coder-fixed:7b",
  "messages": [{"role":"user","content":"Create a test file"}],
  "tools": [{"type":"function","function":{"name":"write","description":"Write a file","parameters":...}}]
}'
# Expect: finish_reason: "tool_calls" with tool_calls array
```

## What Still Works Fine ✅
Bob and Freya work perfectly for **EDA (Explore/Data Analysis)** tasks using the `explore` agent type — that's always been their bread and butter. Research, code search, file reading, pattern analysis — no issues there. The limitation is ONLY about **active tool execution** (writing files, running commands, editing) through the `bob`/`freya` subagent types.

## What NOT to Do
- ❌ Don't use `task` with `bob`/`Bob`/`freya`/`Freya` subagent types for execution work
- ❌ Don't rely on Ollama < v0.30.0 for tool calling
- ❌ Don't use qwen2.5-coder:7b (original) - the template is wrong for tool calls
- ❌ Don't use dolphin-llama3:8b for tool calling - it doesn't support tools at all
