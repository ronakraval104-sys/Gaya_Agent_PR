"""JARVIS Island - the Command Core, docked to the top edge of the screen.

Collapsed : a small black notch fused to the top edge. The Command Core glows
            inside it (colour = JARVIS's live state); one dot per Claude Code
            session (cyan pulsing = working, amber = waiting for you, grey = idle).
Hover     : expands into a brief - every recent session, what it is doing,
            the last thing you asked it, harness status.
Toasts    : the notch drops a one-line notification when a session finishes
            and waits for you, a subagent reports, EDIDTH signs, or the guard holds.
Click     : pin / unpin the brief.  Drag: slide along the top edge.
Games     : hides itself while a fullscreen game / app / presentation runs.
Tray icon : click to show / hide; right-click for pin, demo, quit.
"""
import glob
import json
import math
import os
import sys
import time
from collections import deque

from PIL import Image, ImageChops
from PySide6.QtCore import QEasingCurve, QRectF, Qt, QTimer, QVariantAnimation
from PySide6.QtGui import (QAction, QColor, QFont, QFontMetrics, QIcon, QImage, QPainter,
                           QPainterPath, QPixmap)
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import jarvis_state  # noqa: E402

LAYERS = os.path.join(HERE, "layers")
PREFS = os.path.join(os.path.expanduser("~"), ".jarvis", "island.json")
PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects")

STATE_RGB = {"idle": (255, 215, 60), "thinking": (255, 175, 40), "spawning": (255, 235, 120),
             "hold": (255, 120, 20), "broken": (255, 59, 59), "approved": (47, 225, 120),
             "asleep": (160, 145, 120)}
DOT = {"working": QColor(255, 215, 60), "waiting": QColor(255, 140, 25), "idle": QColor(100, 95, 90),
       "closed": QColor(60, 58, 62)}
BG = QColor(6, 6, 8)
TEXT = QColor(236, 238, 242)
MUTED = QColor(140, 144, 152)
DIM = QColor(88, 92, 100)

ICON = 22                    # logical px of the core inside the notch
COLLAPSED_H = 30
EXPANDED_W = 400
TOAST_W = 360
MAX_ROWS = 5


# ------------------------------------------------------------------ art
def compose_core(rgb, glow_k, bloom_k, body_k=1.0, px=64):
    """Base body + tinted bloom + tinted glow, Lanczos down to exact pixels."""
    base = Image.open(os.path.join(LAYERS, "base.png")).convert("RGBA")
    out = Image.new("RGBA", base.size, (0, 0, 0, 0))
    if body_k < 1:
        base.putalpha(base.getchannel("A").point(lambda v: int(v * body_k)))
    out.alpha_composite(base)
    for name, k in (("bloom.png", bloom_k), ("glow.png", glow_k)):
        if k <= 0:
            continue
        a = Image.open(os.path.join(LAYERS, name)).getchannel("A").point(lambda v: min(255, int(v * k)))
        lay = Image.new("RGBA", base.size, rgb + (255,))
        lay.putalpha(a)
        out.alpha_composite(lay)
    bbox = out.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox() or (0, 0, *out.size)
    side = max(bbox[2] - bbox[0], bbox[3] - bbox[1])
    cx, cy = (bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2
    sq = out.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2))
    return sq.resize((px, px), Image.LANCZOS)


def to_pixmap(pil, dpr):
    data = pil.tobytes("raw", "RGBA")
    img = QImage(data, pil.width, pil.height, QImage.Format_RGBA8888).copy()
    pm = QPixmap.fromImage(img)
    pm.setDevicePixelRatio(dpr)
    return pm


# ------------------------------------------------------------------ sessions
def tail_lines(path, nbytes=300_000):
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - nbytes))
            return f.read().decode("utf-8", "replace").splitlines()[1:]
    except OSError:
        return []


def live_sessions():
    """Sessions running right now, from Claude Code's own registry
    (~/.claude/sessions/<pid>.json): sessionId -> {pid, name, status, cwd, ...}.
    status is "busy" while a turn runs, "idle" between turns."""
    out = {}
    for f in glob.glob(os.path.join(os.path.expanduser("~"), ".claude", "sessions", "*.json")):
        try:
            d = json.load(open(f, encoding="utf-8"))
            if d.get("sessionId"):
                out[d["sessionId"]] = d
        except (OSError, ValueError):
            continue
    return out


