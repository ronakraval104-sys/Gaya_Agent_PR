"""Gaya's voice: Native Windows OneCore synthesizer with Microsoft Heera (English - India)
as the divine Bodhi Vanguard voice, with full library switching (Susan, Hazel, Zira).

    say("At your command, R0n.")            queue it
    say("R0n, ...", interrupt=True)         drop the queue and say this immediately
    stop()                                  silence
All local and instant. Settings stored in ~/.jarvis/voice/voice_config.json.
"""
import glob
import json
import os
import queue
import re
import site
import threading
import time

HOME = os.path.expanduser("~")
VOICE_DIR = os.path.join(HOME, ".gaya", "voice")
CONFIG_PATH = os.path.join(VOICE_DIR, "voice_config.json")
DEFAULT_VOICE = "Microsoft Heera - English (India)"

def get_user_profile():
    prof_path = os.path.join(HOME, ".gaya", "user_profile.json")
    if os.path.exists(prof_path):
        try:
            return json.load(open(prof_path, "r", encoding="utf-8"))
        except Exception:
            pass
    return {"name": "Ronak", "prefix": "R0n"}

WARM = [
    "Voice is online, Ros. Hold right control and talk.",
    "Allow, or deny?",
    "Done.",
    "Sent.",
    "On it.",
    "I didn't catch that, Ros.",
    "Opening the deck.",
    "Muted.",
    "Voice off.",
    "Preparing for work, Ros.",
    "Allowed.",
    "Denied.",
    "Handed back to Antigravity."
]


def _get_config():
    try:
        if os.path.exists(CONFIG_PATH):
            return json.load(open(CONFIG_PATH, "r", encoding="utf-8"))
    except Exception:
        pass
    return {"voice_name": DEFAULT_VOICE, "rate": 0, "volume": 100}


def _save_config(cfg):
    try:
        os.makedirs(VOICE_DIR, exist_ok=True)
        json.dump(cfg, open(CONFIG_PATH, "w", encoding="utf-8"), indent=2)
    except Exception:
        pass


