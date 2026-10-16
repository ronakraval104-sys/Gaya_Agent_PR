"""Make J say something, from any session or script:  python say.py "Good morning, Boss." [--now]
Simulate something Boss said (no mic needed):       python say.py --hear "Jarvis, prepare for work"

Goes through the sprite hook (same HMAC handshake as every other event), so only a local
process holding ~/.jarvis/sprite.key can put words in J's mouth. --now interrupts whatever
J is saying. Prints nothing; exit 0 even when J is not running (it just stays quiet).
(Use this rather than piping JSON from PowerShell 5.1 - that path never reaches the hook.)
"""
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gaya_sprite_hook.py")


def _send(payload):
    env = {k: v for k, v in os.environ.items() if k != "ELECTRON_RUN_AS_NODE"}
    subprocess.run([sys.executable, HOOK], input=json.dumps(payload).encode(), env=env, timeout=5)


def say(text, interrupt=False, session_id=""):
    _send({"hook_event_name": "Say", "text": str(text)[:400], "interrupt": bool(interrupt),
           "session_id": session_id or os.environ.get("CLAUDE_SESSION_ID", "")})


def hear(text):
    """Feed J a line as if Whisper had heard it - same router, same actions, same spoken reply."""
    _send({"hook_event_name": "VoiceText", "text": str(text)[:400]})


if __name__ == "__main__":
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    words = " ".join(a for a in sys.argv[1:] if not a.startswith("--"))
    if words and "--hear" in flags:
        hear(words)
    elif words:
        say(words, interrupt="--now" in flags)