def read_antigravity_sessions(window_s=3 * 3600):
    import sqlite3
    from datetime import datetime
    
    db_path = os.path.join(os.environ.get("USERPROFILE", ""), ".gemini", "antigravity", "conversation_summaries.db")
    presence_dir = os.path.join(os.environ.get("USERPROFILE", ""), ".gemini", "antigravity", "presence")
    brain_dir = os.path.join(os.environ.get("USERPROFILE", ""), ".gemini", "antigravity", "brain")
    
    if not os.path.exists(db_path):
        return []
        
    rows = []
    now = time.time()
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        c = conn.cursor()
        c.execute("""
            SELECT conversation_id, title, preview, step_count, last_modified_time, status, workspace_uris
            FROM conversation_summaries
            ORDER BY last_modified_time DESC
            LIMIT 12
        """)
        for cid, title, preview, step_count, lmt, status_str, uris in c.fetchall():
            lock_file = os.path.join(presence_dir, f"{cid}.lock")
            is_live = os.path.exists(lock_file)
            
            try:
                lmt_clean = lmt.split("+")[0].strip()
                dt = datetime.fromisoformat(lmt_clean)
                mt = dt.timestamp()
                idle_s = max(0, now - mt)
            except Exception:
                mt = now
                idle_s = 0
                
            if is_live:
                status = "working" if "RUNNING" in status_str else "idle"
            elif idle_s < window_s:
                status = "idle"
            else:
                status = "closed"
                
            prompt = preview or ""
            tool = ""
            
            tpath = os.path.join(brain_dir, cid, ".system_generated", "logs", "transcript.jsonl")
            if os.path.exists(tpath):
                try:
                    for line in tail_lines(tpath, n=6):
                        d = json.loads(line)
                        if d.get("type") == "USER_INPUT" and d.get("content"):
                            prompt = str(d["content"])
                        elif d.get("type") == "PLANNER_RESPONSE" and d.get("tool_calls"):
                            tc = d["tool_calls"]
                            if tc and isinstance(tc, list):
                                tool = tc[0].get("name", "")
                except Exception:
                    pass
                    
            rows.append({
                "id": cid[:8],
                "title": title or "Antigravity Session",
                "live": is_live,
                "pid": None,
                "status": status,
                "tool": tool,
                "idle_s": idle_s,
                "reply": preview or "",
                "prompt": prompt[:80] if prompt else "",
                "cwd": "d:\\Ai_Tools\\antigravity_ai",
                "entry": "antigravity",
                "turns": step_count or 0,
                "mt": mt,
            })
        conn.close()
    except Exception:
        pass
    return rows


