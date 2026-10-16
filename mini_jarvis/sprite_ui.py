"""Interactive pieces of the JARVIS sprite: the radial command ring, the
session panel you can act on, and jumping to a session's window."""
import ctypes
import math
import os
import time
from ctypes import wintypes

from PySide6.QtCore import QEasingCurve, QPointF, QRectF, Qt, QTimer, QVariantAnimation
from PySide6.QtGui import QColor, QCursor, QFont, QFontMetrics, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
                               QWidget)

NOFOCUS = (Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
           | Qt.WindowDoesNotAcceptFocus | Qt.NoDropShadowWindowHint)
STATUS_COL = {"working": "#57c7ff", "waiting": "#ffb020", "idle": "#6a6e76", "closed": "#4a4c52"}


def ui_font(size, bold=False, family="Space Grotesk"):
    """Our windows are translucent, so Windows can't use ClearType on them and
    text falls back to grayscale smoothing - at small sizes that looks
    pixelated. Full hinting snaps stems to whole pixels and fixes most of it."""
    f = QFont(family, size, QFont.DemiBold if bold else QFont.Normal)
    f.setHintingPreference(QFont.PreferFullHinting)
    f.setStyleStrategy(QFont.PreferAntialias)
    return f


def load_fonts():
    """Space Grotesk (UI) + Space Mono (commands), bundled in sprite/fonts (OFL)."""
    from PySide6.QtGui import QFontDatabase
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    for f in ("SpaceGrotesk.ttf", "SpaceMono-Regular.ttf"):
        p = os.path.join(d, f)
        if os.path.exists(p):
            QFontDatabase.addApplicationFont(p)
    QApplication.setFont(ui_font(9.5))


def esc(t):
    return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------------ jump to a session
def _windows():
    u = ctypes.windll.user32
    out = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, _):
        if u.IsWindowVisible(hwnd):
            n = u.GetWindowTextLengthW(hwnd)
            if n:
                buf = ctypes.create_unicode_buffer(n + 1)
                u.GetWindowTextW(hwnd, buf, n + 1)
                out.append((hwnd, buf.value))
        return True

    u.EnumWindows(cb, 0)
    return out


def focus_session(r):
    """Open THIS session. The Claude Code VS Code extension registers
    vscode://anthropic.claude-code/open?session=<uuid> (extension.js handleUri
    "/open" -> claude-vscode.primaryEditor.open), which opens/focuses that exact
    conversation. Falls back to bringing a VS Code / terminal window forward."""
    import re
    from PySide6.QtCore import QTimer
    sid = str(r.get("sid", ""))
    if re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", sid):
        try:
            os.startfile("vscode://anthropic.claude-code/open?session=" + sid)
            # Windows won't let a background process raise VS Code - it just
            # flashes in the taskbar. Pull it forward ourselves once the link landed.
            QTimer.singleShot(650, lambda: _focus_window(r))
            return True
        except OSError:
            pass
    return _focus_window(r)


def _focus_window(r):
    folder = (r.get("cwd") or "").lower()
    wins = _windows()
    vs = [(h, t) for h, t in wins if t.endswith("Visual Studio Code") or "antigravity" in t.lower()]
    pick = None
    if r.get("entry", "").startswith("antigravity") or r.get("entry", "").startswith("claude-vscode") or vs:
        pick = next((h for h, t in vs if folder and folder in t.lower()), None) or (vs[0][0] if vs else None)
    if pick is None:
        pick = next((h for h, t in wins if ("antigravity" in t.lower() or "claude" in t.lower()) and "gaya" not in t.lower() and "jarvis" not in t.lower()), None)
    if pick is None:
        return False
    u = ctypes.windll.user32
    if u.IsIconic(pick):
        u.ShowWindow(pick, 9)                     # SW_RESTORE
    u.keybd_event(0x12, 0, 0, 0)                  # tap Alt so Windows lets us take the foreground
    u.keybd_event(0x12, 0, 2, 0)
    u.SetForegroundWindow(pick)
    return True


