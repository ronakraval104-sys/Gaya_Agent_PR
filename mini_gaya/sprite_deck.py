"""GAYA Deck - the panel that opens when you click the sprite.

  Top bar : Home · Sessions · Agents tabs, settings, sound, close
  Home    : big live Command Core + status + quick actions | agent grid
  Sessions: hover-to-expand rows -> Jump / Folder / Copy
  Agents  : latest reports from EDIDTH / VERONICA / FRIDAY / DUM-E, click to open
"""
import glob
import json
import math
import os
import sys
import time

from PySide6.QtCore import QRectF, Qt, QTimer, QUrl, QVariantAnimation
from PySide6.QtGui import QColor, QDesktopServices, QFont, QPainter, QPen
from PySide6.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy,
                               QStackedWidget, QVBoxLayout, QWidget)

from gaya_island import STATE_RGB, compose_core, to_pixmap
from sprite_brief import TodayView, gather
from sprite_ui import NOFOCUS, SessionRow, _ago, esc, focus_session, ui_font

JDIR = os.path.join(os.path.expanduser("~"), ".jarvis")
KB = os.path.join(JDIR, "kb")
AGENTS = [("logos", "🛡️ LOGOS", (255, 215, 60), "Mind & QC Gate"),
          ("bob", "🔨 Bob", (255, 140, 25), "Hands & Builder"),
          ("freya", "✨ Freya", (255, 120, 180), "Heart & Designer"),
          ("tvashtar", "⚙️ Tvashtar", (155, 140, 255), "Tools & Craftsman")]
STARTUP = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup",
                       "Mini Gaya.bat")

CSS = """
QWidget#deck { background: rgba(8,8,10,246); border: 1px solid rgba(255,255,255,26); border-radius: 18px; }
QWidget#tile { background: rgba(255,255,255,9); border: 1px solid rgba(255,255,255,14); border-radius: 14px; }
QLabel { color: #e9ecf1; font-family: 'Space Grotesk'; font-size: 9pt; background: transparent; }
QLabel#title { font-family: 'Space Grotesk'; font-weight: 600; font-size: 12pt; }
QLabel#muted { color: #8c9098; font-size: 8.5pt; }
QPushButton { color: #e9ecf1; background: rgba(255,255,255,14); border: 1px solid rgba(255,255,255,26);
              border-radius: 10px; padding: 6px 10px; font-family: 'Space Grotesk', 'Segoe UI', sans-serif; font-weight: 600; font-size: 9.5pt; text-align: center; }
QPushButton:hover { background: rgba(255,255,255,34); border-color: rgba(255,255,255,45); }
QPushButton#tab { border: none; background: transparent; border-radius: 12px; padding: 5px 10px;
                  font-size: 10pt; color: #9aa0aa; }
QPushButton#tab:hover { background: rgba(255,255,255,14); color: #e9ecf1; }
QPushButton#tab:checked { background: rgba(255,255,255,26); color: #ffffff; }
QPushButton#icon { border: none; background: transparent; font-size: 11pt; padding: 3px 7px; color: #9aa0aa; }
QPushButton#icon:hover { color: #ffffff; background: rgba(255,255,255,14); }
QPushButton:checked { background: rgba(143,211,255,50); border-color: #8fd3ff; }
"""


class CoreView(QWidget):
    """Big live Command Core - breathes in GAYA's state colour."""

    def __init__(self, sprite, size=104):
        super().__init__()
        self.sprite, self.sz = sprite, size
        self.setFixedSize(size + 16, size + 16)
        px = round(size * sprite.dpr)
        self.pm = {s: (to_pixmap(compose_core(rgb, .5, .25, px=px), sprite.dpr),
                       to_pixmap(compose_core(rgb, 1, .85, px=px), sprite.dpr)) for s, rgb in STATE_RGB.items()}
        QTimer(self, timeout=self.update, interval=33).start()

    def paintEvent(self, _):
        t = time.time()
        st = "hold" if self.sprite.requests else self.sprite.state
        dim, bright = self.pm.get(st, self.pm["idle"])
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        y = 8 + math.sin(t * 1.1) * 3
        r = QRectF(8, y, self.sz, self.sz)
        src = QRectF(0, 0, dim.width(), dim.height())
        p.drawPixmap(r, dim, src)
        p.setOpacity(0.55 + 0.45 * math.sin(t * 2 * math.pi / 3.2))
        p.drawPixmap(r, bright, src)
        p.end()


