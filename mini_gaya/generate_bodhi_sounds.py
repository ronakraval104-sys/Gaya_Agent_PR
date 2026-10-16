"""
Bodhi Vanguard Acoustic Sound Synthesizer
Generates resonant, crystalline, meditative sound effects matching Gaya's persona:
- Tibetan singing bowls
- Temple tingsha chimes
- Solfeggio sacred harmonic resonances (432Hz, 528Hz, 639Hz)
Replaces legacy sci-fi beeps with organic, peaceful harmonic cues.
"""

import os
import math
import wave
import struct
import numpy as np

SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
os.makedirs(SOUNDS_DIR, exist_ok=True)
SAMPLE_RATE = 44100

def write_wav(filename, samples, sample_rate=SAMPLE_RATE):
    # Normalize to -1.0 to 1.0, clamp to -0.98 to avoid digital clipping
    max_val = np.max(np.abs(samples))
    if max_val > 0:
        samples = (samples / max_val) * 0.95
    else:
        samples = np.zeros_like(samples)
    
    # Convert to 16-bit PCM
    int_samples = (samples * 32767).astype(np.int16)
    
    filepath = os.path.join(SOUNDS_DIR, filename)
    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(1)        # mono
        wf.setsampwidth(2)        # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(int_samples.tobytes())
    print(f"Generated: {filepath} ({len(int_samples)} samples, {len(int_samples)/sample_rate:.2f}s)")

def synthesize_bell(freqs, weights, decays, dur, sample_rate=SAMPLE_RATE, attack_s=0.015, shimmer_hz=1.5):
    t = np.linspace(0, dur, int(sample_rate * dur), endpoint=False)
    sig = np.zeros_like(t)
    
    # Attack envelope
    attack_samples = int(sample_rate * attack_s)
    env_attack = np.ones_like(t)
    if attack_samples > 0:
        env_attack[:attack_samples] = np.sin(np.linspace(0, np.pi / 2, attack_samples)) ** 2
    
    for f, w, d in zip(freqs, weights, decays):
        # Add slight natural detuning for acoustic warmth (beating shimmer)
        shimmer = 1.0 + 0.003 * np.sin(2 * np.pi * shimmer_hz * t)
        decay_env = np.exp(-t * d)
        component = w * np.sin(2 * np.pi * f * shimmer * t) * decay_env
        sig += component
        
    return sig * env_attack

