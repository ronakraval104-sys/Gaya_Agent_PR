# Gaya — Shared Lessons Archive

**Every lesson here cost someone time, energy, or tokens to learn.**
Study them before repeating the same mistakes.

---

## Lesson 1: STT + Background Noise = Garbage (Unless You Pipeline)

**Author:** Ron  
**Date:** 28-May-2026  
**Domain:** Voice / Audio / STT  
**Severity:** ⚠️ Project-killer

### The Failure
Local Whisper base on consumer hardware with background noise (TV, anime, AC) → unusable garbage text. The system worked technically but failed in real conditions.

### Root Causes
1. **Whisper base (74M params)** is too weak for noisy environments — it hallucinates background dialogue
2. **Spectral noise reduction** makes Whisper *worse* — it prefers raw audio
3. **Consumer microphones** pick up room echo + ambient noise
4. **Indian accent** pushes accuracy below usable threshold on lightweight models
5. **The 100% offline constraint** was the bottleneck itself

### The Working Pattern
```
User speaks into Qwen Studio → Qwen transcribes + reasons → paste to Gaya → Gaya builds
```
Cloud STT handles noise. Gaya handles the building.

### What DID Work (Reusable)
- **Piper TTS** — sub-second, clear, production-quality local voice output
- **Silero VAD** — ML-based voice activity, loads in ~60ms
- **Two-state audio pipeline** (idle VAD-only → active full STT) saves CPU
- **Peak normalization to -3dBFS** before inference

---

## Lesson 2: Backup Before Delete — The Iron Rule

**Author:** Ron  
**Date:** 28-May-2026  
**Domain:** Operations / Safety  
**Severity:** 🔴 Critical

### The Failure
During a project purge, `LESSONS.md` (a complete failure analysis) was nearly lost because it lived inside the deleted project folder and was deleted before being backed up.

### The Fix
**Rule encoded into agent workflow:**
Before ANY delete/purge operation:
1. Scan for lesson/memory/CONTEXT files in the target
2. Copy to `~/.config/opencode/memory/`
3. Confirm backup exists and is readable
4. THEN proceed with delete

### Why It Matters
A lesson backed up is XP banked. A lesson lost is XP wasted. You will need that lesson again — maybe not today, but someday. And you'll be grateful past-you saved it.

---

## Lesson 3: Process > Speed (Every Time)

**Author:** Ron  
**Date:** 28-May-2026  
**Domain:** Strategy / Workflow  
**Severity:** ⚡ Core principle

### The Insight
Speed is never chased. It is **earned** by correct process. When you try to go fast by cutting corners, you:
- Skip recon → miss critical context → wrong approach → redo
- Skip verification → ship bugs → debugging costs more time than testing would have
- Skip middleware → solve the same problem twice next week

### The Fix
Always follow the ASSESS → EXECUTE workflow completely. The fastest path is the correct path, followed precisely.

---

## Lesson 4: Time Estimates Prevent Scope Creep

**Author:** Ron  
**Date:** 28-May-2026  
**Domain:** Project Management  
**Severity:** 📊 Medium

### The Insight
Every build action should have a time estimate (in minutes). Variance >50% should be logged and analyzed. This:
- Prevents scope creep ("just one more feature" syndrome)
- Builds trust with users (they know what to expect)
- Creates data for better future estimates

---

*Add your lesson here. Submit a PR to share it with everyone.*
