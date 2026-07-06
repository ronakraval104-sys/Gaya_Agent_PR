# Pattern: Voice Pipeline — Ambient Noise Profiling

**Domain:** Voice / Audio / STT  
**Source:** Gaya hardening log, 28-May-2026  
**Applies to:** Any project that needs local STT with noisy input

---

## The Pattern

```
Mic → normalize → RNNoise (ambient noise profile from first 500ms)
     → energy VAD (trim silence, merge nearby speech)
     → volume normalize → Whisper small → 95%+ accuracy
```

## Key Parameters

| Stage | Setting | Why |
|---|---|---|
| Noise profiling | First ~500ms of audio capture | Profiles ambient noise before user speaks |
| RNNoise | Spectral subtraction lib | Strips steady-state noise (fans, AC, hum) |
| Energy VAD | Numpy-based threshold | Removes silence before/after speech |
| Volume norm | Peak normalize to -3dBFS | Consistent input level for Whisper |
| Whisper model | small (244M params) | Good accuracy/speed tradeoff |
| Temperature | Default fallback chain | Recovery from garbled audio |
| no_speech_threshold | 0.3 | Prevents valid speech rejection |

## When to Use
- Local STT on consumer hardware
- Noisy environments (open offices, home with TV, coffee shops)
- Real-time or near-real-time voice capture

## When NOT to Use
- Clean studio audio → raw Whisper is fine
- Cloud STT available → always prefer cloud for noisy environments
- Need multilingual → use Whisper multilingual model instead

## Alternative: Cloud-Reliant Pattern
```
Mic → cloud STT (Qwen, OpenAI, Deepgram) → text → local processing
```
Better accuracy in noise, requires internet.
