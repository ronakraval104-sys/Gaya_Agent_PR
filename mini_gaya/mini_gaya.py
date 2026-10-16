"""GAYA sprite - the Command Core, free on the desktop. Replaces Coucou.

  * Drag it anywhere. It floats, breathes, blinks, glances toward your cursor,
    hops when a session finishes, shakes amber when it needs you, dozes when idle,
    gets dizzy if you poke it three times.
  * Click it  -> brief of your Antigravity sessions (pin with the pin button).
  * Permission requests -> a card beside it: Allow / Always / Deny / Terminal.
    Antigravity's questions (AskUserQuestion) -> the options as buttons.
  * Notifications -> speech bubbles: session waiting for you, subagent reported,
    EDIDTH PASS/FAIL, guard holds.
  * Sounds per event (mute from the tray). Hides itself during games.
  * Tray icon: click = show/hide.

Events come from gaya_sprite_hook.py over 127.0.0.1:8767 (HMAC-signed both
ways) and from the v10 log ~/.jarvis/logs/events.jsonl. Nothing is ever
allowed without Boss clicking - see the hook's docstring.
"""
import hashlib
import hmac
import json
import math
import os
import random
import re
import secrets
import struct
import sys
import time
import wave

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, QUrl
from PySide6.QtGui import (QColor, QCursor, QFont, QFontMetrics, QIcon, QPainter,
                           QPainterPath, QPen, QRadialGradient)
from PySide6.QtNetwork import QHostAddress, QTcpServer
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel, QMenu, QPlainTextEdit,
                               QPushButton, QSystemTrayIcon, QVBoxLayout, QWidget)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gaya_state  # noqa: E402
import gaya_sprite_hook as hk  # noqa: E402  (shared rules: safe_suggestions, canon)
from sprite_deck import Deck  # noqa: E402
from sprite_ui import RadialMenu, load_fonts, ui_font  # noqa: E402
from gaya_island import (STATE_RGB, ago, compose_core, fullscreen_busy,  # noqa: E402
                           read_sessions, to_pixmap)

GDIR = os.path.join(os.path.expanduser("~"), ".gaya")
JDIR = GDIR if os.path.exists(GDIR) else os.path.join(os.path.expanduser("~"), ".jarvis")
KEYFILE = os.path.join(JDIR, "secrets", "sprite.key")
PREFS = os.path.join(JDIR, "sprite.json")
SOUNDS = os.path.join(HERE, "sounds")

def get_user_salutation():
    try:
        prof_path = os.path.join(GDIR, "user_profile.json")
        if os.path.exists(prof_path):
            with open(prof_path, "r", encoding="utf-8") as f:
                d = json.load(f)
                prefix = d.get("prefix", "R0n")
                if prefix.lower() in ("r0n", "ron"):
                    return "Ros"
                return prefix
    except Exception:
        pass
    return "Ros"
PORT = 8767
SPRITE = 64                    # logical px of the core
BODY_H = 132                   # logical px tall, full-body mode
PAD = 26                       # room for shadow / hop / shake
DOZE_AFTER = 120               # s of no activity

ACCENT = {"waiting": "#ffb020", "hold": "#ffb020", "approved": "#2fd36f", "broken": "#ff3b3b",
          "info": "#8fd3ff", "spawning": "#8fd3ff"}
CARD_CSS = """
QWidget#card { background: rgba(10,10,12,242); border: 1px solid %s; border-radius: 12px; }
QLabel { color: #e9ecf1; font-family: 'Space Grotesk'; font-size: 9pt; background: transparent; }
QLabel#title { font-family: 'Space Grotesk'; font-weight: 600; font-size: 10pt; }
QLabel#muted { color: #8c9098; font-size: 8.5pt; }
QLabel#code { color: #d7e3ff; font-family: 'Space Mono'; font-size: 8.5pt;
              background: rgba(255,255,255,10); border-radius: 6px; padding: 6px; }
QPushButton { color: #e9ecf1; background: rgba(255,255,255,16); border: 1px solid rgba(255,255,255,30);
              border-radius: 8px; padding: 5px 12px; font-family: 'Space Grotesk'; font-weight: 600; font-size: 9pt; }
QPushButton:hover { background: rgba(255,255,255,34); }
QPushButton#allow { background: rgba(47,211,111,40); border-color: rgba(47,211,111,150); }
QPushButton#allow:hover { background: rgba(47,211,111,80); }
QPushButton#deny { background: rgba(255,59,59,34); border-color: rgba(255,59,59,140); }
QPushButton#deny:hover { background: rgba(255,59,59,70); }
QPushButton:checked { background: rgba(143,211,255,60); border-color: #8fd3ff; }
"""


# ------------------------------------------------------------------ sounds
def make_sounds():
    """Tiny synthetic cues, generated once (no assets to ship)."""
    os.makedirs(SOUNDS, exist_ok=True)
    cues = {"request": [(660, .09), (880, .13)], "done": [(784, .08), (1046, .16)],
            "error": [(330, .12), (247, .2)], "notify": [(988, .07)],
            "dizzy": [(520, .05), (440, .05), (520, .05), (390, .1)]}
    for name, notes in cues.items():
        path = os.path.join(SOUNDS, name + ".wav")
        if os.path.exists(path):
            continue
        rate, frames = 22050, b""
        for f, dur in notes:
            n = int(rate * dur)
            for i in range(n):
                env = min(1, i / 300) * (1 - i / n) ** 1.6
                v = 0.55 * env * (math.sin(2 * math.pi * f * i / rate)
                                  + 0.25 * math.sin(4 * math.pi * f * i / rate))
                frames += struct.pack("<h", int(v * 32767 * 0.6))
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(frames)


class Sound:
    def __init__(self):
        self.muted = False
        self.fx = {}
        try:
            from PySide6.QtMultimedia import QSoundEffect
            for f in os.listdir(SOUNDS):                 # CC0 Kenney cues (see sounds/LICENSE.txt)
                if f.endswith(".wav"):
                    e = QSoundEffect()
                    e.setSource(QUrl.fromLocalFile(os.path.join(SOUNDS, f)))
                    e.setVolume(0.32)
                    self.fx[f[:-4]] = e
        except Exception:
            pass

    def play(self, name):
        if not self.muted and name in self.fx:
            self.fx[name].play()


# ------------------------------------------------------------------ floating card base
class Bubble(QWidget):
    """Frameless, never steals focus, sits beside the sprite."""

    def __init__(self, sprite, accent="#8fd3ff", width=330):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
                         | Qt.WindowDoesNotAcceptFocus | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.sprite = sprite
        self.accent = accent
        self.tail_side = None            # "left" / "right" / None - set by place_bubble
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, self.TAIL)
        self.card = QWidget(objectName="card")
        self.card.setStyleSheet(CARD_CSS % accent)
        self.card.setFixedWidth(width)
        outer.addWidget(self.card)
        self.body = QVBoxLayout(self.card)
        self.body.setContentsMargins(14, 12, 14, 12)
        self.body.setSpacing(6)

    TAIL = 11

    def paintEvent(self, _):
        if not self.tail_side:
            return
        from PySide6.QtGui import QPolygonF
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        bottom = self.height() - self.TAIL
        if self.tail_side == "right":
            pts = [QPointF(self.width() - 40, bottom - 1), QPointF(self.width() - 18, bottom - 1),
                   QPointF(self.width() - 24, bottom + self.TAIL - 1)]
        else:
            pts = [QPointF(18, bottom - 1), QPointF(40, bottom - 1), QPointF(24, bottom + self.TAIL - 1)]
        col = QColor(self.accent) if self.accent.startswith("#") else QColor(255, 255, 255, 40)
        p.setPen(QPen(col, 1))
        p.setBrush(QColor(10, 10, 12, 242))
        p.drawPolygon(QPolygonF(pts))
        p.setPen(QColor(10, 10, 12, 242))               # hide the card edge behind the tail
        p.drawLine(QPointF(pts[0].x() + 1, bottom - 1), QPointF(pts[1].x() - 1, bottom - 1))
        p.end()

    def label(self, text, name=None, wrap=True):
        l = QLabel(text)
        if name:
            l.setObjectName(name)
        l.setWordWrap(wrap)
        l.setTextFormat(Qt.PlainText)
        self.body.addWidget(l)
        return l

    def place(self, stack_index=0, above=0):
        self.adjustSize()
        self.sprite.place_bubble(self, above)


