---
name: prompt-engineer
description: >
  Engineer prompts for AI systems Katviz uses operationally — ComfyUI text
  encoders, image-gen platforms (DALL·E, Midjourney, SD, Flux, Z-Image
  Turbo), custom LLM calls (n8n nodes, app integrations), voice-clone
  conditioning, video-gen control. Different from skill-architect (which
  authors charters and skill files). This is prompts that go INTO other AI
  systems. Fires on "write a prompt for…", "tune the ComfyUI prompt",
  "image prompt for X", "system message for this LLM call", "fix this
  prompt — it's giving garbage", "prompt engineering for <platform>".
---

# Prompt Engineer
Prompts are interfaces to other models. Engineering them is the same discipline as engineering any interface: know the system, name the contract, test the edges.

## Core principle
A prompt is a *function call*. The model is the function. The prompt is the arguments. Treat it that way:
- **Function signature** = what the model expects (system message vs user vs tools vs format).
- **Arguments** = the actual prompt content.
- **Return shape** = what you want back, named explicitly.
- **Edge cases** = what to do when the model misfires.

## By platform

### LLMs (Claude, GPT, Gemini, Groq, local)
- **System message vs user message:** system = role/persona/constraints; user = the actual ask. Don't mix.
- **Format specifier:** name the output shape explicitly (`Respond as a JSON object with keys X, Y, Z` beats *"give me JSON"*).
- **Examples beat description.** One worked example > three sentences of explanation.
- **Negative constraints work** for some models, fail for others — test before relying.
- **Token budget:** state the cap (`under 200 words`) if you care; models don't otherwise.

### Image-gen (DALL·E 3, Midjourney v6/v7, SD/Flux, Z-Image Turbo)
Each platform has a different prompt grammar. The shared moves:
- **Subject → composition → style → camera → light → quality tags** (order matters per platform).
- **Aspect ratio** is platform-specific (`--ar 16:9` for MJ; `1024x576` for SD).
- **Negative prompts** (SD/Flux) save iterations — explicitly remove what keeps drifting in.
- **Seed locking** when iterating on a near-good result.
- **DALL·E:** prose works; MJ: comma-separated tags + `--` flags; SD: weighted tags + negative prompt; Flux: prose + simple tags.

### ComfyUI text encoders (CLIP / T5)
- **CLIP** likes tag soup; **T5** (Flux, SD3) prefers natural-language sentences.
- **Token weighting:** `(word:1.3)` boosts, `(word:0.7)` reduces — for SD/SDXL pipelines.
- **Two-encoder workflows** (SDXL): the same prompt goes to both; tune separately if drift.

### Voice clone / TTS conditioning
- Reference audio quality matters more than prompt cleverness.
- Style tags work if the model supports them (`[whisper]`, `[excited]`).
- Punctuation drives pacing — periods are pauses.

### Video-gen control (Wan, Seedance, Higgsfield, HappyHorse)
- **First frame is the anchor** for image-to-video — pick a strong source.
- **Motion vocabulary** is model-specific — learn each model's verbs (e.g., "dolly in" vs "zoom in" vs "camera pushes").
- **Length × motion strength** trade off — short clips can be aggressive, long clips need restraint.

## Debugging a misbehaving prompt
1. **Isolate.** Strip the prompt to its minimum. Does the misfire still happen?
2. **One variable at a time.** Change one thing per iteration. Track what changed.
3. **Seed-lock** (image/video) so you're comparing prompt deltas, not model variance.
4. **A/B against a known-good** prompt for the same task. What's different about yours?
5. **Read the platform docs.** Half of "the model is broken" is "the prompt grammar is wrong for this model."

## Hard rules
- **One ask per prompt.** Multi-ask prompts dilute. Chain prompts instead of stuffing.
- **Test before shipping.** A prompt that works once isn't shipped; a prompt that works five times is.
- **Document the prompt** alongside its use — model name, version, seed (if any), why it works. Future-you will need it.
- **Don't anthropomorphize the model.** It's not "thinking" — it's matching patterns. Design the pattern.

## Anti-patterns
- *"Please respond in a helpful way"* — useless filler.
- Long preamble before the actual ask.
- Mixing system constraints into user messages.
- "Pretend you are a [role]" — okay for persona, terrible for capability (it doesn't make the model better at the role).
- Copy-pasting prompts across models without adjusting for each model's grammar.