# ------------------------------------------------------------------ radial command ring
class RadialMenu(QWidget):
    """Opens around the sprite: buttons fan out on a ring. Hover lights a
    button, click runs it, moving away closes it."""
    SIZE = 300
    R = 98
    BTN = 25

    def __init__(self, sprite):
        super().__init__(None, NOFOCUS)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setMouseTracking(True)
        self.setFixedSize(self.SIZE, self.SIZE)
        self.sprite = sprite
        self.items = []
        self.hot = -1
        self.p = 0.0
        self.anim = QVariantAnimation(self, startValue=0.0, endValue=1.0, duration=230,
                                      easingCurve=QEasingCurve.OutBack)
        self.anim.valueChanged.connect(self._on_anim)
        self.away = QTimer(self, singleShot=True, interval=1400, timeout=self.close_ring)
        QTimer(self, timeout=self._watch, interval=120).start()

    def _on_anim(self, v):
        self.p = float(v)
        self.update()

    def open_at(self, center, items):
        """items: list of (glyph, label, colour, callback, badge)"""
        self.items = items
        self.hot = -1
        self.move(int(center.x() - self.SIZE / 2), int(center.y() - self.SIZE / 2))
        self.show()
        self.anim.setDirection(QVariantAnimation.Forward)
        self.anim.start()

    def close_ring(self):
        if self.isVisible():
            self.hide()

    def _pos(self, i):
        n = len(self.items)
        a = -math.pi / 2 + i * 2 * math.pi / n
        r = self.R * self.p
        c = self.SIZE / 2
        return QPointF(c + math.cos(a) * r, c + math.sin(a) * r)

    def _hit(self, pt):
        for i in range(len(self.items)):
            if (self._pos(i) - pt).manhattanLength() < self.BTN * 1.4:
                return i
        return -1

    def _watch(self):
        if not self.isVisible():
            return
        inside = self.geometry().contains(QCursor.pos())
        if inside:
            self.away.stop()
        elif not self.away.isActive():
            self.away.start()

    def mouseMoveEvent(self, e):
        h = self._hit(e.position())
        if h != self.hot:
            self.hot = h
            self.setCursor(Qt.PointingHandCursor if h >= 0 else Qt.ArrowCursor)
            self.update()

    def mouseReleaseEvent(self, e):
        h = self._hit(e.position())
        self.close_ring()
        if h >= 0:
            self.items[h][3]()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        c = QPointF(self.SIZE / 2, self.SIZE / 2)
        # faint disc so the whole ring catches the mouse; soft halo
        g = QRadialGradient(c, self.R + 40)
        g.setColorAt(0, QColor(8, 9, 12, int(150 * self.p)))
        g.setColorAt(0.75, QColor(8, 9, 12, int(110 * self.p)))
        g.setColorAt(1, QColor(8, 9, 12, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(g)
        p.drawEllipse(c, self.R + 40, self.R + 40)
        p.setPen(QPen(QColor(255, 255, 255, int(28 * self.p)), 1))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(c, self.R * self.p, self.R * self.p)
        for i, (glyph, label, colour, _cb, badge) in enumerate(self.items):
            pt = self._pos(i)
            hot = i == self.hot
            r = self.BTN * (1.12 if hot else 1.0) * min(1.0, self.p + 0.2)
            col = QColor(colour)
            p.setPen(QPen(col if hot else QColor(255, 255, 255, 50), 1.5))
            p.setBrush(QColor(col.red(), col.green(), col.blue(), 70 if hot else 26))
            p.drawEllipse(pt, r, r)
            p.setPen(QColor(colour) if hot else QColor(232, 236, 242))
            p.setFont(QFont("Segoe UI Emoji", 12))
            p.drawText(QRectF(pt.x() - r, pt.y() - r - 2, 2 * r, 2 * r), Qt.AlignCenter, glyph)
            p.setFont(ui_font(8.5, True))
            p.setPen(QColor(232, 236, 242, int(255 * self.p)))
            p.drawText(QRectF(pt.x() - 50, pt.y() + r + 1, 100, 14), Qt.AlignHCenter, label)
            if badge:
                bp = QPointF(pt.x() + r * 0.72, pt.y() - r * 0.72)
                p.setPen(Qt.NoPen)
                p.setBrush(QColor("#ffb020"))
                p.drawEllipse(bp, 8, 8)
                p.setPen(QColor(10, 10, 12))
                p.setFont(ui_font(8.5, True))
                p.drawText(QRectF(bp.x() - 8, bp.y() - 8, 16, 16), Qt.AlignCenter, str(badge))
        p.end()


# ------------------------------------------------------------------ session panel
class SessionRow(QWidget):
    """One session. Hover = highlight + expand with the full last reply and
    actions. Click = jump to that session's window."""

    def __init__(self, panel, r):
        super().__init__()
        self.panel, self.r = panel, r
        self.setAttribute(Qt.WA_Hover)
        self.setCursor(Qt.PointingHandCursor)
        self.hot = False
        col = STATUS_COL[r["status"]]
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 7, 10, 7)
        lay.setSpacing(3)
        what = {"working": "working" + (" · " + r["tool"] if r["tool"] else ""),
                "waiting": "waiting for you · " + _ago(r["idle_s"]),
                "idle": "open · idle " + _ago(r["idle_s"]),
                "closed": "closed · " + _ago(r["idle_s"])}[r["status"]]
        fm = QFontMetrics(ui_font(9.5, True))
        head = QLabel('<span style="color:%s">●</span>&nbsp; <b>%s</b>&nbsp;&nbsp;'
                      '<span style="color:%s;font-size:7.5pt">%s</span>'
                      % (col, esc(fm.elidedText(r["title"], Qt.ElideRight, 210)), col, esc(what)))
        head.setTextFormat(Qt.RichText)
        lay.addWidget(head)
        sub = r["reply"] if r["status"] == "waiting" and r["reply"] else (
            "> " + r["prompt"] if r["prompt"] else r["cwd"])
        fm2 = QFontMetrics(ui_font(8.5))
        self.short = QLabel(fm2.elidedText(sub, Qt.ElideRight, 330))
        self.short.setTextFormat(Qt.PlainText)
        self.short.setObjectName("muted")
        lay.addWidget(self.short)
        # expanded part
        self.more = QWidget()
        ml = QVBoxLayout(self.more)
        ml.setContentsMargins(0, 4, 0, 0)
        ml.setSpacing(5)
        if r.get("prompt_full"):
            pl = QLabel("you:  " + r["prompt_full"][:240])
            pl.setWordWrap(True)
            pl.setObjectName("muted")
            ml.addWidget(pl)
        if r.get("reply_full"):
            rl = QLabel("jarvis:  " + r["reply_full"][:420] + ("…" if len(r["reply_full"]) > 420 else ""))
            rl.setWordWrap(True)
            rl.setTextFormat(Qt.PlainText)
            ml.addWidget(rl)
        btns = QHBoxLayout()
        for text, fn in (("Jump to it", lambda: panel.jump(r)),
                         ("Tell it…", lambda: panel.sprite.open_chat(r.get("sid"))),
                         ("Open folder", lambda: _open_folder(r)),
                         ("Copy reply", lambda: QApplication.clipboard().setText(r.get("reply_full", "")))):
            b = QPushButton(text)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(fn)
            btns.addWidget(b)
        ml.addLayout(btns)
        self.more.setVisible(False)
        lay.addWidget(self.more)

    def enterEvent(self, _):
        self.hot = True
        self.more.setVisible(True)
        self.short.setVisible(False)
        self.update()
        self.panel.relayout()

    def leaveEvent(self, _):
        self.hot = False
        self.more.setVisible(False)
        self.short.setVisible(True)
        self.update()
        self.panel.relayout()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.panel.jump(self.r)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        col = QColor(STATUS_COL[self.r["status"]])
        if self.hot:
            p.setPen(QPen(QColor(col.red(), col.green(), col.blue(), 140), 1))
            p.setBrush(QColor(255, 255, 255, 14))
        else:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 6))
        p.drawRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 9, 9)
        if self.r["status"] == "waiting":           # amber edge pulse = needs you
            k = 0.5 + 0.5 * math.sin(time.time() * 4)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 176, 32, int(90 + 120 * k)))
            p.drawRoundedRect(QRectF(0, 6, 3, self.height() - 12), 1.5, 1.5)
        p.end()