class AgentPill(QWidget):
    """Coloured mini core + name + latest activity. Click = open its last report."""

    def __init__(self, deck, key, name, rgb, role):
        super().__init__()
        self.deck, self.key, self.name, self.rgb, self.role = deck, key, name, rgb, role
        self.setFixedHeight(46)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover)
        self.hot = False
        px = round(26 * deck.sprite.dpr)
        self.face = to_pixmap(compose_core(rgb, 1.0, .7, px=px), deck.sprite.dpr)
        self.info = ("", "", None)

    def set_info(self, line, sub, path):
        self.info = (line, sub, path)
        self.update()

    def enterEvent(self, _):
        self.hot = True
        self.update()

    def leaveEvent(self, _):
        self.hot = False
        self.update()

    def mouseReleaseEvent(self, e):
        path = self.info[2]
        if path and os.path.exists(path):
            os.startfile(path)
        else:
            self.deck.sprite.toast("info", "%s has no report yet" % self.name, "they report into the KB when they run")

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
        c = QColor(*self.rgb)
        p.setPen(QPen(QColor(c.red(), c.green(), c.blue(), 160 if self.hot else 60), 1))
        p.setBrush(QColor(c.red(), c.green(), c.blue(), 34 if self.hot else 16))
        p.drawRoundedRect(QRectF(self.rect()).adjusted(.5, .5, -.5, -.5), 14, 14)
        bob = math.sin(time.time() * 2 + hash(self.key) % 7) * (1.5 if self.hot else 0.6)
        p.drawPixmap(QRectF(10, 10 + bob, 26, 26), self.face, QRectF(0, 0, self.face.width(), self.face.height()))
        p.setPen(QColor(236, 238, 242))
        p.setFont(ui_font(9.5, True))
        p.drawText(QRectF(44, 5, self.width() - 50, 18), Qt.AlignVCenter, self.name)
        p.setFont(ui_font(8.5))
        p.setPen(c if self.info[0] else QColor(140, 144, 152))
        p.drawText(QRectF(44, 23, self.width() - 50, 16), Qt.AlignVCenter, self.info[0] or self.role)
        p.end()


