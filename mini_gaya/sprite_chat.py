"""Talk to mini J: a composer that sends your message into a Claude Code
session - the one that's open ("all docs 2"), a closed one, or a new one.

Routes (best available first):
  1. cc_peer.send(...)  - Claude Code's own session-to-session pipe, when
     sprite/cc_peer.py exists and the target is live. Arrives as a message
     from "GAYA sprite" inside that chat.
  2. New / closed session: vscode://anthropic.claude-code/open?session=..&prompt=..
     pre-fills the chat input (the extension only pre-fills, it never sends),
     then J presses Enter for you - or not, if you chose Draft.
  3. Open session, no pipe: J reveals the session, puts your text on the
     clipboard, pastes it into the focused chat input and presses Enter.
     It checks VS Code really is in front first; if not, the text stays on
     your clipboard and J tells you.
"""
import ctypes
import os
import time
import urllib.parse
from ctypes import wintypes

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel, QPlainTextEdit,
                               QPushButton, QVBoxLayout, QWidget)

from gaya_island import live_sessions
from sprite_ui import _focus_window, esc, ui_font

VK_RETURN, VK_CONTROL, VK_V = 0x0D, 0x11, 0x56
KEYUP = 0x0002

CSS = """
QWidget#card { background: rgba(8,8,10,248); border: 1px solid rgba(143,211,255,120); border-radius: 14px; }
QLabel { color: #e9ecf1; font-family: 'Space Grotesk'; font-size: 9pt; background: transparent; }
QLabel#title { font-family: 'Space Grotesk'; font-weight: 600; font-size: 11pt; }
QLabel#muted { color: #8c9098; font-size: 8.5pt; }
QComboBox { color: #e9ecf1; background: rgba(255,255,255,12); border: 1px solid rgba(255,255,255,26);
            border-radius: 9px; padding: 5px 10px; font-family: 'Space Grotesk'; font-size: 9pt; }
QComboBox QAbstractItemView { background: #121316; color: #e9ecf1; selection-background-color: rgba(143,211,255,60);
            border: 1px solid rgba(255,255,255,30); outline: none; }
QPlainTextEdit { color: #e9ecf1; background: rgba(255,255,255,8); border: 1px solid rgba(255,255,255,22);
            border-radius: 10px; padding: 8px; font-family: 'Space Grotesk'; font-size: 10pt; }
QPlainTextEdit:focus { border-color: rgba(143,211,255,160); }
QPushButton { color: #e9ecf1; background: rgba(255,255,255,12); border: 1px solid rgba(255,255,255,22);
              border-radius: 9px; padding: 6px 14px; font-family: 'Space Grotesk'; font-weight: 600; font-size: 9pt; }
QPushButton:hover { background: rgba(255,255,255,30); }
QPushButton#send { background: rgba(143,211,255,45); border-color: rgba(143,211,255,160); }
QPushButton#send:hover { background: rgba(143,211,255,90); }
"""


# ------------------------------------------------------------------ Windows input helpers
def foreground_title():
    u = ctypes.windll.user32
    h = u.GetForegroundWindow()
    n = u.GetWindowTextLengthW(h)
    buf = ctypes.create_unicode_buffer(n + 1)
    u.GetWindowTextW(h, buf, n + 1)
    return buf.value


def vscode_in_front():
    return foreground_title().endswith("Visual Studio Code")


def set_clipboard_text(text):
    """Write the clipboard directly (CF_UNICODETEXT). Qt's clipboard renders
    lazily and VS Code's paste request can arrive while we're mid-flow."""
    k, u = ctypes.windll.kernel32, ctypes.windll.user32
    k.GlobalAlloc.restype = ctypes.c_void_p
    k.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    k.GlobalLock.restype = ctypes.c_void_p
    k.GlobalLock.argtypes = [ctypes.c_void_p]
    k.GlobalUnlock.argtypes = [ctypes.c_void_p]
    u.SetClipboardData.restype = ctypes.c_void_p
    u.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    data = text.encode("utf-16-le") + b"\x00\x00"
    for _ in range(10):                                   # the clipboard can be briefly locked
        if u.OpenClipboard(None):
            break
        time.sleep(0.05)
    else:
        return False
    try:
        u.EmptyClipboard()
        h = k.GlobalAlloc(0x0042, len(data))            # GMEM_MOVEABLE | GMEM_ZEROINIT
        p = k.GlobalLock(h)
        ctypes.memmove(p, data, len(data))
        k.GlobalUnlock(h)
        u.SetClipboardData(13, h)                        # CF_UNICODETEXT; system owns h now
        return True
    finally:
        u.CloseClipboard()