def read_sessions(window_s=3 * 3600):
    ag_rows = read_antigravity_sessions(window_s)
    if ag_rows:
        return ag_rows
    now = time.time()
    rows = []
    live = live_sessions()
    for f in glob.glob(os.path.join(PROJECTS, "*", "*.jsonl")):
        try:
            mt = os.path.getmtime(f)
        except OSError:
            continue
        if now - mt > window_s:
            continue
        title = prompt = last_text = tool = cwd = entry = ""
        last_role = ""
        for ln in tail_lines(f):
            try:
                d = json.loads(ln)
            except ValueError:
                continue
            t = d.get("type")
            if t == "custom-title":
                title = d.get("customTitle") or title
            elif t == "ai-title" and not title:
                title = d.get("aiTitle") or title
            elif t == "last-prompt":
                prompt = d.get("lastPrompt") or d.get("prompt") or prompt
            elif t in ("user", "assistant"):
                cwd = d.get("cwd") or cwd
                entry = d.get("entrypoint") or entry
                msg = d.get("message") or {}
                content = msg.get("content")
                if t == "user":
                    if isinstance(content, str) and not content.startswith("<"):
                        prompt, last_role = content, "user"
                    elif isinstance(content, list) and any(
                            b.get("type") == "text" and not str(b.get("text", "")).startswith("<")
                            for b in content if isinstance(b, dict)):
                        last_role = "user"
                elif isinstance(content, list):
                    for b in content:
                        if not isinstance(b, dict):
                            continue
                        if b.get("type") == "text" and b.get("text", "").strip():
                            last_text, last_role = b["text"], "assistant"
                        elif b.get("type") == "tool_use":
                            tool, last_role = b.get("name", ""), "tool"
        idle_s = now - mt
        sid_full = os.path.splitext(os.path.basename(f))[0]
        lv = live.get(sid_full)
        if lv:                                   # exact: the session is open right now
            if lv.get("status") == "busy" or idle_s < 15:
                status = "working"
            elif last_role == "assistant":
                status = "waiting"
            else:
                status = "idle"
        elif idle_s < 25:
            status = "working"
        else:
            status = "closed"
        rows.append({"id": os.path.basename(f)[:8], "title": title or (lv or {}).get("name") or "untitled session",
                     "live": bool(lv), "pid": (lv or {}).get("pid"),
                     "prompt": " ".join(str(prompt).split())[:90], "tool": tool,
                     "reply": " ".join(last_text.split())[:110], "status": status,
                     "idle_s": idle_s, "cwd": os.path.basename(cwd.rstrip("\\/")) if cwd else "",
                     "sid": os.path.splitext(os.path.basename(f))[0],
                     "cwd_full": cwd, "entry": entry, "reply_full": last_text.strip()[:1500],
                     "prompt_full": str(prompt).strip()[:600]})
    rank = {"waiting": 0, "working": 1, "idle": 2, "closed": 3}
    rows.sort(key=lambda r: (rank[r["status"]], r["idle_s"]))
    return rows


def ago(s):
    s = int(s)
    return "now" if s < 25 else "%ds" % s if s < 60 else "%dm" % (s // 60) if s < 3600 else "%dh" % (s // 3600)


# ------------------------------------------------------------------ fullscreen / game check
# Apps that go fullscreen but are work, not games - JARVIS stays visible over them.
WORK_APPS = {"code.exe", "chrome.exe", "msedge.exe", "firefox.exe", "explorer.exe",
             "windowsterminal.exe", "claude.exe", "obsidian.exe", "coucou.exe", "python.exe",
             "pythonw.exe", "powershell.exe", "cmd.exe", "searchhost.exe", "shellexperiencehost.exe",
             "startmenuexperiencehost.exe", "lockapp.exe"}


def _foreground_exe(hwnd):
    import ctypes
    from ctypes import wintypes
    pid = wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid.value)   # QUERY_LIMITED_INFORMATION
    if not h:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(520)
        n = wintypes.DWORD(520)
        ctypes.windll.kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n))
        return os.path.basename(buf.value).lower()
    finally:
        ctypes.windll.kernel32.CloseHandle(h)


def fullscreen_busy():
    """True while a game (or any non-work app) owns the whole monitor.

    Windows' own "busy" flag (QUNS_BUSY) also fires for overlays like an FPS
    counter, so it is NOT used. Signals: exclusive D3D fullscreen, or the
    foreground window covering its entire monitor and not being a work app.
    """
    try:
        import ctypes
        from ctypes import wintypes
        st = ctypes.c_int(0)
        if ctypes.windll.shell32.SHQueryUserNotificationState(ctypes.byref(st)) == 0 and st.value in (3, 4):
            return True                              # exclusive D3D fullscreen / presentation
        u = ctypes.windll.user32
        hwnd = u.GetForegroundWindow()
        if not hwnd:
            return False
        cls = ctypes.create_unicode_buffer(64)
        u.GetClassNameW(hwnd, cls, 64)
        if cls.value in ("Progman", "WorkerW", "Shell_TrayWnd"):
            return False
        r = wintypes.RECT()
        u.GetWindowRect(hwnd, ctypes.byref(r))

        class MONITORINFO(ctypes.Structure):
            _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT),
                        ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(MONITORINFO)
        u.GetMonitorInfoW(u.MonitorFromWindow(hwnd, 2), ctypes.byref(mi))
        m = mi.rcMonitor
        covers = r.left <= m.left and r.top <= m.top and r.right >= m.right and r.bottom >= m.bottom
        return covers and _foreground_exe(hwnd) not in WORK_APPS
    except Exception:
        return False


