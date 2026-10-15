"""J's ears: push-to-talk (hold Right Ctrl) -> faster-whisper small.en (GPU if it can, else CPU).

    Listener(on_text, on_state).start()
    on_state: "listening" / "thinking" / "stt-ready" / "stt-error: ..."
    on_text(text): the transcript (already trimmed), only for real speech >= 0.4 s
"""
import ctypes
import glob
import os
import site
import threading
import time

import numpy as np

VK_RCONTROL = 0xA3
SR = 16000
HINTS = ("Hey Gaya. Hello, Gaya. Good morning, Gaya. Thanks, Gaya. Mini Gaya, Gaya. "
         "LOGOS, Bob, Freya, Tvashtar, Ros, Ross, Ron, Council of Gaya, Bodhi Vanguard, "
         "deck, session, allow, deny, terminal, status report.")


def _nvidia_dlls():
    for sp in site.getsitepackages() + [site.getusersitepackages()]:
        for d in glob.glob(os.path.join(sp, "nvidia", "*", "bin")):
            try:
                os.add_dll_directory(d)
                os.environ["PATH"] = d + os.pathsep + os.environ["PATH"]
            except OSError:
                pass


def key_down(vk=VK_RCONTROL):
    return ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000 != 0


class Listener:
    def __init__(self, on_text, on_state=None, vk=VK_RCONTROL):
        self.on_text = on_text
        self.on_state = on_state or (lambda s: None)
        self.vk = vk
        self.model = None
        self.device = "?"
        self.enabled = True
        self._frames = []
        self._stream = None

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    # ---------------------------------------------------------------- model
    def _load(self):
        _nvidia_dlls()
        from faster_whisper import WhisperModel
        # 15 Oct bench (GTX 1070, int8, 4 synthetic lines): small.en 0.2 s but mangles names ("Jols", "toast");
        # medium.en 0.55 s; large-v3-turbo 0.63 s and the only one to spell Laxcon + EDIDTH right.
        for name, dev, ctype in (("large-v3-turbo", "cuda", "int8"), ("small.en", "cuda", "int8"),
                                 ("small.en", "cpu", "int8")):
            try:
                self.model = WhisperModel(name, device=dev, compute_type=ctype)
                self.device = "%s %s" % (dev, name)
                # warm-up so the first real command isn't slow - with the VAD, which loads lazily too
                # (15 Oct: first real utterance took 1.46 s vs 0.22 s after; the VAD model was cold)
                segs, _ = self.model.transcribe(np.zeros(SR, dtype=np.float32), beam_size=1, language="en",
                                                vad_filter=True, initial_prompt=HINTS)
                list(segs)
                self.on_state("stt-ready:%s" % self.device)
                return
            except Exception as e:
                self.on_state("stt-error:%s %s" % (dev, str(e)[:80]))
        self.model = None

    def transcribe(self, audio):
        import re
        segs, _ = self.model.transcribe(audio, beam_size=1, language="en", vad_filter=True,
                                        initial_prompt=HINTS, condition_on_previous_text=False)
        raw = " ".join(s.text.strip() for s in segs).strip()
        raw = re.sub(r'\br\s*[-_]?\s*0\s*[-_]?\s*n\b', 'Ros', raw, flags=re.I)
        raw = re.sub(r'\br\s+zero\s+n\b', 'Ros', raw, flags=re.I)
        raw = re.sub(r'\br0n\b', 'Ros', raw, flags=re.I)
        raw = re.sub(r'\b(clowd|cloud|claude)\s+sessions?\b', 'antigravity sessions', raw, flags=re.I)
        return raw

    # ---------------------------------------------------------------- push-to-talk loop
    def _run(self):
        self._load()
        if self.model is None:
            return
        import sounddevice as sd
        held = False
        while True:
            time.sleep(0.03)
            if not self.enabled:
                continue
            down = key_down(self.vk)
            if down and not held:
                held = True
                self._frames = []
                try:
                    self._stream = sd.InputStream(samplerate=SR, channels=1, dtype="float32",
                                                  callback=lambda d, f, t, s: self._frames.append(d.copy()))
                    self._stream.start()
                    self.on_state("listening")
                except Exception as e:
                    self.on_state("stt-error:mic %s" % str(e)[:80])
                    held = False
            elif not down and held:
                held = False
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception:
                    pass
                audio = np.concatenate(self._frames)[:, 0] if self._frames else np.zeros(0, dtype=np.float32)
                if len(audio) < SR * 0.4:
                    self.on_state("idle")
                    continue
                self.on_state("thinking")
                t0 = time.time()
                try:
                    text = self.transcribe(audio)
                except Exception as e:
                    self.on_state("stt-error:%s" % str(e)[:80])
                    continue
                self.on_state("idle")
                self.on_text(text, time.time() - t0, len(audio) / SR)