def press(*vks, ctrl=False):
    u = ctypes.windll.user32
    if ctrl:
        u.keybd_event(VK_CONTROL, 0, 0, 0)
    for vk in vks:
        u.keybd_event(vk, 0, 0, 0)
        u.keybd_event(vk, 0, KEYUP, 0)
    if ctrl:
        u.keybd_event(VK_CONTROL, 0, KEYUP, 0)


# ------------------------------------------------------------------ delivery
def deliver(sprite, sid, text, submit=True, title="", route="auto"):
    """Get `text` into session `sid` (None = new session). Never blocks the UI.

    route: "auto"  = Claude Code's own session pipe when the target is open
                     (arrives as a message from "GAYA sprite"); else the UI route
           "type"  = always the UI route: it's typed into the chat as you
           "draft" = UI route, no Enter
    """
    text = text.strip()
    if not text:
        return
    live = live_sessions()
    name = title or (live.get(sid, {}).get("name") if sid else "") or "a new session"
    if route == "draft":
        submit = False

    # 1. the real pipe - on a thread, the receiver holds the pipe open until we time out
    if route == "auto" and sid and sid in live:
        import threading
        box = {}

        def work():
            try:
                import cc_peer
                box["res"] = cc_peer.send(sid, text, timeout=1.2)
            except Exception as e:
                box["err"] = "%s: %s" % (type(e).__name__, str(e)[:120])

        threading.Thread(target=work, daemon=True).start()

        def poll(n=0):
            if "res" in box:
                sprite.sound.play("send")
                sprite.toast("approved", "Sent to %s" % name[:40], text[:90])
            elif "err" in box or n > 40:
                import logging
                logging.warning("pipe send failed (%s) - falling back to typing", box.get("err", "timeout"))
                deliver(sprite, sid, text, submit=submit, title=title, route="type")
            else:
                QTimer.singleShot(100, lambda: poll(n + 1))
        poll()
        return

    def after_reveal(step):
        if step > 10:                                  # ~3 s and VS Code never came up
            set_clipboard_text(text)
            sprite.toast("hold", "Couldn't reach VS Code", "your message is on the clipboard - paste it in")
            return
        if not vscode_in_front():
            if step == 2:
                _focus_window({"cwd": "", "entry": "claude-vscode"})
            QTimer.singleShot(300, lambda: after_reveal(step + 1))
            return
        QTimer.singleShot(350, finish)

    def finish():
        if sid and sid in live:                        # open session: paste into its input
            set_clipboard_text(text)
            press(VK_V, ctrl=True)
        if submit:
            QTimer.singleShot(250, lambda: press(VK_RETURN))
        sprite.sound.play("send")
        sprite.toast("approved" if submit else "info",
                     ("Sent to %s" if submit else "Drafted in %s - press Enter there") % name[:40], text[:90])

    if sid and sid in live:
        url = "vscode://anthropic.claude-code/open?session=" + sid
    else:
        q = "prompt=" + urllib.parse.quote(text, safe="")
        url = "vscode://anthropic.claude-code/open?" + (("session=%s&" % sid) if sid else "") + q
    try:
        os.startfile(url)
    except OSError as e:
        set_clipboard_text(text)
        sprite.toast("broken", "Couldn't open VS Code", str(e)[:80])
        return
    QTimer.singleShot(500, lambda: after_reveal(0))