# ------------------------------------------------------------------ the island
class Island(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
                            | Qt.NoDropShadowWindowHint | Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)     # never steal focus (Coucou rule)
        self.setMouseTracking(True)
        self.screen_ = QApplication.primaryScreen()
        self.dpr = self.screen_.devicePixelRatio()
        prefs = self._load()
        self.offset = prefs.get("offset", 250)          # px right of screen centre
        self.state, self.detail, self.armed, self.holds = "idle", "", "?", 0
        self.sessions, self.prev_status = [], {}
        self.toasts, self.toast = deque(), None
        self.hover = self.pinned = self.demo = False
        self.user_hidden = False
        self.t0 = time.time()
        self.seen_ev = self._log_size()
        self._drag_x = None

        px = round(ICON * self.dpr)
        self.core = {}
        for s, rgb in STATE_RGB.items():
            self.core[s] = (to_pixmap(compose_core(rgb, 0.55, 0.25, px=px), self.dpr),
                            to_pixmap(compose_core(rgb, 1.0, 0.75, px=px), self.dpr))
        self.core_off = to_pixmap(compose_core(STATE_RGB["asleep"], 0.12, 0, 0.6, px=px), self.dpr)
        big = round(64 * self.dpr)
        self.tray_icon_pm = to_pixmap(compose_core(STATE_RGB["idle"], 1.0, 0.6, px=big), self.dpr)

        self.f_title = QFont("Segoe UI Semibold", 9)
        self.f_body = QFont("Segoe UI", 8)
        self.f_small = QFont("Segoe UI", 7)
        self.f_mono = QFont("Cascadia Mono", 7)

        self.w = self.collapsed_w()
        self.h = COLLAPSED_H
        self.anim = QVariantAnimation(self, duration=220, easingCurve=QEasingCurve.OutCubic)
        self.anim.valueChanged.connect(self._on_anim)
        self._place()

        QTimer(self, timeout=self.update, interval=33).start()
        QTimer(self, timeout=self.poll, interval=1200).start()
        QTimer(self, timeout=self.check_fullscreen, interval=2000).start()
        self.collapse_timer = QTimer(self, singleShot=True, interval=450, timeout=self._maybe_collapse)
        self.toast_timer = QTimer(self, singleShot=True, interval=4800, timeout=self._end_toast)
        self._tray()
        self.poll()

    # ---------------------------------------------------------------- data
    def _log_size(self):
        try:
            return os.path.getsize(jarvis_state.LOG)
        except OSError:
            return 0

    def poll(self):
        if self.demo:
            states = list(STATE_RGB)
            self.state = states[int((time.time() - self.t0) // 3) % len(states)]
        else:
            try:
                s = jarvis_state.current()
                self.state, self.detail = s["state"], s.get("detail", "")
                self.armed, self.holds = s.get("armed", "?"), s.get("holds_today", 0)
            except Exception as e:
                self.state, self.detail = "broken", str(e)[:60]
        try:
            self.sessions = read_sessions()
        except Exception:
            self.sessions = []
        self._notify_from_sessions()
        self._notify_from_log()
        if not self.anim.state() and not self.toast:
            self._resize_to(self.target_size())
        self.tray.setToolTip("JARVIS - %s" % self.state)

    def _notify_from_sessions(self):
        for r in self.sessions:
            before = self.prev_status.get(r["id"])
            if before == "working" and r["status"] == "waiting":
                self.push_toast("waiting", "%s is waiting for you" % r["title"][:38], r["reply"][:70])
        self.prev_status = {r["id"]: r["status"] for r in self.sessions}

    def _notify_from_log(self):
        size = self._log_size()
        if size <= self.seen_ev:
            self.seen_ev = size
            return
        try:
            with open(jarvis_state.LOG, "rb") as f:
                f.seek(self.seen_ev)
                chunk = f.read().decode("utf-8", "replace")
        except OSError:
            return
        self.seen_ev = size
        for ln in chunk.splitlines():
            try:
                e = json.loads(ln)
            except ValueError:
                continue
            if e.get("ev") == "guard":
                self.push_toast("hold", "Guard %s - your call" % e.get("decision", "held"),
                                (e.get("reason") or "")[:70])
            elif e.get("ev") == "subagent_stop":
                agent = str(e.get("agent", "agent")).upper()
                v = e.get("verdict")
                if v and v.startswith("PASS"):
                    self.push_toast("approved", "EDIDTH signed off - PASS", ", ".join(e.get("tokens") or [])[:70])
                elif v and v.startswith("FAIL"):
                    self.push_toast("broken", "EDIDTH: FAIL", "fixes needed - see the report")
                else:
                    self.push_toast("spawning", "%s reported back" % agent, "saved to the KB")

    # ---------------------------------------------------------------- toasts
    def push_toast(self, kind, title, body=""):
        self.toasts.append((kind, title, body))
        if not self.toast:
            self._next_toast()

    def _next_toast(self):
        if not self.toasts:
            self.toast = None
            self._resize_to(self.target_size())
            return
        self.toast = self.toasts.popleft()
        self.toast_t = time.time()
        self._resize_to((TOAST_W, 54))
        self.toast_timer.start()

    def _end_toast(self):
        self._next_toast()

    # ---------------------------------------------------------------- geometry
    def collapsed_w(self):
        return 44 + 13 * max(1, min(len(getattr(self, "sessions", [])) or 1, 6)) + 12

    def target_size(self):
        if self.hover or self.pinned:
            n = min(len(self.sessions), MAX_ROWS)
            return (EXPANDED_W, 58 + max(n, 1) * 46 + 26)
        return (self.collapsed_w(), COLLAPSED_H)

    def _resize_to(self, wh):
        if (round(self.w), round(self.h)) == wh:
            return
        self.anim.stop()
        self.anim.setStartValue(QRectF(0, 0, self.w, self.h))
        self.anim.setEndValue(QRectF(0, 0, *wh))
        self.anim.start()

    def _on_anim(self, r):
        self.w, self.h = r.width(), r.height()
        self._place()

    def _place(self):
        g = self.screen_.geometry()
        x = g.center().x() + self.offset - self.w / 2
        x = max(g.left(), min(x, g.right() - self.w))
        self.setGeometry(round(x), g.top(), round(self.w), round(self.h))

    # ---------------------------------------------------------------- visibility
    def check_fullscreen(self):
        should_show = not self.user_hidden and not fullscreen_busy()
        if should_show and not self.isVisible():
            self.show()
        elif not should_show and self.isVisible():
            self.hide()

    def toggle_visible(self):
        self.user_hidden = not self.user_hidden
        self.check_fullscreen()

    # ---------------------------------------------------------------- paint
    def paintEvent(self, _):
        t = time.time() - self.t0
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
        w, h = self.w, self.h

        # notch body: square top (fused to screen edge), round bottom corners
        r = 14 if h <= COLLAPSED_H + 2 else 18
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(w, 0)
        path.lineTo(w, h - r)
        path.quadTo(w, h, w - r, h)
        path.lineTo(r, h)
        path.quadTo(0, h, 0, h - r)
        path.closeSubpath()
        p.fillPath(path, BG)
        # hairline in state colour along the bottom - the notch "breathes"
        rgb = STATE_RGB[self.state]
        breath = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 3.6)
        edge = QColor(*rgb, int(40 + 50 * breath) if self.state != "asleep" else 18)
        p.setPen(edge)
        p.drawLine(round(r), round(h) - 1, round(w - r), round(h) - 1)

        # the core
        cy = COLLAPSED_H / 2
        cx = 14 + ICON / 2
        self._draw_core(p, cx, cy, t)

        if self.toast:
            self._paint_toast(p, w, h, t)
        elif self.hover or self.pinned:
            self._paint_brief(p, w, h, t)
        else:
            self._paint_dots(p, t)
        p.end()

    def _draw_core(self, p, cx, cy, t):
        st = self.state
        dim, bright = self.core[st]
        if st == "asleep":
            p.drawPixmap(round(cx - ICON / 2), round(cy - ICON / 2), self.core_off)
            return
        speed = {"idle": 3.6, "thinking": 1.4, "spawning": 0.9, "hold": 2.0,
                 "broken": 0.5, "approved": 1.0}.get(st, 3.6)
        k = 0.5 + 0.5 * math.sin(t * 2 * math.pi / speed)
        if st == "broken" and int(t * 9) % 7 == 0:
            k = 0.05
        if self.hover:
            k = max(k, 0.85)
        # an occasional blink - it is alive
        if st in ("idle", "thinking") and (t % 6.5) < 0.12:
            k = 0.0
        x, y = round(cx - ICON / 2), round(cy - ICON / 2)
        p.drawPixmap(x, y, dim)
        p.setOpacity(k)
        p.drawPixmap(x, y, bright)
        p.setOpacity(1.0)

    def _paint_dots(self, p, t):
        x = 14 + ICON + 10
        cy = COLLAPSED_H / 2
        if not self.sessions:
            p.setPen(DIM)
            p.setFont(self.f_small)
            p.drawText(QRectF(x, 0, 60, COLLAPSED_H), Qt.AlignVCenter, "quiet")
            return
        for r in self.sessions[:6]:
            c = QColor(DOT[r["status"]])
            if r["status"] == "working":
                c.setAlphaF(0.55 + 0.45 * math.sin(t * 5))
            p.setPen(Qt.NoPen)
            p.setBrush(c)
            p.drawEllipse(QRectF(x, cy - 3.5, 7, 7))
            x += 13

    def _paint_brief(self, p, w, h, t):
        p.setPen(TEXT)
        p.setFont(self.f_title)
        p.drawText(QRectF(14 + ICON + 10, 0, 200, COLLAPSED_H), Qt.AlignVCenter, "JARVIS")
        p.setFont(self.f_mono)
        p.setPen(QColor(*STATE_RGB[self.state]))
        right = "%s  ·  %s  ·  %d holds today%s" % (self.state.upper(), self.armed, self.holds,
                                                   "  ·  PINNED" if self.pinned else "")
        p.drawText(QRectF(0, 0, w - 14, COLLAPSED_H), Qt.AlignVCenter | Qt.AlignRight, right)
        p.setPen(QColor(255, 255, 255, 18))
        p.drawLine(14, 34, round(w) - 14, 34)

        y = 42
        if not self.sessions:
            p.setPen(MUTED)
            p.setFont(self.f_body)
            p.drawText(QRectF(14, y, w - 28, 40), Qt.AlignVCenter, "No Antigravity sessions in the last 3 hours.")
        fm = QFontMetrics(self.f_body)
        for r in self.sessions[:MAX_ROWS]:
            c = QColor(DOT[r["status"]])
            if r["status"] == "working":
                c.setAlphaF(0.55 + 0.45 * math.sin(t * 5))
            p.setPen(Qt.NoPen)
            p.setBrush(c)
            p.drawEllipse(QRectF(16, y + 6, 7, 7))
            p.setPen(TEXT)
            p.setFont(self.f_body)
            title = fm.elidedText(r["title"], Qt.ElideRight, int(w - 150))
            p.drawText(QRectF(30, y, w - 150, 18), Qt.AlignVCenter, title)
            status = {"working": "working%s" % (" · " + r["tool"] if r["tool"] else ""),
                      "waiting": "waiting for you · %s" % ago(r["idle_s"]),
                      "idle": "idle · %s" % ago(r["idle_s"])}[r["status"]]
            p.setPen(QColor(DOT[r["status"]]) if r["status"] != "idle" else MUTED)
            p.setFont(self.f_small)
            p.drawText(QRectF(0, y, w - 14, 18), Qt.AlignVCenter | Qt.AlignRight, status)
            p.setPen(MUTED)
            sub = r["reply"] if r["status"] == "waiting" and r["reply"] else (
                "> " + r["prompt"] if r["prompt"] else r["cwd"])
            fm2 = QFontMetrics(self.f_small)
            p.drawText(QRectF(30, y + 18, w - 44, 16), Qt.AlignVCenter,
                       fm2.elidedText(sub, Qt.ElideRight, int(w - 44)))
            y += 46
        more = len(self.sessions) - MAX_ROWS
        p.setPen(DIM)
        p.setFont(self.f_small)
        foot = ("+%d more  ·  " % more if more > 0 else "") + "click to %s  ·  drag to move" % (
            "unpin" if self.pinned else "pin")
        p.drawText(QRectF(14, h - 24, w - 28, 18), Qt.AlignVCenter, foot)

    def _paint_toast(self, p, w, h, t):
        kind, title, body = self.toast
        col = {"waiting": DOT["waiting"], "hold": QColor(255, 176, 32), "approved": QColor(47, 211, 111),
               "broken": QColor(255, 59, 59), "spawning": DOT["working"]}.get(kind, TEXT)
        p.setPen(col)
        p.setFont(self.f_title)
        fm = QFontMetrics(self.f_title)
        p.drawText(QRectF(14 + ICON + 10, 4, w - ICON - 40, 22), Qt.AlignVCenter,
                   fm.elidedText(title, Qt.ElideRight, int(w - ICON - 40)))
        if body:
            p.setPen(MUTED)
            p.setFont(self.f_small)
            fm2 = QFontMetrics(self.f_small)
            p.drawText(QRectF(14 + ICON + 10, 25, w - ICON - 40, 18), Qt.AlignVCenter,
                       fm2.elidedText(body, Qt.ElideRight, int(w - ICON - 40)))
        # progress hairline
        frac = min(1.0, (time.time() - self.toast_t) / 4.8)
        p.setPen(QColor(col.red(), col.green(), col.blue(), 120))
        p.drawLine(18, round(h) - 2, round(18 + (w - 36) * (1 - frac)), round(h) - 2)

    # ---------------------------------------------------------------- input
    def enterEvent(self, _):
        self.hover = True
        self.collapse_timer.stop()
        if not self.toast:
            self._resize_to(self.target_size())

    def leaveEvent(self, _):
        self.collapse_timer.start()

    def _maybe_collapse(self):
        if not self.underMouse():
            self.hover = False
            if not self.toast:
                self._resize_to(self.target_size())

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_x = e.globalPosition().x()
            self._drag_moved = False
            self._drag_off0 = self.offset

    def mouseMoveEvent(self, e):
        if self._drag_x is not None and e.buttons() & Qt.LeftButton:
            dx = e.globalPosition().x() - self._drag_x
            if abs(dx) > 4:
                self._drag_moved = True
                self.offset = self._drag_off0 + dx
                self._place()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            if not getattr(self, "_drag_moved", False):
                if self.toast:
                    self.toast_timer.stop()
                    self._next_toast()
                else:
                    self.pinned = not self.pinned
                    self._resize_to(self.target_size())
            self._drag_x = None
            self._save()

    def contextMenuEvent(self, e):
        self._menu().exec(e.globalPos())

    def _menu(self):
        m = QMenu()
        m.addAction(("Unpin" if self.pinned else "Pin") + " the brief", self._toggle_pin)
        m.addAction(("Stop" if self.demo else "Start") + " demo (all states)", self._toggle_demo)
        m.addAction("Test notification", lambda: self.push_toast("approved", "JARVIS online",
                                                                 "notifications are working, Boss"))
        m.addAction("Reset position", self._reset_pos)
        m.addSeparator()
        m.addAction("Hide JARVIS" if not self.user_hidden else "Show JARVIS", self.toggle_visible)
        m.addAction("Quit", QApplication.quit)
        return m

    def _toggle_pin(self):
        self.pinned = not self.pinned
        self._resize_to(self.target_size())

    def _toggle_demo(self):
        self.demo = not self.demo
        self.t0 = time.time()

    def _reset_pos(self):
        self.offset = 250
        self._place()
        self._save()

    # ---------------------------------------------------------------- tray
    def _tray(self):
        self.tray = QSystemTrayIcon(QIcon(self.tray_icon_pm), self)
        self.tray.setToolTip("JARVIS")
        self.tray.activated.connect(lambda reason: self.toggle_visible()
                                    if reason == QSystemTrayIcon.Trigger else None)
        self.tray_menu = self._menu()
        self.tray.setContextMenu(self.tray_menu)
        self.tray.show()

    # ---------------------------------------------------------------- prefs
    def _load(self):
        try:
            return json.load(open(PREFS))
        except Exception:
            return {}

    def _save(self):
        try:
            os.makedirs(os.path.dirname(PREFS), exist_ok=True)
            json.dump({"offset": self.offset}, open(PREFS, "w"))
        except Exception:
            pass


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    isl = Island()
    isl.show()
    isl.push_toast("approved", "JARVIS online", "hover me for the brief, Boss")
    sys.exit(app.exec())
