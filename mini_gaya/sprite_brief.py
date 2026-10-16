"""Daily brief + to-do checklist - what got done, what's left.

Shown when GAYA starts with Windows (and as the Deck's "Today" tab).
  Done   : Antigravity sessions you worked in (yesterday, or earlier today),
           EDIDTH sign-offs, commits.
  To do  : sessions still waiting on your reply, memory items marked
           RESUME HERE / IN-PROGRESS / pending, unpushed commits, Coucou
           still installed. Tick items off - ticks persist per day.
Everything is read locally; nothing is sent anywhere.
"""
import glob
import json
import os
import re
import subprocess
import time
from datetime import datetime, timedelta

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

HOME = os.path.expanduser("~")
JDIR = os.path.join(HOME, ".jarvis")
TODO = os.path.join(JDIR, "todo.json")
MEMORY = os.path.join(HOME, ".claude", "projects", "C--Users-Ronak", "memory", "MEMORY.md")
REPO = os.path.join(HOME, "Desktop", "GAYA")


def _window():
    """Yesterday 00:00 -> today 00:00 if it's morning, else today 00:00 -> now."""
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if now.hour < 12:
        return today - timedelta(days=1), today, "yesterday"
    return today, now, "earlier today"


def _sessions_between(start, end):
    out = []
    for f in glob.glob(os.path.join(HOME, ".claude", "projects", "*", "*.jsonl")):
        try:
            mt = os.path.getmtime(f)
        except OSError:
            continue
        if mt < start.timestamp():
            continue
        title, prompts, first_ts = "", 0, None
        try:
            with open(f, "rb") as fh:
                fh.seek(max(0, os.path.getsize(f) - 40_000_000))   # long sessions: last ~40 MB
                fh.readline()
                for raw in fh:
                    if b'"type":"user"' not in raw and b'title"' not in raw:
                        continue                                   # skip tool output fast
                    try:
                        d = json.loads(raw.decode("utf-8", "replace"))
                    except ValueError:
                        continue
                    t = d.get("type")
                    if t == "custom-title":
                        title = d.get("customTitle") or title
                    elif t == "ai-title" and not title:
                        title = d.get("aiTitle") or title
                    elif t == "user":
                        c = (d.get("message") or {}).get("content")
                        ts = d.get("timestamp", "")
                        try:
                            when = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().replace(tzinfo=None)
                        except ValueError:
                            continue
                        if isinstance(c, list):            # VS Code: list of content blocks
                            c = " ".join(b.get("text", "") for b in c
                                         if isinstance(b, dict) and b.get("type") == "text")
                        if start <= when < end and isinstance(c, str) and c.strip() \
                                and not c.lstrip().startswith("<"):
                            prompts += 1
        except OSError:
            continue
        if prompts:
            out.append({"title": title or "untitled session", "prompts": prompts,
                        "sid": os.path.splitext(os.path.basename(f))[0]})
    return sorted(out, key=lambda r: -r["prompts"])


def _edidth(start, end):
    n_pass = n_fail = 0
    try:
        for ln in open(os.path.join(JDIR, "logs", "events.jsonl"), encoding="utf-8"):
            try:
                e = json.loads(ln)
                when = datetime.fromisoformat(e.get("ts", ""))
            except Exception:
                continue
            if start <= when < end and e.get("ev") == "subagent_stop" and e.get("agent") == "edidth":
                v = str(e.get("verdict", ""))
                n_pass += v.startswith("PASS")
                n_fail += v.startswith("FAIL")
    except OSError:
        pass
    return n_pass, n_fail


def _git(*args):
    try:
        r = subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True, timeout=8,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return r.stdout.strip()
    except Exception:
        return ""


