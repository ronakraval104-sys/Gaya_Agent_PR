"""GAYA's ears: Wake-Word Detection ("Hey Gaya") + Push-to-Talk (Right Ctrl) -> faster-whisper small.en (GPU if available, else CPU).

    Listener(on_text, on_state, on_wake, vk, speaker, wake_word_enabled).start()
    on_state: "listening" / "thinking" / "stt-ready" / "stt-error: ..."
    on_wake(): fired immediately when "Hey Gaya" is detected
    on_text(text, dt, audio_s): transcript emitted for intent routing
"""
import ctypes
import glob
import logging
import os
import re
import site
import threading
import time

import numpy as np

VK_RCONTROL = 0xA3
SR = 16000
BLOCK_SIZE = 1600  # 100 ms blocks at 16 kHz
HINTS = ("Hey Gaya. Hello, Gaya. Good morning, Gaya. Thanks, Gaya. Mini Gaya, Gaya. "
         "LOGOS, Bob, Freya, Tvashtar, Ros, Ross, Ron, Council of Gaya, Bodhi Vanguard, "
         "deck, session, allow, deny, terminal, status report.")

# Wake word regex matching variants
WAKE_PATTERN = re.compile(
    r'\b(?:hey|hay|ok|okay|hi|hello|yo)?\s*(?:gaya|gaia|guy-a|gya|guya|mini gaya|mini-gaya)\b',
    re.IGNORECASE
)


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
    def __init__(self, on_text, on_state=None, on_wake=None, vk=VK_RCONTROL, speaker=None, wake_word_enabled=True):
        self.on_text = on_text
        self.on_state = on_state or (lambda s: None)
        self.on_wake = on_wake or (lambda: None)
        self.vk = vk
        self.speaker = speaker
        self.model = None
        self.device = "?"
        self.enabled = True
        self.wake_word_enabled = wake_word_enabled
        self.active_window_until = 0.0
        self._frames = []
        self._stream = None

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def set_wake_enabled(self, enabled):
        self.wake_word_enabled = bool(enabled)
        if not self.wake_word_enabled:
            self.active_window_until = 0.0
            self.on_state("idle")

    # ---------------------------------------------------------------- model
    def _load(self):
        _nvidia_dlls()
        from faster_whisper import WhisperModel
        for name, dev, ctype in (("large-v3-turbo", "cuda", "int8"), ("small.en", "cuda", "int8"),
                                 ("small.en", "cpu", "int8")):
            try:
                self.model = WhisperModel(name, device=dev, compute_type=ctype)
                self.device = "%s %s" % (dev, name)
                # Warm-up pass so the first real command is fast
                segs, _ = self.model.transcribe(np.zeros(SR, dtype=np.float32), beam_size=1, language="en",
                                                vad_filter=True, initial_prompt=HINTS)
                list(segs)
                self.on_state("stt-ready:%s" % self.device)
                return
            except Exception as e:
                self.on_state("stt-error:%s %s" % (dev, str(e)[:80]))
        self.model = None

    def transcribe(self, audio):
        segs, _ = self.model.transcribe(audio, beam_size=1, language="en", vad_filter=True,
                                        initial_prompt=HINTS, condition_on_previous_text=False)
        raw = " ".join(s.text.strip() for s in segs).strip()
        raw = re.sub(r'\br\s*[-_]?\s*0\s*[-_]?\s*n\b', 'Ros', raw, flags=re.I)
        raw = re.sub(r'\br\s+zero\s+n\b', 'Ros', raw, flags=re.I)
        raw = re.sub(r'\br0n\b', 'Ros', raw, flags=re.I)
        raw = re.sub(r'\b(clowd|cloud|claude)\s+sessions?\b', 'antigravity sessions', raw, flags=re.I)
        return raw

    # ---------------------------------------------------------------- continuous audio stream
    def _run(self):
        self._load()
        if self.model is None:
            return
        import sounddevice as sd

        held = False
        ptt_frames = []

        speech_frames = []
        silence_blocks = 0
        in_speech = False
        noise_floor = 0.005

        def audio_callback(indata, frames, time_info, status):
            nonlocal held, ptt_frames, speech_frames, silence_blocks, in_speech, noise_floor

            if not self.enabled:
                return

            chunk = indata[:, 0].copy()
            down = key_down(self.vk)

            # 1. Physical Push-To-Talk Override (Holding Right Ctrl)
            if down:
                if not held:
                    held = True
                    ptt_frames = []
                    self.on_state("listening")
                ptt_frames.append(chunk)
                return

            if held and not down:
                held = False
                if ptt_frames:
                    audio = np.concatenate(ptt_frames)
                    ptt_frames = []
                    if len(audio) >= SR * 0.35:
                        self._process_utterance(audio, is_wake_mode=False)
                    else:
                        self.on_state("idle")
                return

            # 2. Continuous Wake-Word Detection
            if not self.wake_word_enabled:
                return

            # Skip microphone input if TTS speaker is currently speaking (avoid self-trigger loop)
            if self.speaker and getattr(self.speaker, "is_speaking", False):
                speech_frames = []
                in_speech = False
                silence_blocks = 0
                return

            rms = float(np.sqrt(np.mean(chunk**2)))
            if not in_speech:
                noise_floor = 0.95 * noise_floor + 0.05 * rms

            speech_threshold = max(0.024, noise_floor * 2.4)

            if rms >= speech_threshold:
                if not in_speech:
                    in_speech = True
                    silence_blocks = 0
                    if time.time() < self.active_window_until:
                        self.on_state("listening")
                speech_frames.append(chunk)
                silence_blocks = 0
            elif in_speech:
                speech_frames.append(chunk)
                silence_blocks += 1
                # 0.65s of silence marks end of utterance (or max 8 seconds safety cap)
                if silence_blocks >= 7 or len(speech_frames) >= 80:
                    in_speech = False
                    audio = np.concatenate(speech_frames)
                    speech_frames = []
                    silence_blocks = 0
                    if len(audio) >= SR * 0.4:
                        self._process_utterance(audio, is_wake_mode=True)
                    else:
                        self.on_state("idle")

        try:
            with sd.InputStream(samplerate=SR, channels=1, dtype="float32", blocksize=BLOCK_SIZE, callback=audio_callback):
                while True:
                    time.sleep(0.1)
        except Exception as e:
            self.on_state("stt-error:stream %s" % str(e)[:80])

    def _process_utterance(self, audio, is_wake_mode=True):
        self.on_state("thinking")
        t0 = time.time()
        try:
            raw = self.transcribe(audio)
        except Exception as e:
            self.on_state("stt-error:transcribe %s" % str(e)[:80])
            self.on_state("idle")
            return

        dt_ = time.time() - t0
        audio_s = len(audio) / SR

        if not raw or len(raw.strip()) == 0:
            self.on_state("idle")
            return

        if not is_wake_mode:
            self.on_state("idle")
            self.on_text(raw, dt_, audio_s)
            return

        now = time.time()
        is_wake = bool(WAKE_PATTERN.search(raw))
        in_active_window = now < self.active_window_until

        if is_wake:
            logging.info("wake word detected: %r", raw)
            self.on_wake()

            stripped = WAKE_PATTERN.sub("", raw).strip(" ,.!?")
            if not stripped:
                # User only said "Hey Gaya"
                self.active_window_until = now + 6.0
                self.on_state("idle")
                self.on_text("hey gaya", dt_, audio_s)
            else:
                # User said "Hey Gaya, <command>" in one sentence
                self.active_window_until = 0.0
                self.on_state("idle")
                self.on_text(raw, dt_, audio_s)
        elif in_active_window:
            logging.info("active-window command: %r", raw)
            self.active_window_until = 0.0
            self.on_state("idle")
            self.on_text(raw, dt_, audio_s)
        else:
            self.on_state("idle")