# ------------------------------------------------------------------ permission / question card
SHOW_MAX = 20000           # a command longer than this is unreadable even scrolled -> Terminal only
PREVIEW = 300              # chars of a file write/edit previewed
SENSITIVE = ("/.claude/", "/.jarvis/", "/startup/", "settings.json", "settings.local.json",
             ".claude.json", ".mcp.json", "/.git/config", ".gitconfig", "/.config/",
             "profile.ps1", ".bashrc", ".bash_profile", ".zshrc", ".profile", "/.ssh/", "/.git/hooks/",
             "/appdata/roaming/microsoft/windows/start menu/")


# invisible-but-not-Cf code points (Hangul fillers, Mongolian/Khmer fillers, CGJ ...)
DEFAULT_IGNORABLE = {0x034F, 0x115F, 0x1160, 0x17B4, 0x17B5, 0x3164, 0xFFA0, 0x2800}


def reveal(text):
    """(safe_text, had_hidden). Control/format chars (bidi overrides like U+202E,
    zero-width chars, escapes) are shown as \\uXXXX so the card can't display a
    command that differs from what runs. Newlines and tabs are kept."""
    import unicodedata
    out, hidden = [], False
    for ch in str(text):
        o = ord(ch)
        if ch in "\n\t":
            out.append(ch)
        elif (unicodedata.category(ch) in ("Cc", "Cf", "Co", "Cs", "Zl", "Zp", "Mn", "Me", "Cn")
              or o in DEFAULT_IGNORABLE or 0xFE00 <= o <= 0xFE0F or 0xE0000 <= o <= 0xE0FFF
              or 0x180B <= o <= 0x180F or 0xFFF0 <= o <= 0xFFF8 or 0x1BCA0 <= o <= 0x1BCA3):
            out.append("\\u%04x" % ord(ch))
            hidden = True
        else:
            out.append(ch)
    return "".join(out), hidden


def breakable(text):
    """Wrap ANYWHERE: a zero-width space after every char, so no unbroken run
    (base64, $(...), long URLs) can run off the card unseen. Call on text that
    already went through reveal()."""
    return "​".join(str(text))


def _norm(p):
    """realpath expands 8.3 short names (CLAUDE~1 -> .claude) and links before
    any check; normpath folds .. segments."""
    try:
        p = os.path.realpath(str(p))
    except Exception:
        p = str(p)
    return os.path.normpath(p).replace("\\", "/").lower()