def gather(sessions_now=()):
    start, end, label = _window()
    done = []
    for s in _sessions_between(start, end)[:6]:
        done.append(("%s" % s["title"], "%d prompt%s" % (s["prompts"], "s" * (s["prompts"] > 1))))
    p, f = _edidth(start, end)
    if p or f:
        done.append(("EDIDTH reviews", "%d PASS · %d FAIL" % (p, f)))
    commits = [c for c in _git("log", "--since", start.isoformat(), "--until", end.isoformat(),
                               "--pretty=%s").splitlines() if c]
    if commits:
        done.append(("%d commit%s to GAYA" % (len(commits), "s" * (len(commits) > 1)), commits[0][:60]))

    todo = []
    for r in sessions_now:
        if r.get("status") == "waiting":
            todo.append({"id": "reply:" + r.get("sid", r["id"]), "text": "Reply to \"%s\"" % r["title"][:44],
                         "sid": r.get("sid", "")})
    try:
        for ln in open(MEMORY, encoding="utf-8"):
            if re.search(r"RESUME HERE|IN-PROGRESS|\(PLANNED\)|pending|awaiting", ln, re.I):
                m = re.search(r"\[([^\]]+)\]", ln)
                if m:
                    name = re.sub(r"\*|\(.*?\)", "", m.group(1)).strip()
                    todo.append({"id": "mem:" + name, "text": name[:60]})
    except OSError:
        pass
    ahead = _git("rev-list", "--count", "@{u}..HEAD")
    if ahead.isdigit() and int(ahead) > 0:
        todo.append({"id": "push:%s" % _git("rev-parse", "--short", "HEAD"),
                     "text": "Push %s GAYA commit%s (your go needed)" % (ahead, "s" * (int(ahead) > 1))})
    if os.path.exists(r"C:\Program Files\Coucou\coucou.exe"):
        todo.append({"id": "uninstall-coucou", "text": "Uninstall Coucou (admin prompt)"})
    return {"label": label, "done": done, "todo": todo[:10]}


def load_ticks():
    try:
        d = json.load(open(TODO, encoding="utf-8"))
    except Exception:
        d = {}
    return d.get("ticks", {})


def tick(item_id, on):
    ticks = load_ticks()
    if on:
        ticks[item_id] = time.time()
    else:
        ticks.pop(item_id, None)
    cutoff = time.time() - 7 * 86400                       # forget ticks after a week
    ticks = {k: v for k, v in ticks.items() if v > cutoff}
    os.makedirs(JDIR, exist_ok=True)
    json.dump({"ticks": ticks}, open(TODO, "w", encoding="utf-8"), indent=1)


class TodayView(QWidget):
    """Done list + tickable to-do list. Used by the boot card and the Deck."""

    def __init__(self, on_jump=None, compact=False):
        super().__init__()
        self.on_jump = on_jump
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(5)
        self.compact = compact

    def fill(self, data):
        while self.lay.count():
            it = self.lay.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
            elif it.layout():
                while it.layout().count():
                    w = it.layout().takeAt(0).widget()
                    if w:
                        w.deleteLater()
        ticks = load_ticks()
        h = QLabel("DONE %s" % data["label"].upper(), objectName="muted")
        h.setStyleSheet("letter-spacing: 1px; color:#8fd3ff;")
        self.lay.addWidget(h)
        if not data["done"]:
            self.lay.addWidget(QLabel("Nothing logged.", objectName="muted"))
        for title, sub in data["done"]:
            l = QLabel("✓  %s   <span style='color:#8c9098'>%s</span>"
                       % (title.replace("&", "&amp;").replace("<", "&lt;"), sub.replace("<", "&lt;")))
            l.setTextFormat(Qt.RichText)
            self.lay.addWidget(l)
        h2 = QLabel("TO DO", objectName="muted")
        h2.setStyleSheet("letter-spacing: 1px; color:#ffb020; margin-top:6px;")
        self.lay.addWidget(h2)
        if not data["todo"]:
            self.lay.addWidget(QLabel("All clear, Boss.", objectName="muted"))
        for item in data["todo"]:
            row = QHBoxLayout()
            b = QPushButton(("☑  " if item["id"] in ticks else "☐  ") + item["text"])
            b.setCheckable(True)
            b.setChecked(item["id"] in ticks)
            b.setStyleSheet("text-align:left; padding:6px 10px;" +
                            ("color:#6a6e76; text-decoration: line-through;" if item["id"] in ticks else ""))
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda on, item=item, b=b: self._tick(item, b, on))
            row.addWidget(b, 1)
            if item.get("sid") and self.on_jump:
                j = QPushButton("Open")
                j.setCursor(Qt.PointingHandCursor)
                j.clicked.connect(lambda _=False, sid=item["sid"]: self.on_jump(sid))
                row.addWidget(j)
            self.lay.addLayout(row)

    def _tick(self, item, b, on):
        tick(item["id"], on)
        b.setText(("☑  " if on else "☐  ") + item["text"])
        b.setStyleSheet("text-align:left; padding:6px 10px;" +
                        ("color:#6a6e76; text-decoration: line-through;" if on else ""))
