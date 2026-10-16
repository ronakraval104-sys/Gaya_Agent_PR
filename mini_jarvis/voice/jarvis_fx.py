"""The JARVIS treatment - make a clean TTS voice sound like a refined AI, not a narrator.

    python jarvis_fx.py in.wav out.wav [light|mid|heavy]

light : presence EQ + a whisper of room  (barely there - "a very good speaker system")
mid   : + subtle doubling (8 ms) and a slightly lower, steadier pitch (the sci-fi AI sheen)
heavy : + gentle tremolo / ring-mod and tighter band  (clearly synthetic)
numpy only.
"""
import sys

import numpy as np
import soundfile as sf


def eq(x, sr, hp=110.0, lp=9000.0, presence_db=3.0):
    """FFT band shaping: high-pass, low-pass, +presence at 2-5 kHz."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / sr)
    g = np.ones_like(f)
    g[f < hp] *= (f[f < hp] / hp) ** 2
    g[f > lp] *= np.exp(-(f[f > lp] - lp) / 1500.0)
    band = (f > 1800) & (f < 5200)
    g[band] *= 10 ** (presence_db / 20)
    return np.fft.irfft(X * g, n)


def delay_mix(x, sr, ms, mix, detune=0.0):
    d = int(sr * ms / 1000)
    y = np.zeros_like(x)
    src = x
    if detune:
        idx = np.arange(len(x)) * (1 + detune)
        src = np.interp(idx, np.arange(len(x)), x, right=0.0)
    y[d:] = src[: len(x) - d]
    return x + mix * y


def room(x, sr, ms=140, mix=0.12, seed=7):
    rng = np.random.default_rng(seed)
    n = int(sr * ms / 1000)
    ir = rng.normal(0, 1, n) * np.exp(-np.linspace(0, 6, n))
    ir[0] = 0
    wet = np.convolve(x, ir / np.abs(ir).sum() * 3)[: len(x)]
    return x + mix * wet


def pitch(x, sr, semitones):
    """Resample-based pitch shift (also changes length slightly - fine for speech)."""
    r = 2 ** (semitones / 12)
    idx = np.arange(0, len(x), r)
    return np.interp(idx, np.arange(len(x)), x)


def tremolo(x, sr, hz=28.0, depth=0.10):
    t = np.arange(len(x)) / sr
    return x * (1 - depth + depth * np.sin(2 * np.pi * hz * t))


def compress(x, drive=1.25):
    return np.tanh(x * drive) / np.tanh(drive)


def jarvis(x, sr, strength="mid"):
    x = x.astype(np.float64)
    x = x / (np.abs(x).max() + 1e-9) * 0.8
    if strength in ("mid", "heavy"):
        x = pitch(x, sr, -0.6 if strength == "mid" else -1.2)
    x = eq(x, sr, presence_db=3.0 if strength == "light" else 4.0,
           lp=9000 if strength != "heavy" else 7000)
    if strength in ("mid", "heavy"):
        x = delay_mix(x, sr, 8.0, 0.30, detune=0.004)      # doubling = synthetic sheen
    if strength == "heavy":
        x = tremolo(x, sr, 28.0, 0.12)
        x = delay_mix(x, sr, 1.1, 0.5)                      # tiny comb = vocoder hint
    x = room(x, sr, 140, 0.10 if strength == "light" else 0.14)
    x = compress(x)
    return (x / (np.abs(x).max() + 1e-9) * 0.9).astype(np.float32)


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    strength = sys.argv[3] if len(sys.argv) > 3 else "mid"
    x, sr = sf.read(src)
    if x.ndim > 1:
        x = x.mean(axis=1)
    sf.write(dst, jarvis(x, sr, strength), sr)
    print(dst)
