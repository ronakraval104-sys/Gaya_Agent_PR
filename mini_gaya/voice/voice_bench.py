"""Local voice benchmark for JARVIS - no cloud, no subscriptions.

    python voice_bench.py            # TTS samples (3 voices) + STT round trip + timings

TTS : Kokoro-82M via kokoro-onnx (Apache-2.0), CPU
STT : faster-whisper (CTranslate2) - CPU int8, and CUDA if the GTX 1070 is usable
Writes samples to ~/.jarvis/voice/samples/ so Boss can listen and pick J's voice.
"""
import os
import sys
import time

HOME = os.path.expanduser("~")
VOICE = os.path.join(HOME, ".jarvis", "voice")
MODELS = os.path.join(VOICE, "models")
SAMPLES = os.path.join(VOICE, "samples")
os.makedirs(SAMPLES, exist_ok=True)

LINES = {
    "greeting": "Good morning, Boss. Two sessions are waiting for you, and the guard is armed.",
    "approval": "Boss, the all docs session wants to run git push. Allow, or deny?",
    "done": "The Laxcon quote is done. EDIDTH passed it, and it's ready to print.",
}
VOICES = ["bm_george", "bm_lewis", "bm_daniel", "bf_emma"]


def tts():
    from kokoro_onnx import Kokoro
    import soundfile as sf
    t0 = time.time()
    k = Kokoro(os.path.join(MODELS, "kokoro-v1.0.onnx"), os.path.join(MODELS, "voices-v1.0.bin"))
    print("TTS model load: %.1fs" % (time.time() - t0))
    out = []
    for v in VOICES:
        for name, text in LINES.items():
            t0 = time.time()
            try:
                audio, sr = k.create(text, voice=v, speed=1.0, lang="en-gb")
            except Exception as e:
                print("  %-10s %-9s FAILED %s" % (v, name, e))
                continue
            dt = time.time() - t0
            path = os.path.join(SAMPLES, "%s_%s.wav" % (v, name))
            sf.write(path, audio, sr)
            dur = len(audio) / sr
            print("  %-10s %-9s %4.1fs audio in %4.2fs  (%.1fx realtime)" % (v, name, dur, dt, dur / dt))
            out.append(path)
    return out


def stt(paths):
    from faster_whisper import WhisperModel
    import ctranslate2
    cuda = ctranslate2.get_cuda_device_count() > 0
    print("CUDA devices visible to CTranslate2:", ctranslate2.get_cuda_device_count())
    configs = [("small.en", "cpu", "int8")]
    if cuda:
        configs.append(("medium.en", "cuda", "float16"))
    for size, dev, ctype in configs:
        t0 = time.time()
        try:
            m = WhisperModel(size, device=dev, compute_type=ctype)
        except Exception as e:
            print("  %s on %s: load failed - %s" % (size, dev, str(e)[:120]))
            continue
        print("STT %s on %s/%s loaded in %.1fs" % (size, dev, ctype, time.time() - t0))
        for p in paths[:3]:
            t0 = time.time()
            segs, info = m.transcribe(p, beam_size=1, vad_filter=True, language="en")
            text = " ".join(s.text.strip() for s in segs)
            print("  %-28s %4.2fs -> %s" % (os.path.basename(p), time.time() - t0, text[:80]))


if __name__ == "__main__":
    paths = tts()
    if paths:
        stt(paths)
    print("samples in", SAMPLES)