def generate_all_cues():
    print("Synthesizing Bodhi Vanguard Sound Effects...")

    # 1. wake.wav: Bodhi Singing Bowl (432Hz fundamental + rich overtones)
    wake_sig = synthesize_bell(
        freqs=[432.0, 864.0, 1296.0, 1728.0],
        weights=[0.60, 0.25, 0.10, 0.05],
        decays=[2.4, 3.8, 5.0, 7.0],
        dur=1.4,
        attack_s=0.035,
        shimmer_hz=1.2
    )
    write_wav("wake.wav", wake_sig)

    # 2. notify.wav: Bodhi Bell Shimmer (528Hz Solfeggio Love/Transformation + high tingsha overtone)
    notify_sig = synthesize_bell(
        freqs=[528.0, 1056.0, 1584.0, 2112.0],
        weights=[0.55, 0.30, 0.10, 0.05],
        decays=[3.8, 5.2, 7.5, 9.0],
        dur=0.75,
        attack_s=0.008,
        shimmer_hz=2.0
    )
    write_wav("notify.wav", notify_sig)

    # 3. done.wav: Bodhi Ascendant Triad (528Hz -> 660Hz -> 792Hz ascending harmonic resolution)
    dur_done = 1.25
    t = np.linspace(0, dur_done, int(SAMPLE_RATE * dur_done), endpoint=False)
    done_sig = np.zeros_like(t)
    notes = [(528.0, 0.0, 0.35), (660.0, 0.08, 0.35), (792.0, 0.16, 0.45), (1056.0, 0.22, 0.25)]
    for f, start_t, amp in notes:
        idx = int(start_t * SAMPLE_RATE)
        sub_t = t[idx:] - start_t
        env = np.exp(-sub_t * 3.5)
        att = min(int(0.012 * SAMPLE_RATE), len(sub_t))
        if att > 0:
            env[:att] *= np.linspace(0, 1, att)
        done_sig[idx:] += amp * np.sin(2 * np.pi * f * sub_t) * env
    write_wav("done.wav", done_sig)

    # 4. error.wav: Bodhi Grounding Tone (Deep Tibetan Bronze Bowl 144Hz + 216Hz, warm & meditative)
    error_sig = synthesize_bell(
        freqs=[144.0, 216.0, 288.0, 432.0],
        weights=[0.60, 0.25, 0.10, 0.05],
        decays=[3.2, 4.5, 6.0, 8.0],
        dur=0.9,
        attack_s=0.04,
        shimmer_hz=0.8
    )
    write_wav("error.wav", error_sig)

    # 5. open.wav: Lotus Unfolding (Ascending frequency sweep 432Hz -> 720Hz with soft crystal bloom)
    dur_open = 0.42
    t_open = np.linspace(0, dur_open, int(SAMPLE_RATE * dur_open), endpoint=False)
    freq_sweep = 432.0 + (720.0 - 432.0) * (t_open / dur_open) ** 1.3
    phase = 2 * np.pi * np.cumsum(freq_sweep) / SAMPLE_RATE
    env_open = (np.sin(np.pi * (t_open / dur_open)) ** 0.8) * np.exp(-t_open * 2.2)
    open_sig = (0.7 * np.sin(phase) + 0.3 * np.sin(phase * 2)) * env_open
    write_wav("open.wav", open_sig)

    # 6. close.wav: Lotus Settling (Soft descending crystal droplet 720Hz -> 432Hz)
    dur_close = 0.38
    t_close = np.linspace(0, dur_close, int(SAMPLE_RATE * dur_close), endpoint=False)
    freq_sweep_c = 720.0 - (720.0 - 432.0) * (t_close / dur_close) ** 0.9
    phase_c = 2 * np.pi * np.cumsum(freq_sweep_c) / SAMPLE_RATE
    env_close = (np.sin(np.pi * (t_close / dur_close)) ** 0.9) * np.exp(-t_close * 3.5)
    close_sig = (0.75 * np.sin(phase_c) + 0.25 * np.sin(phase_c * 2)) * env_close
    write_wav("close.wav", close_sig)

    # 7. send.wav: Vanguard Crystal Transmission (528Hz focused pulse with delicate chime tail)
    send_sig = synthesize_bell(
        freqs=[528.0, 1056.0, 2112.0],
        weights=[0.60, 0.30, 0.10],
        decays=[6.5, 8.5, 12.0],
        dur=0.35,
        attack_s=0.005,
        shimmer_hz=3.0
    )
    write_wav("send.wav", send_sig)

    # 8. scan.wav: Resonant Bodhi Sweep (Shimmering sacred overtone oscillation)
    dur_scan = 1.05
    t_scan = np.linspace(0, dur_scan, int(SAMPLE_RATE * dur_scan), endpoint=False)
    mod = 528.0 + 110.0 * np.sin(2 * np.pi * 2.5 * t_scan)
    phase_scan = 2 * np.pi * np.cumsum(mod) / SAMPLE_RATE
    env_scan = np.sin(np.pi * (t_scan / dur_scan)) ** 0.6
    scan_sig = (0.6 * np.sin(phase_scan) + 0.25 * np.sin(phase_scan * 1.5) + 0.15 * np.sin(phase_scan * 2)) * env_scan
    write_wav("scan.wav", scan_sig)

    # 9. dizzy.wav: Playful Singing Bowl Flutter
    dur_dizzy = 0.65
    t_dizzy = np.linspace(0, dur_dizzy, int(SAMPLE_RATE * dur_dizzy), endpoint=False)
    flutter = 440.0 + 35.0 * np.sin(2 * np.pi * 7.0 * t_dizzy)
    phase_dizzy = 2 * np.pi * np.cumsum(flutter) / SAMPLE_RATE
    env_dizzy = np.exp(-t_dizzy * 3.2) * (1.0 + 0.3 * np.sin(2 * np.pi * 14.0 * t_dizzy))
    dizzy_sig = 0.8 * np.sin(phase_dizzy) * env_dizzy
    write_wav("dizzy.wav", dizzy_sig)

    # 10. request.wav: Bodhi Temple Attention Call (Two warm singing bowl strikes: 432Hz -> 648Hz)
    dur_req = 1.1
    t_req = np.linspace(0, dur_req, int(SAMPLE_RATE * dur_req), endpoint=False)
    req_sig = np.zeros_like(t_req)
    # Strike 1: 432Hz
    env1 = np.exp(-t_req * 3.2)
    att1 = int(0.02 * SAMPLE_RATE)
    env1[:att1] *= np.linspace(0, 1, att1)
    req_sig += 0.5 * (np.sin(2 * np.pi * 432.0 * t_req) + 0.3 * np.sin(2 * np.pi * 864.0 * t_req)) * env1
    # Strike 2: 648Hz at t = 0.24s
    t2_idx = int(0.24 * SAMPLE_RATE)
    sub_t2 = t_req[t2_idx:] - 0.24
    env2 = np.exp(-sub_t2 * 3.8)
    att2 = min(int(0.015 * SAMPLE_RATE), len(sub_t2))
    env2[:att2] *= np.linspace(0, 1, att2)
    req_sig[t2_idx:] += 0.55 * (np.sin(2 * np.pi * 648.0 * sub_t2) + 0.25 * np.sin(2 * np.pi * 1296.0 * sub_t2)) * env2
    write_wav("request.wav", req_sig)

    print("All 10 Bodhi Vanguard audio files generated successfully!")

if __name__ == "__main__":
    generate_all_cues()