class Deck(QWidget):
    def __init__(self, sprite):
        super().__init__(None, NOFOCUS)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.sprite = sprite
        self.sig = None
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.card = QWidget(objectName="deck")
        self.card.setStyleSheet(CSS)
        self.card.setFixedWidth(700)
        outer.addWidget(self.card)
        root = QVBoxLayout(self.card)
        root.setContentsMargins(12, 10, 12, 12)
        root.setSpacing(10)

        # ---- top bar
        bar = QHBoxLayout()
        self.tabs = []
        for i, (glyph, tip) in enumerate((("⌂  Home", "Home"), ("☀  Today", "Done + to-do"), ("⚡  Sessions", "Sessions"), ("◆  Agents", "Agents"))):
            b = QPushButton(glyph, objectName="tab")
            b.setCheckable(True)
            b.setToolTip(tip)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, i=i: self.show_tab(i))
            bar.addWidget(b)
            self.tabs.append(b)
        bar.addStretch(1)
        chat = QPushButton("💬", objectName="icon")
        chat.setToolTip("Talk to J - send a message into a session")
        chat.setCursor(Qt.PointingHandCursor)
        chat.clicked.connect(lambda: self.sprite.open_chat())
        bar.addWidget(chat)
        self.gear = QPushButton("⚙", objectName="icon")
        self.gear.setToolTip("Settings")
        self.gear.clicked.connect(self._toggle_settings)
        self.snd = QPushButton("🔊", objectName="icon")
        self.snd.setToolTip("Sound on/off")
        self.snd.clicked.connect(self._toggle_sound)
        close = QPushButton("✕", objectName="icon")
        close.clicked.connect(self.hide)
        for w in (self.gear, self.snd, close):
            w.setCursor(Qt.PointingHandCursor)
            bar.addWidget(w)
        root.addLayout(bar)

        # ---- settings strip (hidden until ⚙)
        self.settings = QWidget()
        sl = QHBoxLayout(self.settings)
        sl.setContentsMargins(0, 0, 0, 0)
        self.s_roam = QPushButton("Roam around")
        self.s_body = QPushButton("Full body")
        self.s_start = QPushButton("Start with Windows")
        self.s_focus = QPushButton("Focus mode · 1 h")
        self.s_voice = QPushButton("Voice")
        self.s_voice.setToolTip("J speaks and listens - hold Right Ctrl to talk")
        for b in (self.s_roam, self.s_body, self.s_start, self.s_voice):
            b.setCheckable(True)
        self.s_roam.clicked.connect(lambda: (self.sprite._toggle_roam(), self._sync()))
        self.s_body.clicked.connect(lambda: (self.sprite.toggle_body(), self._sync()))
        self.s_start.clicked.connect(self._toggle_startup)
        self.s_focus.clicked.connect(self._focus)
        self.s_voice.clicked.connect(lambda: (self.sprite.toggle_voice(), self._sync()))
        for b in (self.s_roam, self.s_body, self.s_start, self.s_voice, self.s_focus):
            b.setCursor(Qt.PointingHandCursor)
            sl.addWidget(b)
        sl.addStretch(1)
        self.settings.setVisible(False)
        root.addWidget(self.settings)

        # ---- pages
        self.stack = QStackedWidget()
        root.addWidget(self.stack)
        self.stack.addWidget(self._home_page())
        self.today = TodayView(on_jump=self._jump_sid)
        self.stack.addWidget(self.today)
        self.sess_page = QWidget()
        self.sess_rows = QVBoxLayout(self.sess_page)
        self.sess_rows.setContentsMargins(0, 0, 0, 0)
        self.sess_rows.setSpacing(6)
        self.stack.addWidget(self.sess_page)
        self.agent_page = QWidget()
        self.agent_rows = QVBoxLayout(self.agent_page)
        self.agent_rows.setContentsMargins(0, 0, 0, 0)
        self.agent_rows.setSpacing(6)
        self.stack.addWidget(self.agent_page)

        self.fade = QVariantAnimation(self, startValue=0.0, endValue=1.0, duration=170)
        self.fade.valueChanged.connect(lambda v: self.setWindowOpacity(float(v)))
        self.show_tab(0)

    # ---------------------------------------------------------------- home
    def _home_page(self):
        page = QWidget()
        lay = QHBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        left = QWidget(objectName="tile")
        ll = QHBoxLayout(left)
        ll.setContentsMargins(10, 8, 12, 8)
        ll.addWidget(CoreView(self.sprite))
        info = QVBoxLayout()
        info.setSpacing(3)
        self.h_title = QLabel("", objectName="title")
        self.h_state = QLabel("")
        self.h_guard = QLabel("", objectName="muted")
        self.h_wait = QLabel("", objectName="muted")
        for w in (self.h_title, self.h_state, self.h_guard, self.h_wait):
            w.setTextFormat(Qt.RichText)
            info.addWidget(w)
        acts = QHBoxLayout()
        acts.setSpacing(8)
        talk = QPushButton("💬 Talk to\nGaya")
        talk.setToolTip("Talk to Gaya: send a message or prompt into your active session")
        talk.setMinimumHeight(46)
        talk.clicked.connect(lambda: self.sprite.open_chat())

        self.b_jump = QPushButton("⚡ Jump In\n(Session)")
        self.b_jump.setToolTip("Jump to the active Antigravity session or IDE window")
        self.b_jump.setMinimumHeight(46)
        self.b_jump.clicked.connect(self._jump_waiting)

        council = QPushButton("🏛️ Council\nDashboard")
        council.setToolTip("Open Council of Gaya command center (http://localhost:4200)")
        council.setMinimumHeight(46)
        council.clicked.connect(self._council)

        for b in (talk, self.b_jump, council):
            b.setCursor(Qt.PointingHandCursor)
            acts.addWidget(b)
        info.addSpacing(4)
        info.addLayout(acts)
        info.addStretch(1)
        ll.addLayout(info)
        lay.addWidget(left, 1)

        right = QWidget(objectName="tile")
        grid = QGridLayout(right)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setSpacing(8)
        self.pills = {}
        for i, (key, name, rgb, role) in enumerate(AGENTS):
            pill = AgentPill(self, key, name, rgb, role)
            self.pills[key] = pill
            grid.addWidget(pill, i // 2, i % 2)
        right.setFixedWidth(300)
        lay.addWidget(right, 0)
        return page

    def _agent_info(self):
        latest = {}
        for f in glob.glob(os.path.join(KB, "*", "*.md")):
            parts = os.path.basename(f).split("-")
            if len(parts) < 3:
                continue
            agent = "dum-e" if parts[1] == "dum" else parts[1]
            mt = os.path.getmtime(f)
            if agent not in latest or mt > latest[agent][0]:
                latest[agent] = (mt, f)
        verdicts = {}
        try:
            for ln in open(os.path.join(JDIR, "logs", "events.jsonl"), encoding="utf-8").readlines()[-500:]:
                e = json.loads(ln)
                if e.get("ev") == "subagent_stop" and e.get("verdict") in ("PASS", "FAIL"):
                    verdicts[e.get("agent")] = e["verdict"]
        except Exception:
            pass
        return latest, verdicts

    # ---------------------------------------------------------------- refresh
    def refresh(self, force=False):
        s = self.sprite
        st = "hold" if s.requests else s.state
        col = "#%02x%02x%02x" % STATE_RGB.get(st, STATE_RGB["idle"])
        waiting = [r for r in s.sessions if r["status"] == "waiting"]
        working = [r for r in s.sessions if r["status"] == "working"]
        self.h_title.setText("MINI GAYA")
        self.h_state.setText('<span style="color:%s">●</span>&nbsp; %s%s' % (
            col, st.capitalize(), (" · %d approval%s waiting" % (len(s.requests), "s" * (len(s.requests) > 1)))
            if s.requests else ""))
        self.h_guard.setText("Guard %s  ·  %d holds today" % (s.armed, s.holds))
        self.h_wait.setText('<span style="color:#ffb020">%d waiting</span>  ·  '
                            '<span style="color:#57c7ff">%d working</span>  ·  %d sessions'
                            % (len(waiting), len(working), len(s.sessions)))
        self.b_jump.setEnabled(True)
        latest, verdicts = self._agent_info()
        for key, pill in self.pills.items():
            if key in latest:
                mt, f = latest[key]
                v = verdicts.get(key, "")
                pill.set_info(("%s · %s ago" % (v, _ago(time.time() - mt))) if v else "reported %s ago" % _ago(time.time() - mt), "", f)
        self.snd.setText("🔇" if s.sound.muted else "🔊")
        self._sync()
        if self.stack.currentIndex() == 1:
            if force:
                self.today.fill(gather(s.sessions))
                self.relayout()
        elif self.stack.currentIndex() == 2:
            self._fill_sessions(force)
        elif self.stack.currentIndex() == 3:
            self._fill_agents(latest, verdicts, force)

    def _fill_sessions(self, force=False):
        s = self.sprite
        sig = tuple((r["id"], r["status"], r["tool"], int(r["idle_s"] // 60)) for r in s.sessions[:6])
        if sig == self.sig and not force:
            return
        if any(w.hot for w in self.sess_page.findChildren(SessionRow)):
            return                                     # never rebuild under the mouse
        self.sig = sig
        self._clear(self.sess_rows)
        if not s.sessions:
            self.sess_rows.addWidget(QLabel("No Antigravity sessions in the last 3 hours.", objectName="muted"))
        for r in s.sessions[:6]:
            self.sess_rows.addWidget(SessionRow(self, r))
        self.relayout()

    def _fill_agents(self, latest, verdicts, force=False):
        self._clear(self.agent_rows)
        files = sorted(glob.glob(os.path.join(KB, "*", "*.md")), key=os.path.getmtime, reverse=True)[:7]
        if not files:
            self.agent_rows.addWidget(QLabel("No agent reports yet.", objectName="muted"))
        roster = {a[0] for a in AGENTS} | {"general", "explore", "plan"}
        for f in files:
            parts = os.path.basename(f).split("-")
            agent = ("dum-e" if len(parts) > 1 and parts[1] == "dum" else parts[1] if len(parts) > 1 else "?")
            if agent not in roster:
                continue                               # skip compaction summaries etc.
            rgb = next((a[2] for a in AGENTS if a[0] == agent), (200, 200, 200))
            try:
                body = open(f, encoding="utf-8").read().split("\n\n", 2)[-1]
            except OSError:
                body = ""
            first = " ".join(body.split())[:110]
            b = QPushButton("%s  ·  %s ago\n%s" % (agent.upper(), _ago(time.time() - os.path.getmtime(f)), first))
            b.setStyleSheet("text-align:left; padding:7px 10px; border-left:3px solid rgb(%d,%d,%d);" % rgb)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, f=f: os.startfile(f))
            self.agent_rows.addWidget(b)
        self.relayout()

    @staticmethod
    def _clear(lay):
        while lay.count():
            w = lay.takeAt(0).widget()
            if w:
                w.deleteLater()

    # ---------------------------------------------------------------- actions
    def show_tab(self, i):
        for j, b in enumerate(self.tabs):
            b.setChecked(i == j)
        self.stack.setCurrentIndex(i)
        self.sig = None
        self.refresh(force=True)
        self.relayout()

    def _toggle_settings(self):
        self.settings.setVisible(not self.settings.isVisible())
        self._sync()
        self.relayout()

    def _sync(self):
        self.s_roam.setChecked(bool(self.sprite.roam))
        self.s_body.setChecked(bool(getattr(self.sprite, "body_on", False)))
        v = getattr(self.sprite, "voice", None)
        self.s_voice.setChecked(bool(v and v.enabled))
        self.s_start.setChecked(os.path.exists(STARTUP))

    def _toggle_sound(self):
        self.sprite._mute()
        self.snd.setText("🔇" if self.sprite.sound.muted else "🔊")

    def _toggle_startup(self):
        try:
            if os.path.exists(STARTUP):
                os.remove(STARTUP)
                self.sprite.toast("info", "Mini Gaya won't start with Windows", "")
            else:
                here = os.path.dirname(os.path.abspath(__file__))
                with open(STARTUP, "w") as f:
                    f.write('@echo off\r\nstart "" pythonw "%s" --boot\r\n' % os.path.join(here, "mini_gaya.py"))
                self.sprite.toast("approved", "Mini Gaya starts with Windows now", "toggle it off here any time")
        except OSError as e:
            self.sprite.toast("broken", "Couldn't change startup", str(e)[:80])
        self._sync()

    def _focus(self):
        self.hide()
        self.sprite.user_hidden = True
        self.sprite._visibility()
        QTimer.singleShot(3600_000, lambda: (setattr(self.sprite, "user_hidden", False), self.sprite._visibility()))

    def _jump_waiting(self):
        w = [r for r in self.sprite.sessions if r.get("status") in ("waiting", "hold")]
        if w:
            self.jump(w[0])
            return
        working = [r for r in self.sprite.sessions if r.get("status") == "working" or r.get("live")]
        if working:
            self.jump(working[0])
            return
        if self.sprite.sessions:
            self.jump(self.sprite.sessions[0])
            return
        ok = focus_session({"entry": "antigravity", "cwd": "d:\\Ai_Tools\\antigravity_ai"})
        self.sprite.toast("info" if ok else "hold",
                          "Jumped to Antigravity IDE" if ok else "No active editor found",
                          "Active workspace" if ok else "Launch Antigravity or open an editor")

    def _jump_sid(self, sid):
        focus_session({"sid": sid})

    def _council(self):
        QDesktopServices.openUrl(QUrl("http://localhost:4200"))

    def jump(self, r):
        ok = focus_session(r)
        self.sprite.toast("info", ("Jumping to %s" % r["title"][:40]) if ok else "Couldn't find that window",
                          r.get("cwd_full", "") if ok else "it may be in a closed editor")

    # ---------------------------------------------------------------- show / place
    def relayout(self):
        """Size to the CURRENT page only. Hidden pages are 'Ignored' so the stack
        never takes the tallest page's height; the real resize runs after Qt has
        laid out freshly added rows (measuring before that gave 0 px - the
        'empty tab' bug Boss hit)."""
        cur = self.stack.currentIndex()
        for i in range(self.stack.count()):
            pol = QSizePolicy.Preferred if i == cur else QSizePolicy.Ignored
            self.stack.widget(i).setSizePolicy(pol, pol)
        QTimer.singleShot(0, self._resize_now)

    def _resize_now(self):
        page = self.stack.currentWidget()
        if page is not None and page.layout():
            page.layout().activate()
        self.stack.setMinimumHeight(0)
        self.stack.setMaximumHeight(16777215)
        self.card.layout().activate()
        self.card.adjustSize()
        self.adjustSize()
        if self.isVisible():
            self.sprite._layout_bubbles()

    def open(self):
        self.refresh(force=True)
        self.setWindowOpacity(0.0)
        self.show()
        self.relayout()
        self.fade.start()