def _ago(s):
    s = int(s)
    return "now" if s < 25 else "%ds" % s if s < 60 else "%dm" % (s // 60) if s < 3600 else "%dh" % (s // 3600)


def _open_folder(r):
    path = r.get("cwd_full")
    if path and os.path.isdir(path):
        os.startfile(path)


class SessionPanel(QWidget):
    def __init__(self, sprite, css):
        super().__init__(None, NOFOCUS)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.sprite = sprite
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.card = QWidget(objectName="card")
        self.card.setStyleSheet(css % "rgba(143,211,255,90)")
        self.card.setFixedWidth(390)
        outer.addWidget(self.card)
        self.body = QVBoxLayout(self.card)
        self.body.setContentsMargins(12, 10, 12, 12)
        self.body.setSpacing(6)
        top = QHBoxLayout()
        self.head = QLabel("Sessions", objectName="title")
        top.addWidget(self.head)
        top.addStretch(1)
        x = QPushButton("✕")
        x.setFixedWidth(30)
        x.setCursor(Qt.PointingHandCursor)
        x.clicked.connect(self.hide)
        top.addWidget(x)
        self.body.addLayout(top)
        self.status = QLabel("", objectName="muted")
        self.body.addWidget(self.status)
        self.rows = QVBoxLayout()
        self.rows.setSpacing(6)
        self.body.addLayout(self.rows)
        self.fade = QVariantAnimation(self, startValue=0.0, endValue=1.0, duration=180)
        self.fade.valueChanged.connect(lambda v: self.setWindowOpacity(float(v)))
        self.sig = None

    def refresh(self, force=False):
        s = self.sprite
        sig = tuple((r["id"], r["status"], r["tool"], int(r["idle_s"] // 60)) for r in s.sessions[:6])
        self.status.setText("%s  ·  guard %s  ·  %d holds today  ·  click a session to jump to it"
                            % (s.state.upper(), s.armed, s.holds))
        if sig == self.sig and not force:
            return
        if any(isinstance(w, SessionRow) and w.hot for w in self.card.findChildren(SessionRow)):
            return                                 # don't rebuild under the mouse
        self.sig = sig
        while self.rows.count():
            w = self.rows.takeAt(0).widget()
            if w:
                w.deleteLater()
        if not s.sessions:
            l = QLabel("No Antigravity sessions in the last 3 hours.", objectName="muted")
            self.rows.addWidget(l)
        for r in s.sessions[:6]:
            self.rows.addWidget(SessionRow(self, r))
        self.relayout()

    def relayout(self):
        self.adjustSize()
        self.sprite._layout_bubbles()

    def open(self):
        self.refresh(force=True)
        self.setWindowOpacity(0.0)
        self.show()
        self.relayout()
        self.fade.start()

    def jump(self, r):
        ok = focus_session(r)
        self.sprite.toast("info", "Jumping to %s" % r["title"][:40] if ok else "Couldn't find that window",
                          r.get("cwd_full", "") if ok else "it may be in a closed editor")
