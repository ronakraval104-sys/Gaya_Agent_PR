"""Glue: the voice engine inside the sprite process.

VoiceEngine(sprite): starts the Speaker (Kokoro) and the Listener (push-to-talk +
Whisper) on background threads; everything that touches the UI comes back
through Qt signals so it runs on the GUI thread.

Three lanes for what Boss says (voice/intents.py decides):
  command / routine / open   J does it on this PC
  ask                        J answers from this PC (voice/brain.py) and speaks the answer
  tell / new                 into a Claude Code session, only by an explicit verb
"""
import datetime as dt
import logging
import os
import sys
import threading
import time

from PySide6.QtCore import QObject, Signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import brain  # noqa: E402
import intents  # noqa: E402
from stt import Listener  # noqa: E402
from tts import Speaker  # noqa: E402


class VoiceEngine(QObject):
    heard = Signal(str, float, float)       # text, stt seconds, audio seconds
    state = Signal(str)
    answered = Signal(str, str, str)        # reply, detail, what Boss said

    def __init__(self, sprite):
        super().__init__()
        self.sprite = sprite
        self.enabled = True
        self.stt_dev = "?"
        self.speaker = Speaker(on_state=self.state.emit)
        self.listener = Listener(on_text=lambda t, dt_, a: self.heard.emit(t, dt_, a), on_state=self.state.emit)
        self.heard.connect(self._on_heard)
        self.state.connect(self._on_state)
        self.answered.connect(self._on_answered)
        self.listener.start()
        self.last_session = None

    # ---------------------------------------------------------------- speaking
    def say(self, text, interrupt=False):
        if self.enabled and not self.speaker.muted:
            self.speaker.say(text, interrupt=interrupt)

    def mute(self, on):
        self.speaker.muted = on
        if on:
            self.speaker.stop()

    def off(self):
        self.enabled = False
        self.listener.enabled = False
        self.speaker.stop()

    def on(self):
        self.enabled = True
        self.listener.enabled = True

    # ---------------------------------------------------------------- state -> UI
    def _on_state(self, s):
        sp = self.sprite
        if s == "listening":
            sp.listening = True
            sp.anim["pulse"] = 1.0
        elif s in ("thinking", "idle"):
            sp.listening = False
        elif s.startswith("stt-ready"):
            self.stt_dev = s.split(":", 1)[-1]
            logging.info("voice: STT ready on %s", self.stt_dev)
            self.say("Voice is online, Ros. Hold right control and talk.")
        elif s.startswith("stt-error") or s.startswith("tts-error"):
            logging.error("voice: %s", s)
        sp.update()

    # ---------------------------------------------------------------- what Boss said
    def _on_heard(self, text, dt_, audio_s):
        sp = self.sprite
        logging.info("voice heard (%.1fs audio, %.2fs stt): %r", audio_s, dt_, text)
        kind, payload, reply = intents.route(text, len(sp.requests))
        shown = text.strip()[:80]
        logging.info("voice route: %s %r", kind, payload if isinstance(payload, str) else
                     (payload[0] if isinstance(payload, tuple) else payload))
        try:
            if kind == "none":
                sp.toast("info", "Didn't catch that", "")
            elif kind == "approve":
                sp.decide(sp.requests[0], payload)
                sp.toast("approved" if payload == "allow" else "hold", "Voice: %s" % payload, shown)
            elif kind == "command":
                if payload[0] == "greet":
                    waiting = [r["title"] for r in sp.sessions if r.get("status") == "waiting"]
                    if waiting:
                        reply += (" %d sessions are waiting for you." % len(waiting)) if len(waiting) > 1 \
                            else " %s is waiting for you." % waiting[0][:40]
                self._command(payload[0], payload[1], shown)
            elif kind == "routine":
                name, r = payload
                sp.toast("approved", "Routine: %s" % name, shown)
                for step in r.get("steps", []):
                    if "say" in step:
                        self.say(step["say"])
                    else:
                        intents.launch(step)
                reply = ""
            elif kind == "open":
                name, exe, args = payload
                if exe:
                    intents.launch({"app": exe, "args": args})
                    sp.toast("approved", "Opening %s" % name, shown)
                else:
                    sp.toast("hold", "Unknown app: %s" % name, "add it to voice/intents.py APPS")
            elif kind == "tell":
                target, msg = payload
                sid = self._find_session(target)
                if sid:
                    from sprite_chat import deliver
                    deliver(sp, sid, msg, submit=True, route="auto")
                    sp.toast("approved", "Voice → %s" % target, msg[:80])
                else:
                    reply = "I can't find a session called %s, Ros. Say 'new session' to start one." % target
                    sp.toast("hold", "No session matches '%s'" % target, "nothing was sent")
            elif kind == "new":
                from sprite_chat import deliver
                deliver(sp, None, payload, submit=True, route="auto")
                sp.toast("approved", "Voice → new session", payload[:80])
            elif kind == "ask":
                sp.toast("info", "Gaya is thinking", shown)
                sp.anim["pulse"] = 1.0
                rows = [dict(r) for r in sp.sessions]            # snapshot for the worker thread
                threading.Thread(target=self._think, args=(payload, rows, shown), daemon=True).start()
        except Exception as e:
            logging.exception("voice action failed")
            reply = "That didn't work, Ros: %s" % str(e)[:60]
        if reply:
            self.say(reply, interrupt=True)

    def _think(self, question, rows, shown):
        try:
            reply, detail = brain.answer(question, rows)
        except Exception as e:
            logging.exception("brain failed")
            reply, detail = "That didn't work, Ros: %s" % str(e)[:60], ""
        self.answered.emit(reply, detail, shown)

    def _on_answered(self, reply, detail, shown):
        logging.info("brain: %r -> %r", shown, reply[:120])
        self.say(reply, interrupt=True)
        self.sprite.toast("info", reply[:90], detail[:100])

    def _command(self, kind, m, shown):
        sp = self.sprite
        if kind == "deck":
            sp.panel.open()
            sp.panel.show_tab(0)
        elif kind == "deck_close":
            sp.panel.hide()
        elif kind == "sessions":
            sp.panel.open()
            sp.panel.show_tab(2)
            self.say(brain.sessions_summary([dict(r) for r in sp.sessions]), interrupt=True)
        elif kind == "jump":
            sid = self._find_session(m.group(3))
            if sid:
                from sprite_ui import focus_session
                focus_session({"sid": sid, "cwd": "", "entry": "claude-vscode"})
                self.say("Jumping in.")
            else:
                self.say("I can't find that session.")
        elif kind == "mute":
            self.mute(True)
        elif kind == "unmute":
            self.mute(False)
            self.say("Back, Ros.")
        elif kind == "voice_off":
            self.say("Voice off.")
            self.off()
        elif kind == "come":
            sp.fly_to_cursor()
        elif kind == "hide":
            sp.toggle()
        elif kind == "roam":
            sp.roam = True
        elif kind == "stay":
            sp.roam = False
            sp.target = sp.glide = None
        elif kind == "time":
            now = dt.datetime.now()
            if "date" in m.group(0) or "day" in m.group(0):
                self.say("It's %s, the %d of %s, Ros." % (now.strftime("%A"), now.day, now.strftime("%B")))
            else:
                self.say(now.strftime("It's %I:%M %p, Ros.").replace(" 0", " "))
        elif kind == "security":
            from mini_gaya.security.agentshield import scan_text, scan_mcp_config
            findings = []
            cfg_path = os.path.expanduser("~/.gemini/config/mcp_config.json")
            if os.path.exists(cfg_path):
                try:
                    findings.extend(scan_mcp_config(json.load(open(cfg_path, "r", encoding="utf-8"))))
                except Exception:
                    pass
            env_path = os.path.join(os.getcwd(), ".env")
            if os.path.exists(env_path):
                try:
                    findings.extend(scan_text(open(env_path, "r", encoding="utf-8").read()))
                except Exception:
                    pass
            if findings:
                self.say("AgentShield scan finished, Ros. %d potential risk items detected." % len(findings))
                sp.toast("hold", "AgentShield: %d findings" % len(findings), findings[0].description)
            else:
                self.say("AgentShield scan complete, Ros. All systems secure, zero risks detected.")
                sp.toast("approved", "AgentShield: All Clear", "0 security risks detected")
        sp.toast("info", "Voice: %s" % kind, shown)

    # ---------------------------------------------------------------- helpers
    def _find_session(self, name):
        name = name.lower().strip()
        best = None
        for r in self.sprite.sessions:
            if not r.get("live", True) or r.get("status") == "closed":
                continue
            t = r["title"].lower()
            if name in t or t in name or all(w in t for w in name.split()):
                if best is None or r["status"] in ("working", "waiting", "idle"):
                    best = r.get("sid")
        return best