class RequestCard(Bubble):
    def __init__(self, sprite, req):
        super().__init__(sprite, "#ffb020", 380)
        self.req = req
        self.locked = set()          # buttons that stay disabled whatever happens
        self.decide_buttons = []
        p = req["payload"]
        tool = p.get("tool_name", "tool")
        proj = os.path.basename(str(p.get("cwd", "")).rstrip("\\/"))
        sess = sprite.session_title(p.get("session_id", ""))
        if tool == "AskUserQuestion":
            self._question(p)
            return
        self.arm_timer = QTimer(self, singleShot=True, timeout=self._rearm)
        self.label("GAYA needs your call - %s" % tool, "title")
        self.label("%s%s" % (sess or "session", ("  ·  " + proj) if proj else ""), "muted")
        text, complete, why = self.summary(tool, p.get("tool_input") or {}, req.get("truncated"),
                                           str(p.get("cwd", "")), req.get("sizes") or {})
        text, hidden = reveal(text)
        if hidden and complete:
            complete, why = False, "hidden characters (shown as \\uXXXX)"
        self.lock_reason = "" if complete else why
        if len(text) > 420 or text.count("\n") > 7:
            # long command: the WHOLE thing, in a scrollable box - readable means approvable
            from PySide6.QtGui import QTextOption
            box = QPlainTextEdit()
            box.setReadOnly(True)
            box.setPlainText(text)
            box.setWordWrapMode(QTextOption.WrapAnywhere)
            box.setFont(ui_font(8.5, family="Space Mono"))
            box.setStyleSheet("QPlainTextEdit { color:#d7e3ff; background: rgba(255,255,255,10); "
                              "border: 1px solid rgba(255,255,255,18); border-radius: 6px; padding: 4px; }")
            box.setFixedHeight(min(230, 18 + 15 * (text.count("\n") + len(text) // 70 + 1)))
            box.setFocusPolicy(Qt.NoFocus)
            self.body.addWidget(box)
            self.label("%d characters - scroll to read it all" % len(text), "muted")
        else:
            code = self.label(breakable(text), "code")
            code.setWordWrap(True)
        if not complete:
            warn = self.label("Allow is off: %s. Use Terminal to answer it in Antigravity." % why, None)
            warn.setStyleSheet("color:#ffb020")
        row = QHBoxLayout()
        btn = {}
        for text_, name, d in (("Allow", "allow", "allow"), ("Always", None, "always"),
                               ("Deny", "deny", "deny"), ("Terminal", None, "terminal")):
            b = QPushButton(text_)
            if name:
                b.setObjectName(name)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, d=d: sprite.decide(self.req, d))
            row.addWidget(b)
            btn[d] = b
            self.decide_buttons.append(b)
        self.body.addLayout(row)
        safe = hk.safe_suggestions(p)
        if not complete:                               # never approve something half-read
            self.locked |= {btn["allow"], btn["always"]}
            btn["allow"].setText("Allow ✕")
            btn["allow"].setToolTip("Locked: " + why)
        if not safe:
            self.locked.add(btn["always"])
            btn["always"].setToolTip("No specific rule to save - Always is off for this one")
        else:
            rules = "; ".join("%s(%s)" % (r.get("toolName"), r.get("ruleContent", "")) for s in safe
                              for r in s["rules"])
            dest = ", ".join(sorted({s.get("destination", "?") for s in safe}))
            rules, rule_hidden = reveal(rules)
            if len(rules) > 300 or rule_hidden:       # can't show the whole rule -> can't save it
                self.locked.add(btn["always"])
                rules = rules[:300] + (" [cut]" if len(rules) > 300 else "")
            self.label(breakable("Always saves: %s  ->  %s" % (rules, dest)), "muted")
        for b in self.locked:
            b.setEnabled(False)

    def arm(self, ms=700):
        """Buttons go dead for a moment whenever the card appears or moves, so a
        click meant for the card that was here a moment ago can't land on this one."""
        for b in self.decide_buttons + ([self.send] if hasattr(self, "send") else []):
            b.setEnabled(False)
        if not hasattr(self, "arm_timer"):
            self.arm_timer = QTimer(self, singleShot=True, timeout=self._rearm)
        self.arm_timer.start(ms)                       # ONE timer per card - each arm restarts it

    @staticmethod
    def summary(tool, ti, truncated, cwd="", sizes=None):
        """(text, complete, why). Everything that will run is shown, wrapped anywhere;
        whatever can't be shown in full locks Allow/Always. File bodies are previews
        by design (real size printed from `sizes`) and don't lock."""
        sizes = sizes or {}
        if truncated:
            return json.dumps(ti, ensure_ascii=False)[:SHOW_MAX], False, "too long to show"
        if tool in ("Bash", "PowerShell") and "command" in ti:
            txt = str(ti["command"])
            extra = {k: v for k, v in ti.items() if k not in ("command", "description")}
            if extra:
                txt += "\n[flags] " + json.dumps(extra, ensure_ascii=False)
            if len(txt) > SHOW_MAX:
                return txt[:SHOW_MAX], False, "too long to show"
            return txt, True, ""
        if tool == "MultiEdit":
            return "%s\n%d edits" % (ti.get("file_path", ""), len(ti.get("edits") or [])), False, \
                "multi-file edit"
        if tool in ("Write", "Edit", "NotebookEdit") and ("file_path" in ti or "notebook_path" in ti):
            path = str(ti.get("file_path") or ti.get("notebook_path"))
            shown = {"file_path", "notebook_path", "old_string", "new_string", "content", "new_source"}
            if ti.get("old_string") is not None:
                old, body = str(ti.get("old_string")), str(ti.get("new_string"))
                n_old, n_new = sizes.get("old_string", len(old)), sizes.get("new_string", len(body))
                txt = "%s\nreplace %d chars with %d chars\n- %s%s" % (
                    path, n_old, n_new, old[:200], " [+%d more]" % (n_old - 200) if n_old > 200 else "")
            else:
                body = str(ti.get("content") or ti.get("new_source") or "")
                n_new = sizes.get("content", sizes.get("new_source", len(body)))
                txt = "%s\nwrite %d chars" % (path, n_new)
            flags = {k: v for k, v in ti.items() if k not in shown}       # replace_all, edit_mode, ...
            if flags:
                txt += "\n[flags] " + json.dumps(flags, ensure_ascii=False)
            txt += "\npreview: %d of %d chars\n+ %s" % (min(PREVIEW, n_new), n_new, body[:PREVIEW])
            np, nc = _norm(path), _norm(cwd).rstrip("/") + "/"
            if re.search(r"~\d", np):                  # a short name realpath couldn't expand
                return txt, False, "short (8.3) path name"
            if any(s in np for s in SENSITIVE):
                return txt, False, "sensitive file"
            if cwd and not np.startswith(nc):
                return txt, False, "outside this project"
            return txt, True, ""
        txt = json.dumps(ti, ensure_ascii=False, indent=0)      # MCP / other tools: every argument
        if len(txt) > SHOW_MAX:
            return txt[:SHOW_MAX], False, "too long to show"
        return txt, True, ""

    def _question(self, p):
        qs = (p.get("tool_input") or {}).get("questions") or []
        self.label("Antigravity is asking", "title")
        self.picks = {}
        self.buttons = {}
        for q in qs[:4]:
            self.label(breakable(reveal(q.get("question", ""))[0]), None)
            grid = QGridLayout()
            multi = bool(q.get("multiSelect"))
            for i, o in enumerate((q.get("options") or [])[:6]):
                b = QPushButton(reveal(o.get("label", "?"))[0])
                b.setProperty("label", o.get("label", "?"))     # the exact label goes back
                b.setCheckable(True)
                b.setToolTip(o.get("description", ""))
                b.setCursor(Qt.PointingHandCursor)
                b.clicked.connect(lambda _=False, q=q, b=b, m=multi: self._pick(q, b, m))
                self.buttons.setdefault(q.get("question"), []).append(b)
                grid.addWidget(b, i // 2, i % 2)
            self.body.addLayout(grid)
        row = QHBoxLayout()
        self.send = QPushButton("Send", objectName="allow")
        self.send.setEnabled(False)
        self.send.clicked.connect(self._submit)
        term = QPushButton("Terminal")
        term.clicked.connect(lambda: self.sprite.decide(self.req, "terminal"))
        row.addWidget(self.send)
        row.addWidget(term)
        self.body.addLayout(row)
        self.qs = qs
        self.decide_buttons = [term] + [b for bs in self.buttons.values() for b in bs]

    def _rearm(self):
        for b in self.decide_buttons:
            if b not in self.locked:
                b.setEnabled(True)
        if hasattr(self, "send"):
            self.send.setEnabled(len(getattr(self, "picks", {})) == len(getattr(self, "qs", [])) > 0)

    def _pick(self, q, b, multi):
        key = q.get("question")
        if not multi:
            for other in self.buttons[key]:
                other.setChecked(other is b)
            self.picks[key] = b.property("label")
            if len(self.qs) == 1:                    # one single-choice question: send now
                self._submit()
                return
        else:
            sel = [x.property("label") for x in self.buttons[key] if x.isChecked()]
            if sel:
                self.picks[key] = sel
            else:
                self.picks.pop(key, None)
        self.send.setEnabled(len(self.picks) == len(self.qs))

    def _submit(self):
        self.sprite.decide(self.req, "answer", answers=self.picks)


# ------------------------------------------------------------------ brief panel
class Brief(Bubble):
    def __init__(self, sprite):
        super().__init__(sprite, "rgba(255,255,255,40)", 360)
        self.pinned = False
        top = QHBoxLayout()
        self.head = QLabel("MINI GAYA", objectName="title")
        top.addWidget(self.head)
        top.addStretch(1)
        self.pin = QPushButton("Pin")
        self.pin.setCheckable(True)
        self.pin.clicked.connect(lambda: setattr(self, "pinned", self.pin.isChecked()))
        top.addWidget(self.pin)
        self.body.addLayout(top)
        self.status = self.label("", "muted")
        self.rows = QVBoxLayout()
        self.rows.setSpacing(8)
        self.body.addLayout(self.rows)
        self.foot = self.label("", "muted")

    def refresh(self):
        s = self.sprite
        self.status.setText("%s  ·  guard %s  ·  %d holds today%s" % (
            s.state.upper(), s.armed, s.holds, "  ·  muted" if s.sound.muted else ""))
        while self.rows.count():
            w = self.rows.takeAt(0).widget()
            if w:
                w.deleteLater()
        if not s.sessions:
            l = QLabel("No Antigravity sessions in the last 3 hours.", objectName="muted")
            self.rows.addWidget(l)
        for r in s.sessions[:6]:
            colour = {"working": "#57c7ff", "waiting": "#ffb020", "idle": "#6a6e76"}[r["status"]]
            what = {"working": "working" + (" · " + r["tool"] if r["tool"] else ""),
                    "waiting": "waiting for you · " + ago(r["idle_s"]),
                    "idle": "idle · " + ago(r["idle_s"])}[r["status"]]
            sub = r["reply"] if r["status"] == "waiting" and r["reply"] else (
                "> " + r["prompt"] if r["prompt"] else r["cwd"])
            fm = QFontMetrics(ui_font(8.5))
            l = QLabel()
            l.setTextFormat(Qt.RichText)
            esc = lambda t: (t or "").replace("&", "&amp;").replace("<", "&lt;")
            l.setText('<span style="color:%s">●</span>&nbsp; <b>%s</b>'
                      '<span style="color:%s;font-size:7.5pt">&nbsp;&nbsp;%s</span><br>'
                      '<span style="color:#8c9098;font-size:8pt">%s</span>'
                      % (colour, esc(fm.elidedText(r["title"], Qt.ElideRight, 190)), colour, esc(what),
                         esc(fm.elidedText(sub, Qt.ElideRight, 320))))
            self.rows.addWidget(l)
        more = len(s.sessions) - 6
        self.foot.setText(("+%d more · " % more if more > 0 else "") + "click me again to close")
        self.adjustSize()


# ------------------------------------------------------------------ the sprite
class Sprite(QWidget):
    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
                         | Qt.WindowDoesNotAcceptFocus | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setMouseTracking(True)
        self.setWindowTitle('Mini Gaya')
        self.setObjectName('MiniGayaSprite')
        load_fonts()
        self.setFixedSize(SPRITE + 2 * PAD, SPRITE + 2 * PAD)
        self.dpr = QApplication.primaryScreen().devicePixelRatio()
        make_sounds()
        self.sound = Sound()
        self.key = self._key()

        px = round(SPRITE * self.dpr)
        self.core = {s: (to_pixmap(compose_core(rgb, .5, .2, px=px), self.dpr),
                         to_pixmap(compose_core(rgb, 1.0, .8, px=px), self.dpr))
                     for s, rgb in STATE_RGB.items()}
        self.core_sleep = to_pixmap(compose_core(STATE_RGB["asleep"], .1, 0, .65, px=px), self.dpr)

        self.state, self.detail, self.armed, self.holds = "idle", "", "?", 0
        self.sessions, self.prev_status, self.titles = [], {}, {}
        self.last_activity = time.time()
        self.t0 = time.time()
        self.anim = {"hop": 0.0, "shake": 0.0, "dizzy": 0.0, "pulse": 0.0}
        self.clicks = []
        self.hover = False
        self.user_hidden = False
        self.drag = None
        self.requests = []           # pending permission requests
        self.cards = {}              # request id -> RequestCard
        self.toasts = []             # live toast bubbles
        p = self._load()
        self.roam = p.get("roam", True)
        self.brief_day = p.get("brief_day", "")
        self.scale_factor = float(p.get("scale", 1.0))
        import sprite_body
        self.body = sprite_body.Body(self.dpr, BODY_H) if sprite_body.available() else None
        self.body_on = bool(self.body) and p.get("body", True)
        self._apply_size()
        self.panel = Deck(self)      # the GAYA Deck (click the sprite)
        self.brief = self.panel      # old name, same thing
        from sprite_chat import Composer
        self.composer = Composer(self)
        self.listening = False
        self.voice = None
        if p.get("voice", True):
            self._start_voice(wake_word=p.get("wake_word", True))
        self.ring = RadialMenu(self)
        self.sal = get_user_salutation()
        self._active_log_file = gaya_state.get_active_log_path()
        try:
            self.log_pos = os.path.getsize(self._active_log_file) if (self._active_log_file and os.path.exists(self._active_log_file)) else 0
        except OSError:
            self.log_pos = 0
        g = QApplication.primaryScreen().availableGeometry()
        self.move(p.get("x", g.right() - self.width() - 40), p.get("y", g.bottom() - self.height() - 60))
        # physics: it glides, gets flung, bounces off edges, roams on its own
        self.fpos = [float(self.x()), float(self.y())]
        self.vel = [0.0, 0.0]
        self.target = None
        self.drag_trail = []
        self.next_roam = time.time() + 20

        self.server = QTcpServer(self)
        self.server.newConnection.connect(self._accept)
        if not self.server.listen(QHostAddress.LocalHost, PORT):
            print("Mini Gaya sprite: port %d busy - is another sprite running?" % PORT)

        self.glide, self.walking, self.facing = None, False, 1
        tick = QTimer(self, timeout=self._tick, interval=16)
        tick.setTimerType(Qt.PreciseTimer)
        tick.start()
        QTimer(self, timeout=self._poll, interval=1500).start()
        QTimer(self, timeout=self._visibility, interval=2000).start()
        self._tray()
        self._poll()

    # ---------------------------------------------------------------- key
    def _key(self):
        os.makedirs(os.path.dirname(KEYFILE), exist_ok=True)
        if not os.path.exists(KEYFILE):
            with open(KEYFILE, "w") as f:
                f.write(secrets.token_hex(32))
        return open(KEYFILE, "rb").read().strip()

    def _sig(self, *parts):
        return hmac.new(self.key, "|".join(parts).encode(), hashlib.sha256).hexdigest()

    # ---------------------------------------------------------------- hook server
    def _accept(self):
        while self.server.hasPendingConnections():
            sock = self.server.nextPendingConnection()
            sock.setProperty("rid", "")
            sock.readyRead.connect(lambda s=sock: self._read(s))
            sock.disconnected.connect(sock.deleteLater)    # no socket pile-up
            # anything that hasn't proved the key within 2 s is dropped
            QTimer.singleShot(2000, lambda s=sock: self._drop_unauth(s))

    @staticmethod
    def _drop_unauth(sock):
        try:
            if not sock.property("rid"):
                sock.close()
        except RuntimeError:
            pass                                       # already gone - fine

    def _read(self, sock):
        if not sock.canReadLine() and sock.bytesAvailable() > 65536:
            sock.close()                               # no newline in 64 KB -> junk
            return
        while sock.canReadLine():
            try:
                msg = json.loads(bytes(sock.readLine()).decode("utf-8"))
            except Exception:
                sock.close()
                return
            rid = sock.property("rid")
            if not rid:                                # stage 1: hello + proof of key
                hello = str(msg.get("hello", ""))
                if not hello or not hmac.compare_digest(str(msg.get("auth", "")), self._sig("hook", hello)):
                    sock.close()
                    return
                sock.setProperty("rid", hello)
                sock.write((json.dumps({"ready": self._sig("ready", hello)}) + "\n").encode())
                sock.flush()
                continue
            # stage 2: the payload (only ever sent after we proved the key)
            self._on_event(msg.get("event", ""), msg.get("payload") or {}, rid, sock,
                           bool(msg.get("truncated")), msg.get("sizes") or {})
            return

    def _on_event(self, event, p, rid, sock, truncated=False, sizes=None):
        self.last_activity = time.time()
        sid = str(p.get("session_id", ""))[:8]
        import logging
        logging.info("hook event %s session=%s tool=%s", event, sid, p.get("tool_name", ""))
        if event == "PermissionRequest":
            if not self.isVisible():                   # hidden (game / Boss) -> terminal asks
                logging.info("request %s: J hidden -> terminal", rid[:8])
                sock.close()
                return
            req = {"id": rid, "sock": sock, "payload": p, "t": time.time(), "truncated": truncated,
                   "sizes": sizes or {}}
            self.requests.append(req)
            sock.disconnected.connect(lambda r=req: self._request_gone(r))
            self.fly_to_cursor()                       # it comes to you (fast, ~1 s)
            card = RequestCard(self, req)
            self.cards[rid] = card
            self._layout_bubbles()
            card.show()
            card.arm(int(self.glide["dur"] * 1000) + 300 if self.glide else 700)   # dead while in flight
            sock.write((json.dumps({"ack": self._sig("ack", rid)}) + "\n").encode())
            sock.flush()
            self.anim["shake"] = 1.0
            self.sound.play("request")
            logging.info("request %s: card shown (%s) at %s%s", rid[:8], p.get("tool_name"), card.pos(),
                         (" ALLOW LOCKED: " + card.lock_reason) if card.lock_reason else "")
            self.speak("%s, %s wants to run %s. %s" % (
                self.sal,
                self.session_title(sid) or "an Antigravity session", p.get("tool_name", "a tool"),
                "Allow, or deny?" if not card.lock_reason else "It's locked - answer it in Antigravity."),
                interrupt=True)
            QTimer.singleShot(106_000, lambda r=req: self._request_gone(r))
            return
        if event == "VoiceText":                       # simulated voice command (tests / demos)
            self._safe_close(sock)                     # the hook has already hung up
            if self.voice:
                self.voice._on_heard(str(p.get("text", "")), 0.0, 0.0)
            return
        if event == "Say":                             # a session talks back through J (voice/say.py)
            self._safe_close(sock)
            text = " ".join(str(p.get("text", "")).split())[:400]
            if text:
                self.toast("info", self.session_title(sid) or "Gaya", text[:100])
                self.speak(text, interrupt=bool(p.get("interrupt")))
                logging.info("say: %r", text[:80])
            return
        if event == "Stop":
            self.anim["hop"] = 1.0
            self.sound.play("done")
            msg = " ".join(str(p.get("last_assistant_message", "")).split())[:110]
            self.toast("waiting", "%s - done, waiting for you" % (self.session_title(sid) or "Antigravity session"), msg)
            first = re.split(r"(?<=[.!?])\s", " ".join(str(p.get("last_assistant_message", "")).split()))[0][:140]
            self.speak("%s is done, %s. %s" % (self.session_title(sid) or "Antigravity session", self.sal, first))
        elif event == "StopFailure":
            self.sound.play("error")
            self.toast("broken", "An Antigravity session hit an error", str(p.get("error", ""))[:100])
        elif event == "Notification" and p.get("notification_type") in ("idle_prompt", "agent_needs_input",
                                                                          "elicitation_dialog"):
            self.toast("waiting", p.get("title") or "Antigravity needs you", str(p.get("message", ""))[:100])
        elif event == "SubagentStart":
            self.anim["pulse"] = 1.0
        elif event == "SessionStart":
            self.anim["hop"] = 0.6
        elif event in ("SetScale", "scale", "set_scale"):
            scale = float(p.get("scale", 1.0))
            self.set_scale(scale)
            try:
                sock.write((json.dumps({"ok": True, "scale": self.scale_factor}) + "\n").encode())
                sock.flush()
            except Exception:
                pass
            self._safe_close(sock)
            return
        self._safe_close(sock)

    def set_scale(self, factor):
        try:
            s = max(0.5, min(2.0, float(factor)))
        except (ValueError, TypeError):
            return
        self.scale_factor = round(s, 2)
        self._apply_size()
        self._save()
        self.update()
        self._layout_bubbles()
        self.anim["pulse"] = 0.8
        self.sound.play("notify")

    @staticmethod
    def _safe_close(sock):
        try:
            sock.close()
        except RuntimeError:
            pass                                       # peer already hung up and Qt deleted it

    def decide(self, req, decision, answers=None):
        import logging
        if req not in self.requests:
            logging.info("decide %s ignored - request already closed", decision)
            return
        out = {"decision": decision, "sig": self._sig("decision", req["id"], decision, hk.canon(answers))}
        if answers is not None:
            out["answers"] = answers
        try:
            req["sock"].write((json.dumps(out) + "\n").encode())
            req["sock"].flush()
            logging.info("request %s: decision %s sent", req["id"][:8], decision)
        except Exception as e:
            logging.error("request %s: could not send %s: %s", req["id"][:8], decision, e)
        self._close_request(req)
        self.sound.play("notify")
        self.anim["hop"] = 0.5
        if decision == "terminal":
            # hand back to Antigravity's own prompt - and put that session in front
            from sprite_ui import focus_session
            sid = str(req["payload"].get("session_id", ""))
            focus_session({"sid": sid, "cwd": "", "entry": "antigravity"})
            self.toast("info", "Handed back to Antigravity", "answer it in the chat - I've brought it forward")

    def _request_gone(self, req):
        if req in self.requests:                       # answered in the terminal / timed out
            self._close_request(req)

    def _close_request(self, req):
        if req in self.requests:
            self.requests.remove(req)
        card = self.cards.pop(req["id"], None)
        if card:
            card.hide()
            card.deleteLater()
        try:
            if req["sock"] is not None:
                req["sock"].disconnectFromHost()
                req["sock"].deleteLater()
        except Exception:
            pass
        self._layout_bubbles()

    # ---------------------------------------------------------------- toasts
    def toast(self, kind, title, body=""):
        if not self.isVisible():                       # in a game / hidden: keep it for later
            self.missed = (getattr(self, "missed", []) + [(kind, title, body)])[-20:]
            return
        b = Bubble(self, ACCENT.get(kind, "#8fd3ff"), 300)
        t = b.label(title, "title")
        t.setStyleSheet("color: %s" % ACCENT.get(kind, "#e9ecf1"))
        if body:
            b.label(body, "muted")
        b.mousePressEvent = lambda e, b=b: self._drop_toast(b)
        self.toasts.append(b)
        while len(self.toasts) > 3:
            old = self.toasts.pop(0)
            try:
                old.hide()
                old.close()
                old.deleteLater()
            except Exception:
                pass
        b.adjustSize()
        b.show()
        self._layout_bubbles()
        QTimer.singleShot(6000, lambda b=b: self._drop_toast(b))

    def _drop_toast(self, b):
        if b in self.toasts:
            self.toasts.remove(b)
        try:
            b.hide()
            b.close()
            b.deleteLater()
        except Exception:
            pass
        self._layout_bubbles()

    # ---------------------------------------------------------------- bubble layout
    def _layout_bubbles(self):
        stack = [self.cards[r["id"]] for r in self.requests if r["id"] in self.cards] + list(self.toasts)
        if self.panel.isVisible():
            stack.append(self.panel)
        above = 0
        for i, w in enumerate(stack):
            w.adjustSize()
            self.place_bubble(w, above)
            # a card re-arms only when it CHANGES SLOT (another card closed under it)
            # or appears - not when the whole stack rides along with J
            if isinstance(w, RequestCard) and (getattr(w, "_slot", None) != i or not w.isVisible()):
                w.arm()
            w._slot = i
            above += w.height() + 8

    def head_point(self):
        """Screen point just above the visor - where speech comes from."""
        me = self.geometry()
        vis_h = getattr(self, "vis_h", SPRITE)
        scale = getattr(self, "scale_factor", 1.0)
        return me.center().x(), me.top() + int(PAD * scale) + int(vis_h * (0.08 if self.body_on else 0.15))

    def place_bubble(self, w, above):
        """Speech-bubble placement: the first bubble sits just above the head
        with its tail pointing at the visor; more stack upward."""
        scr = self.screen() or QApplication.primaryScreen()
        g = scr.availableGeometry() if scr else QRect(0, 0, 1920, 1080)
        hx, hy = self.head_point()
        right_side = hx > g.center().x()
        tail_px = getattr(w, "TAIL", 0)
        if right_side:
            x = hx - w.width() + 28                        # bubble to the left, tail at its right end
        else:
            x = hx - 28                                    # bubble to the right, tail at its left end
        y = hy - 6 - above - w.height()
        if y < g.top() + 4:                                # no room above: hang beside the head
            y = hy - 10 + above
            x = hx - w.width() - 16 if right_side else hx + 16
            if hasattr(w, "tail_side"):
                w.tail_side = None
        elif hasattr(w, "tail_side"):
            w.tail_side = ("right" if right_side else "left") if above == 0 else None
        x = max(g.left() + 4, min(x, g.right() - w.width() - 4))
        y = max(g.top() + 4, min(y, g.bottom() - w.height() - 4))
        w.move(x, y)
        w.update()

    # ---------------------------------------------------------------- polling
    def _log_size(self):
        try:
            return os.path.getsize(gaya_state.get_active_log_path())
        except OSError:
            return 0

    def session_title(self, sid):
        sid = str(sid)[:8]
        return self.titles.get(sid, "")

    def _poll(self):
        try:
            s = gaya_state.current()
            self.state, self.detail = s["state"], s.get("detail", "")
            self.armed, self.holds = s.get("armed", "?"), s.get("holds_today", 0)
        except Exception as e:
            self.state, self.detail = "broken", str(e)[:60]
        try:
            self.sessions = read_sessions()
            self.titles = {r["id"]: r["title"] for r in self.sessions}
        except Exception:
            pass
        if any(r["status"] == "working" for r in self.sessions):
            self.last_activity = time.time()
        self._log_events()
        try:
            from context.budgeter import calculate_pressure, should_warn_pressure
            working_sess = [r for r in self.sessions if r.get("turns")]
            if working_sess:
                max_turns = max(r.get("turns", 0) for r in working_sess)
                pressure = calculate_pressure(step_count=max_turns, transcript_bytes=max_turns * 3000)
                if should_warn_pressure(pressure) and not getattr(self, "_warned_pressure", False):
                    self._warned_pressure = True
                    self.toast("hold", "Context Pressure High", "Session at %d%% budget" % int(pressure * 100))
                elif not should_warn_pressure(pressure):
                    self._warned_pressure = False
        except Exception:
            pass
        if self.panel.isVisible():
            self.panel.refresh()
        self._maybe_roam()
        # new day while GAYA kept running (laptop woke from sleep): morning brief once
        if (time.strftime("%Y-%m-%d") != self.brief_day and time.localtime().tm_hour >= 5
                and self.isVisible() and not getattr(self, "daily", None) in self.toasts):
            self.show_daily_brief()
        self.tray.setToolTip("Mini Gaya - %s" % self.state)

    # ---------------------------------------------------------------- movement
    def _screen_box(self):
        g = self.screen().availableGeometry()
        return g.left() - PAD // 2, g.top(), g.right() - self.width() + PAD // 2, g.bottom() - self.height() + PAD // 2

    def glide_to(self, x, y, speed=170.0, walk=False):
        """Eased glide (or walk) to a spot: smooth start, smooth stop, no spring wobble."""
        x0, y0, x1, y1 = self._screen_box()
        tx, ty = max(x0, min(x, x1)), max(y0, min(y, y1))
        dist = math.hypot(tx - self.fpos[0], ty - self.fpos[1])
        if dist < 2:
            return
        dur = max(0.3, min(9.0, dist / speed))
        self.target = (tx, ty)
        self.glide = {"from": tuple(self.fpos), "to": (tx, ty), "t0": time.monotonic(), "dur": dur,
                      "walk": walk}
        self.vel = [0.0, 0.0]

    def fly_to_cursor(self):
        """Quick hop to where you're working (<= ~1 s) so the card lands near the cursor."""
        c = QCursor.pos()
        self.glide_to(c.x() + 40, c.y() - self.height() // 2, speed=1500.0)

    def _maybe_roam(self):
        if not self.roam or self.drag or self.hover or self.requests or self.target \
                or self.panel.isVisible() or self.ring.isVisible() or self.dozing() \
                or time.time() < self.next_roam:
            return
        x0, y0, x1, y1 = self._screen_box()
        # wander along the lower part of the screen, away from where it is now
        if random.random() < 0.65:
            # a walk along the bottom of the screen
            nx = random.uniform(x0 + (x1 - x0) * 0.06, x1 - (x1 - x0) * 0.04)
            if abs(nx - self.fpos[0]) < 260:
                nx = x0 + (x1 - nx)
            import sprite_body
            self.glide_to(nx, y1, speed=sprite_body.WALK_SPEED * BODY_H / 132.0, walk=True)
        else:
            # a float up to somewhere new
            nx = random.uniform(x0 + (x1 - x0) * 0.08, x1 - (x1 - x0) * 0.04)
            ny = random.uniform(y0 + (y1 - y0) * 0.45, y1)
            self.glide_to(nx, ny, speed=150.0)
        self.next_roam = time.time() + random.uniform(30, 70)

    def _log_events(self):
        log_path = gaya_state.get_active_log_path()
        if not log_path or not os.path.exists(log_path):
            return
        if getattr(self, "_active_log_file", None) != log_path:
            self._active_log_file = log_path
            try:
                self.log_pos = os.path.getsize(log_path)
            except OSError:
                self.log_pos = 0
            return

        try:
            size = os.path.getsize(log_path)
        except OSError:
            return

        if size < self.log_pos:
            self.log_pos = size
            return
        if size == self.log_pos:
            return

        try:
            with open(log_path, "rb") as f:
                f.seek(self.log_pos)
                chunk = f.read().decode("utf-8", "replace")
        except OSError:
            return
        self.log_pos = size
        is_antigravity = "transcript.jsonl" in log_path

        seen_logos_pass = False
        waiting_event = None
        subagent_event = None

        for ln in chunk.splitlines():
            try:
                e = json.loads(ln)
            except ValueError:
                continue
            if is_antigravity:
                content = str(e.get("content", ""))
                tool_calls = e.get("tool_calls") or []
                if "[🛡️ LOGOS]" in content and "PASS" in content:
                    seen_logos_pass = True
                elif tool_calls and isinstance(tool_calls, list):
                    tc = tool_calls[0]
                    t_name = tc.get("name", "")
                    args = tc.get("args") or {}
                    t_summary = args.get("toolSummary") or args.get("toolAction") or t_name
                    if t_name == "ask_question":
                        waiting_event = str(t_summary)[:90]
                    elif t_name == "invoke_subagent":
                        subagent_event = str(t_summary)[:90]
            else:
                if e.get("ev") == "guard" and e.get("decision") == "deny":
                    self.toast("hold", "Guard blocked %s" % (e.get("tool") or "a call"),
                               (e.get("reason") or "")[:100])
                elif e.get("ev") == "subagent_stop":
                    v = str(e.get("verdict") or "")
                    if v.startswith("PASS"):
                        seen_logos_pass = True
                    elif v.startswith("FAIL"):
                        self.sound.play("error")
                        self.toast("broken", "🛡️ LOGOS: FAIL", "fixes needed - report saved to the KB")
                        self.speak("LOGOS held it. Fixes needed, %s." % self.sal)
                    else:
                        self.toast("info", "%s reported back" % str(e.get("agent", "agent")).upper(), "saved to the KB")

        if seen_logos_pass:
            self.sound.play("done")
            self.anim["hop"] = 1.0
            self.toast("approved", "🛡️ LOGOS signed off - PASS", "Gate verified")
            self.speak("LOGOS passed it, %s." % self.sal)
        if waiting_event:
            self.sound.play("alert")
            self.toast("hold", "Antigravity is waiting", waiting_event)
            self.speak("Antigravity needs your input, %s." % self.sal)
        elif subagent_event:
            self.toast("spawning", "Subagents dispatched", subagent_event)

    # ---------------------------------------------------------------- visibility
    def _visibility(self):
        show = not self.user_hidden and not fullscreen_busy()
        widgets = [self.panel, self.ring] + list(self.cards.values()) + list(self.toasts)
        if show and not self.isVisible():
            self.show()
            for c in self.cards.values():
                c.arm()                                # back from a game: no stray clicks
                c.show()
            missed, self.missed = getattr(self, "missed", []), []
            if missed:
                kind, title, body = missed[-1]
                more = len(missed) - 1
                self.toast(kind, "While you were away%s" % (" (+%d more)" % more if more else ""),
                           "%s - %s" % (title, body) if body else title)
        elif not show and self.isVisible():
            self.hide()
            for w in widgets:
                w.hide()

    def toggle(self):
        self.user_hidden = not self.user_hidden
        self._visibility()

    # ---------------------------------------------------------------- animation
    def _tick(self):
        for k in self.anim:
            self.anim[k] = max(0.0, self.anim[k] - 0.016 / {"hop": .7, "shake": .9, "dizzy": 1.4, "pulse": 1.2}[k])
        now = time.monotonic()
        dt = min(0.05, max(0.001, now - getattr(self, "_last_tick", now)))
        self._last_tick = now
        if not self.drag:
            self._physics(dt, now)
        self.update()

    def _physics(self, dt, now):
        """Time-based motion (smooth at any frame rate).
        glide: eased tween A->B (easeInOutSine) - roaming, walking, flying to Boss
        fling: velocity in px/s with exponential drag and soft edge bounces."""
        x, y = self.fpos
        g = getattr(self, "glide", None)
        if g:
            u = min(1.0, (now - g["t0"]) / g["dur"])
            e = 0.5 - 0.5 * math.cos(math.pi * u)
            nx = g["from"][0] + (g["to"][0] - g["from"][0]) * e
            ny = g["from"][1] + (g["to"][1] - g["from"][1]) * e
            # px/frame-ish velocity just for the lean / facing
            self.vel = [(nx - x) / max(dt, 1e-3) * 0.016, (ny - y) / max(dt, 1e-3) * 0.016]
            self.walking = g["walk"] and u < 1.0
            if g["walk"] and abs(g["to"][0] - g["from"][0]) > 1:
                self.facing = 1 if g["to"][0] > g["from"][0] else -1
            x, y = nx, ny
            if u >= 1.0:
                self.glide, self.target, self.vel, self.walking = None, None, [0.0, 0.0], False
                for c in self.cards.values():
                    c.arm(400)                         # landed: a short settle, then clickable
                self._save()
                if self.toasts or self.requests or self.panel.isVisible():
                    self._layout_bubbles()
        else:
            vx, vy = self.vel[0] / 0.016, self.vel[1] / 0.016      # stored as px/frame -> px/s
            if abs(vx) + abs(vy) < 20:
                if self.vel != [0.0, 0.0]:
                    self.vel = [0.0, 0.0]
                    self._save()
                    if self.toasts or self.requests or self.panel.isVisible():
                        self._layout_bubbles()
                return
            decay = math.exp(-2.6 * dt)
            vx, vy = vx * decay, vy * decay
            x += vx * dt
            y += vy * dt
            x0, y0, x1, y1 = self._screen_box()
            if x < x0 or x > x1:                       # soft bounce + a little squash
                x = max(x0, min(x, x1))
                vx = -vx * 0.42
                self.anim["hop"] = max(self.anim["hop"], 0.35)
            if y < y0 or y > y1:
                y = max(y0, min(y, y1))
                vy = -vy * 0.42
            self.vel = [vx * 0.016, vy * 0.016]
        self.fpos = [x, y]
        rx, ry = round(x), round(y)
        if (rx, ry) != (self.x(), self.y()):
            self.move(rx, ry)
            if self.toasts or self.requests or self.panel.isVisible():
                self._layout_bubbles()

    def dozing(self):
        return (time.time() - self.last_activity > DOZE_AFTER and not self.requests and not self.hover
                and self.state in ("idle", "asleep"))

    def paintEvent(self, _):
        t = time.time() - self.t0
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        st = "hold" if self.requests else self.state
        doze = self.dozing()

        scale = getattr(self, "scale_factor", 1.0)
        if scale != 1.0:
            p.scale(scale, scale)

        bw = getattr(self, "base_w", self.width())
        bob = math.sin(t * (0.9 if not doze else 0.45)) * 3
        hop = -math.sin(math.pi * (1 - self.anim["hop"])) * 14 if self.anim["hop"] > 0 else 0
        shake = math.sin(t * 60) * 4 * self.anim["shake"]
        cx = bw / 2 + shake
        cy = PAD + SPRITE / 2 + bob + hop
        if self.body_on:                               # full-body commander
            self.body.paint(self, p, t, st, doze, hop, shake, PAD)
            self._paint_listening(p, t)
            p.end()
            return

        # ground shadow - it floats, it isn't pasted
        sh_w = SPRITE * (0.62 - 0.12 * (abs(hop) / 14))
        g = QRadialGradient(QPointF(bw / 2, PAD + SPRITE + 10), sh_w / 2)
        g.setColorAt(0, QColor(0, 0, 0, 110))
        g.setColorAt(1, QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(g)
        p.drawEllipse(QPointF(bw / 2, PAD + SPRITE + 10), sh_w / 2, 5)

        # aura in state colour (stronger when it needs Boss)
        rgb = STATE_RGB.get(st, STATE_RGB["idle"])
        aura_k = 0.18 + (0.25 if st == "hold" else 0) + 0.1 * math.sin(t * 2) + 0.2 * self.anim["pulse"]
        if doze:
            aura_k = 0.05
        a = QRadialGradient(QPointF(cx, cy), SPRITE * 0.75)
        a.setColorAt(0, QColor(*rgb, int(255 * max(0, aura_k) * 0.6)))
        a.setColorAt(1, QColor(*rgb, 0))
        p.setBrush(a)
        p.drawEllipse(QPointF(cx, cy), SPRITE * 0.75, SPRITE * 0.75)

        p.save()
        p.translate(cx, cy)
        tilt = max(-16.0, min(16.0, self.vel[0] * 1.1))   # leans into its motion
        if self.anim["dizzy"] > 0:
            tilt += math.sin(t * 18) * 14 * self.anim["dizzy"]
        p.rotate(tilt)
        scale = 1.08 if self.hover else 1.0
        p.scale(scale, scale)
        # it watches your cursor
        cur = self.mapFromGlobal(QCursor.pos())
        dx, dy = cur.x() - cx, cur.y() - cy
        dist = max(1.0, math.hypot(dx, dy))
        gx, gy = dx / dist * min(4.0, dist / 40), dy / dist * min(3.0, dist / 40)
        half = SPRITE / 2
        if doze:
            p.drawPixmap(QRectF(-half, -half, SPRITE, SPRITE), self.core_sleep,
                         QRectF(0, 0, self.core_sleep.width(), self.core_sleep.height()))
        else:
            dim, bright = self.core.get(st, self.core["idle"])
            speed = {"idle": 3.6, "thinking": 1.4, "spawning": .9, "hold": 1.1, "broken": .5,
                     "approved": 1.0}.get(st, 3.6)
            k = 0.55 + 0.45 * math.sin(t * 2 * math.pi / speed)
            if self.hover:
                k = max(k, .9)
            if st in ("idle", "thinking") and (t % 5.5) < 0.11:
                k = 0.0                              # blink
            if st == "broken" and random.random() < 0.08:
                k = 0.05
            src = QRectF(0, 0, dim.width(), dim.height())
            p.drawPixmap(QRectF(-half, -half, SPRITE, SPRITE), dim, src)
            p.setOpacity(k)
            p.drawPixmap(QRectF(-half + gx, -half + gy, SPRITE, SPRITE), bright, src)
            p.setOpacity(1)
        p.restore()

        if doze:                                     # z z z
            p.setPen(QColor(180, 195, 220, 150))
            p.setFont(ui_font(8.5, True))
            for i in range(3):
                ph = (t * 0.4 + i / 3) % 1
                p.setOpacity(1 - ph)
                p.drawText(QPointF(cx + 16 + ph * 14, cy - 20 - ph * 22), "z")
            p.setOpacity(1)
        if self.requests:                            # badge with count
            n = len(self.requests)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 176, 32))
            p.drawEllipse(QPointF(cx + SPRITE * 0.38, cy - SPRITE * 0.38), 8, 8)
            p.setPen(QColor(10, 10, 12))
            p.setFont(ui_font(8.5, True))
            p.drawText(QRectF(cx + SPRITE * 0.38 - 8, cy - SPRITE * 0.38 - 8, 16, 16), Qt.AlignCenter, str(n))
        p.end()

    # ---------------------------------------------------------------- input
    def enterEvent(self, _):
        self.hover = True
        self.last_activity = time.time()

    def leaveEvent(self, _):
        self.hover = False

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drag = (e.globalPosition().toPoint() - self.frameGeometry().topLeft(), False)
            self.target, self.vel, self.glide = None, [0.0, 0.0], None
            self.drag_trail = [(time.time(), e.globalPosition())]

    def mouseMoveEvent(self, e):
        if self.drag and e.buttons() & Qt.LeftButton:
            off, moved = self.drag
            new = e.globalPosition().toPoint() - off
            if moved or (new - self.pos()).manhattanLength() > 4:
                self.drag = (off, True)
                self.move(new)
                self.fpos = [float(new.x()), float(new.y())]
                self.drag_trail = (self.drag_trail + [(time.time(), e.globalPosition())])[-6:]
                if len(self.drag_trail) >= 2:              # lean while being carried
                    (t0, p0), (t1, p1) = self.drag_trail[-2], self.drag_trail[-1]
                    self.vel = [(p1.x() - p0.x()) / max(0.004, t1 - t0) * 0.016, 0.0]
                self._layout_bubbles()

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton or not self.drag:
            return
        moved = self.drag[1]
        self.drag = None
        if moved:                                      # fling: keep the throw's momentum
            now = time.time()
            recent = [(t, p) for t, p in self.drag_trail if now - t < 0.09] or self.drag_trail[-2:]
            if len(recent) >= 2:
                (t0, p0), (t1, p1) = recent[0], recent[-1]
                dt = max(0.008, t1 - t0)
                vx, vy = (p1.x() - p0.x()) / dt * 0.016, (p1.y() - p0.y()) / dt * 0.016
                sp = math.hypot(vx, vy)
                if sp > 45:
                    vx, vy = vx / sp * 45, vy / sp * 45
                self.vel = [vx, vy] if sp > 1.5 else [0.0, 0.0]
                if sp > 18:
                    self.sound.play("notify")
            self.next_roam = time.time() + 60          # you put it somewhere: it stays a while
            self._save()
            return
        now = time.time()
        self.clicks = [c for c in self.clicks if now - c < 0.9] + [now]
        if len(self.clicks) >= 3:
            self.clicks = []
            self.anim["dizzy"] = 1.0
            self.sound.play("dizzy")
            self.toast("info", "Easy, %s." % self.sal, "Mini Gaya is awake.")
            return
        if self.panel.isVisible():
            self.panel.hide()
            self.sound.play("close")
        else:
            self.target, self.vel, self.glide = None, [0.0, 0.0], None       # hold still while the deck is open
            self.panel.open()
            self.sound.play("open")
        self._layout_bubbles()

    def contextMenuEvent(self, e):
        self._menu().exec(e.globalPos())

    def _menu(self):
        m = QMenu()
        m.addAction("Talk to Mini Gaya…", lambda: self.open_chat())
        v_on = bool(self.voice and self.voice.enabled)
        m.addAction("Voice: on (say 'Hey Gaya' or hold Right Ctrl)" if v_on else "Voice: off", self.toggle_voice)
        if v_on:
            w_on = bool(getattr(self.voice, "wake_word_enabled", False))
            m.addAction("Wake word: 'Hey Gaya' (ON)" if w_on else "Wake word: 'Hey Gaya' (OFF)", self.toggle_wake)
            m.addAction("Unmute Mini Gaya" if self.voice.speaker.muted else "Mute Mini Gaya",
                        lambda: self.voice.mute(not self.voice.speaker.muted))
        m.addAction("Hide Mini Gaya" if not self.user_hidden else "Show Mini Gaya", self.toggle)
        m.addAction("Unmute sounds" if self.sound.muted else "Mute sounds", self._mute)
        m.addAction("Test notification", lambda: (self.sound.play("done"), self.toast(
            "approved", "Mini Gaya online", "notifications working, %s" % self.sal)))
        m.addAction("Bring me to the corner", self._home)
        m.addAction("Stop roaming" if self.roam else "Roam around", self._toggle_roam)
        m.addSeparator()
        m.addAction("Quit Mini Gaya", QApplication.quit)
        return m

    def _mute(self):
        self.sound.muted = not self.sound.muted
        self._save()

    def _start_voice(self, wake_word=True):
        """Kokoro + Whisper on background threads; J keeps working if they fail."""
        import logging
        try:
            sys.path.insert(0, os.path.join(HERE, "voice"))
            from voice.gaya_voice import VoiceEngine
            self.voice = VoiceEngine(self, wake_word_enabled=wake_word)
        except Exception:
            logging.exception("voice engine failed to start")
            self.voice = None

    def toggle_voice(self):
        if self.voice is None:
            self._start_voice()
        elif self.voice.enabled:
            self.voice.off()
        else:
            self.voice.on()
            self.voice.say("Voice on, %s." % self.sal)
        self._save()

    def toggle_wake(self):
        if self.voice:
            new_val = not getattr(self.voice, "wake_word_enabled", True)
            self.voice.set_wake_enabled(new_val)
            self.toast("info", "Wake Word 'Hey Gaya': %s" % ("Enabled" if new_val else "Disabled"), "")
            self._save()

    def speak(self, text, interrupt=False):
        if self.voice and self.voice.enabled:
            self.voice.say(text, interrupt=interrupt)

    def open_chat(self, sid=None):
        """The composer: tell J what to do in a session (or start one)."""
        self.target, self.vel, self.glide = None, [0.0, 0.0], None
        self.composer.open(sid)
        g = self.screen().availableGeometry()
        hx, hy = self.head_point()
        w = self.composer
        w.adjustSize()
        x = hx - w.width() - 20 if hx > g.center().x() else hx + 20
        y = min(max(g.top() + 8, hy - w.height() // 2), g.bottom() - w.height() - 8)
        w.move(max(g.left() + 8, min(x, g.right() - w.width() - 8)), y)
        self.sound.play("open")

    def show_daily_brief(self):
        """The morning card: what got done, what's left (tickable)."""
        from sprite_brief import TodayView, gather
        try:
            data = gather(self.sessions)
        except Exception as e:
            self.toast("broken", "Couldn't build today's brief", str(e)[:80])
            return
        b = Bubble(self, "#8fd3ff", 430)
        hour = time.localtime().tm_hour
        greet = "Good morning, %s" % self.sal if hour < 12 else "Good afternoon, %s" % self.sal if hour < 17 else "Evening, %s" % self.sal
        b.label(greet, "title")
        b.label("Here's %s - tick things off as you go." % ("yesterday" if data["label"] == "yesterday"
                                                             else "your day so far"), "muted")
        view = TodayView(on_jump=lambda sid: __import__("sprite_ui").focus_session({"sid": sid}))
        view.fill(data)
        b.body.addWidget(view)
        row = QHBoxLayout()
        deck = QPushButton("Open the Deck")
        deck.clicked.connect(lambda: (self._drop_brief(b), self.panel.open(), self.panel.show_tab(1)))
        ok = QPushButton("Got it", objectName="allow")
        ok.clicked.connect(lambda: self._drop_brief(b))
        for w in (deck, ok):
            w.setCursor(Qt.PointingHandCursor)
            row.addWidget(w)
        b.body.addLayout(row)
        self.daily = b
        self.toasts.append(b)
        self._layout_bubbles()
        b.show()
        self.sound.play("done")
        self.anim["hop"] = 1.0
        self.brief_day = time.strftime("%Y-%m-%d")
        self._save()
        n_wait = len([i for i in data["todo"] if i["id"].startswith("reply:")])
        self.speak("%s. %d things done %s, %d on the list%s." % (
            greet, len(data["done"]), data["label"], len(data["todo"]),
            (", %d sessions waiting for you" % n_wait) if n_wait else ""))

    def _drop_brief(self, b):
        if b in self.toasts:
            self.toasts.remove(b)
        b.hide()
        b.deleteLater()
        self._layout_bubbles()

    def _apply_size(self):
        scale = getattr(self, "scale_factor", 1.0)
        if self.body_on and self.body:
            self.vis_h = int(BODY_H * scale)
            self.base_w = self.body.width + 2 * PAD + 30
            self.base_h = BODY_H + 2 * PAD
            self.setFixedSize(max(40, int(self.base_w * scale)), max(40, int(self.base_h * scale)))
        else:
            self.vis_h = int(SPRITE * scale)
            self.base_w = SPRITE + 2 * PAD
            self.base_h = SPRITE + 2 * PAD
            self.setFixedSize(max(40, int(self.base_w * scale)), max(40, int(self.base_h * scale)))

    def toggle_body(self):
        if not self.body:
            self.toast("info", "No body art yet", "run prep_body.py on a character sheet")
            return
        self.body_on = not self.body_on
        self._apply_size()
        self._save()

    def _paint_listening(self, p, t):
        """Red pulsing dot + 'listening' while Right Ctrl is held."""
        if not getattr(self, "listening", False):
            return
        k = 0.6 + 0.4 * math.sin(t * 8)
        bw = getattr(self, "base_w", self.width())
        x, y = bw / 2, PAD - 6
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 70, 70, int(255 * k)))
        p.drawEllipse(QPointF(x - 34, y), 5, 5)
        p.setPen(QColor(255, 120, 120))
        p.setFont(ui_font(8, True))
        p.drawText(QRectF(x - 26, y - 9, 90, 18), Qt.AlignVCenter, "listening")

    def _toggle_roam(self):
        self.roam = not self.roam
        self.target = None
        self._save()

    def _home(self):
        g = self.screen().availableGeometry()
        self.move(g.right() - self.width() - 40, g.bottom() - self.height() - 60)
        self._save()
        self._layout_bubbles()

    # ---------------------------------------------------------------- tray / prefs
    def _tray(self):
        big = round(64 * self.dpr)
        self.tray = QSystemTrayIcon(QIcon(to_pixmap(compose_core(STATE_RGB["idle"], 1, .6, px=big), self.dpr)), self)
        self.tray.activated.connect(lambda r: self.toggle() if r == QSystemTrayIcon.Trigger else None)
        self.tray.setContextMenu(self._menu())
        self.tray.show()

    def _load(self):
        try:
            d = json.load(open(PREFS))
        except Exception:
            d = {}
        QTimer.singleShot(0, lambda: setattr(self.sound, "muted", d.get("muted", False)))
        return d

    def _save(self):
        try:
            json.dump({"x": self.x(), "y": self.y(), "muted": self.sound.muted,
                       "roam": getattr(self, "roam", True), "body": getattr(self, "body_on", True),
                       "scale": getattr(self, "scale_factor", 1.0),
                       "voice": bool(getattr(self, "voice", None) and self.voice.enabled),
                       "wake_word": bool(getattr(self, "voice", None) and getattr(self.voice, "wake_word_enabled", True)),
                       "brief_day": getattr(self, "brief_day", "")}, open(PREFS, "w"))
        except Exception:
            pass


def start_log():
    """pythonw has no console - every exception goes to ~/.jarvis/logs/sprite.log."""
    import logging
    import traceback
    path = os.path.join(JDIR, "logs", "sprite.log")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    logging.basicConfig(filename=path, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Mini Gaya sprite starting pid=%s argv=%s", os.getpid(), sys.argv[1:])

    def hook(t, v, tb):
        logging.error("uncaught: %s", "".join(traceback.format_exception(t, v, tb)))
    sys.excepthook = hook


def scrub_env():
    """If J was launched from inside VS Code (a Claude Code terminal), the
    environment carries ELECTRON_RUN_AS_NODE=1. Any vscode:// link we open
    then starts Code.exe as plain Node, which dies silently - that was the
    'Jump in glitches out' bug. Children must not inherit it."""
    for k in list(os.environ):
        if k == "ELECTRON_RUN_AS_NODE" or k.startswith("VSCODE_") or k.startswith("CLAUDE_CODE_"):
            os.environ.pop(k, None)


def main():
    scrub_env()
    start_log()
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    s = Sprite()
    s.show()
    s.anim["hop"] = 1.0
    today = time.strftime("%Y-%m-%d")
    if "--boot" in sys.argv or s.brief_day != today:
        QTimer.singleShot(2500, s.show_daily_brief)      # once a day: done + to-do checklist
    else:
        s.toast("approved", "Mini Gaya online", "click me for the Deck · throw me around")
    QTimer.singleShot(1200, lambda: s.speak("Mini Gaya is online, %s." % s.sal))
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