def get_available_voices():
    """Returns list of all available OneCore and Desktop SAPI voices."""
    out = []
    try:
        import win32com.client
        cat = win32com.client.Dispatch("SAPI.SpObjectTokenCategory")
        cat.SetId(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices")
        for t in cat.EnumerateTokens():
            desc = t.GetDescription()
            out.append({"id": t.Id, "name": desc, "type": "OneCore"})
    except Exception:
        pass

    try:
        import win32com.client
        sp = win32com.client.Dispatch("SAPI.SpVoice")
        for v in sp.GetVoices():
            desc = v.GetDescription()
            if not any(o["name"] == desc for o in out):
                out.append({"id": v.Id, "name": desc, "type": "Desktop"})
    except Exception:
        pass

    return out


def clean_for_speech(text):
    if not text:
        return ""
    prof = get_user_profile()
    prefix = prof.get("prefix", "R0n")
    pronounce = "Ros" if prefix.lower() in ("r0n", "ron") else prefix
    # "R0n" is typed with a zero, but phonetically pronounced "Ros"
    text = re.sub(r'\br\s*[-_]?\s*0\s*[-_]?\s*n\b', pronounce, text, flags=re.I)
    text = re.sub(r'\br\s+zero\s+n\b', pronounce, text, flags=re.I)
    text = re.sub(r'\br0n\b', pronounce, text, flags=re.I)
    text = re.sub(r'\bR0n\b', pronounce, text)
    # Fix any legacy "cloud sessions" / "clowd sessions" / "claude sessions"
    text = re.sub(r'\b(clowd|cloud|claude)\s+sessions?\b', 'Antigravity sessions', text, flags=re.I)
    text = re.sub(r'\b(clowd|cloud|claude)\s+code\b', 'Antigravity', text, flags=re.I)
    text = re.sub(r'\bclaude\b', 'Antigravity', text, flags=re.I)
    return text


def sentences(text):
    text = clean_for_speech(text)
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [p.strip() for p in parts if p.strip()]


class Speaker:
    def __init__(self, on_state=None):
        self.q = queue.Queue()
        self.on_state = on_state or (lambda s: None)
        self.muted = False
        self.ready = False
        self.is_speaking = False
        self.gen = 0
        self._sp = None
        self._tokens = {}
        self.current_voice_name = DEFAULT_VOICE
        threading.Thread(target=self._worker, daemon=True).start()

    def say(self, text, interrupt=False):
        if not text or self.muted:
            return
        text = clean_for_speech(text)
        if interrupt:
            self.stop()
        g = self.gen
        for s in sentences(text):
            self.q.put((g, s))

    def stop(self):
        self.gen += 1
        try:
            while True:
                self.q.get_nowait()
        except queue.Empty:
            pass
        if self._sp:
            try:
                # SVSFPurgeBeforeSpeak = 2
                self._sp.Speak("", 2)
            except Exception:
                pass

    def set_voice(self, name_part):
        for name, tok in self._tokens.items():
            if name_part.lower() in name.lower():
                try:
                    self._sp.Voice = tok
                    self.current_voice_name = name
                    _save_config({"voice_name": name, "rate": self._sp.Rate, "volume": self._sp.Volume})
                    return True
                except Exception:
                    pass
        return False

    def _load(self):
        import pythoncom
        pythoncom.CoInitialize()
        import win32com.client

        sp = win32com.client.Dispatch("SAPI.SpVoice")
        self._tokens = {}

        # 1. Load OneCore voices (Heera, Susan, Hazel, Zira, etc.)
        try:
            cat = win32com.client.Dispatch("SAPI.SpObjectTokenCategory")
            cat.SetId(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices")
            for t in cat.EnumerateTokens():
                self._tokens[t.GetDescription()] = t
        except Exception:
            pass

        # 2. Add Desktop voices as fallback
        try:
            for v in sp.GetVoices():
                desc = v.GetDescription()
                if desc not in self._tokens:
                    self._tokens[desc] = v
        except Exception:
            pass

        # Set voice based on user configuration
        cfg = _get_config()
        wanted = cfg.get("voice_name", DEFAULT_VOICE)

        matched = False
        for name, tok in self._tokens.items():
            if wanted.lower() in name.lower():
                sp.Voice = tok
                self.current_voice_name = name
                matched = True
                break

        # Fallback to Heera if not matched
        if not matched:
            for name, tok in self._tokens.items():
                if "heera" in name.lower() or "zira" in name.lower() or "hazel" in name.lower():
                    sp.Voice = tok
                    self.current_voice_name = name
                    break

        sp.Rate = int(cfg.get("rate", 0))
        sp.Volume = int(cfg.get("volume", 100))
        self._sp = sp
        self.ready = True
        self.on_state("tts-ready:%s" % self.current_voice_name)

    def _worker(self):
        try:
            self._load()
        except Exception as e:
            self.on_state("tts-error: %s" % e)
            return

        while True:
            g, text = self.q.get()
            if g != self.gen:
                continue
            try:
                self.is_speaking = True
                self.on_state("speaking")
                # 0 = Synchronous speak inside worker thread
                clean_text = clean_for_speech(text)
                self._sp.Speak(clean_text, 0)
            except Exception as e:
                self.on_state("tts-error: %s" % e)
            finally:
                self.is_speaking = False
                if self.q.empty():
                    self.on_state("idle")


if __name__ == "__main__":
    import sys
    s = Speaker(print)
    while not s.ready:
        time.sleep(0.2)
    msg = " ".join(sys.argv[1:]) or "Greetings, Ros. The sacred Bodhi voice of Gaya is awakened."
    s.say(msg)
    time.sleep(1)
    while not s.q.empty():
        time.sleep(0.2)
    time.sleep(3)