# ------------------------------------------------------------------ the composer window
class Composer(QWidget):
    """The one GAYA window that DOES take focus - you type in it."""

    def __init__(self, sprite):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
                         | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.sprite = sprite
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.card = QWidget(objectName="card")
        self.card.setStyleSheet(CSS)
        self.card.setFixedWidth(460)
        outer.addWidget(self.card)
        lay = QVBoxLayout(self.card)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)
        top = QHBoxLayout()
        top.addWidget(QLabel("Tell J what to do", objectName="title"))
        top.addStretch(1)
        x = QPushButton("✕")
        x.setFont(ui_font(9, family="Segoe UI Symbol"))
        x.setFixedWidth(30)
        x.clicked.connect(self.hide)
        top.addWidget(x)
        lay.addLayout(top)
        self.target = QComboBox()
        self.target.setCursor(Qt.PointingHandCursor)
        lay.addWidget(self.target)
        self.box = QPlainTextEdit()
        self.box.setPlaceholderText("e.g. update the last two mockups and print them   (Ctrl+Enter to send)")
        self.box.setFixedHeight(96)
        lay.addWidget(self.box)
        row = QHBoxLayout()
        self.hint = QLabel("", objectName="muted")
        row.addWidget(self.hint, 1)
        draft = QPushButton("Draft")
        draft.setToolTip("Put it in the chat input but don't send")
        draft.clicked.connect(lambda: self._go("draft"))
        typed = QPushButton("Type as me")
        typed.setToolTip("Reveal the chat and type it in as you, then Enter")
        typed.clicked.connect(lambda: self._go("type"))
        send = QPushButton("Send", objectName="send")
        send.setToolTip("Open chat: delivered into Antigravity session as a message from Gaya\n"
                        "New / closed: opened with this as the first message")
        send.clicked.connect(lambda: self._go("auto"))
        for b in (draft, typed, send):
            b.setCursor(Qt.PointingHandCursor)
            row.addWidget(b)
        lay.addLayout(row)
        QShortcut(QKeySequence("Ctrl+Return"), self, activated=lambda: self._go("auto"))
        QShortcut(QKeySequence("Escape"), self, activated=self.hide)
        self.target.currentIndexChanged.connect(self._hint)

    def open(self, preselect_sid=None):
        self.target.clear()
        self.target.addItem("＋  New session", None)
        live = live_sessions()
        seen = set()
        for r in self.sprite.sessions:
            sid = r.get("sid")
            if not sid or sid in seen:
                continue
            seen.add(sid)
            tag = {"working": "working", "waiting": "waiting for you", "idle": "open",
                   "closed": "closed"}.get(r["status"], r["status"])
            self.target.addItem("%s   ·  %s" % (r["title"][:38], tag), sid)
        for sid, d in live.items():                       # live but not in the recent list
            if sid not in seen:
                self.target.addItem("%s   ·  %s" % (d.get("name", sid[:8]), d.get("status", "")), sid)
        if preselect_sid:
            i = self.target.findData(preselect_sid)
            if i >= 0:
                self.target.setCurrentIndex(i)
        self._hint()
        self.show()
        self.raise_()
        self.activateWindow()
        # Windows only hands the foreground to the process that owns it; the
        # click came from a no-focus window, so take it the official way.
        u = ctypes.windll.user32
        u.keybd_event(0x12, 0, 0, 0)
        u.keybd_event(0x12, 0, KEYUP, 0)
        u.SetForegroundWindow(int(self.winId()))
        self.box.setFocus(Qt.ActiveWindowFocusReason)
        QTimer.singleShot(120, lambda: (self.activateWindow(), self.box.setFocus()))

    def _hint(self):
        sid = self.target.currentData()
        live = live_sessions()
        if sid is None:
            self.hint.setText("Send = new chat with this")
        elif sid in live:
            self.hint.setText("Send = via session pipe · Type = as you")
        else:
            self.hint.setText("Send = reopen with this")

    def _go(self, route):
        text = self.box.toPlainText().strip()
        if not text:
            return
        sid = self.target.currentData()
        title = self.target.currentText().split("   ·")[0].strip() if sid else ""
        self.hide()
        self.box.clear()
        deliver(self.sprite, sid, text, submit=(route != "draft"), title=title, route=route)
