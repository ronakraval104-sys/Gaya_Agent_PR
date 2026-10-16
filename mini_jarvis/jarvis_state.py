"""What is JARVIS doing right now? Read from the v10 event log.

    python jarvis_state.py          -> JSON  {"state": ..., "detail": ...}
    python jarvis_state.py --line   -> one status-line string

States: broken > hold > approved > spawning > thinking > idle > asleep
"""
import json
import os
import sys
from datetime import datetime

J = os.path.join(os.path.expanduser("~"), ".jarvis")
LOG = os.path.join(J, "logs", "events.jsonl")


def tail(path, n=400):
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 200_000))
            lines = f.read().decode("utf-8", "replace").splitlines()[-n:]
    except OSError:
        return []
    out = []
    for ln in lines:
        try:
            out.append(json.loads(ln))
        except ValueError:
            pass
    return out


def age(ev, now):
    try:
        return (now - datetime.fromisoformat(ev["ts"]).replace(tzinfo=None)).total_seconds()
    except Exception:
        return 1e9


def current():
    now = datetime.now()
    status = ""
    try:
        status = open(os.path.join(J, "STATUS")).read().strip()
    except OSError:
        pass
    evs = tail(LOG)
    holds_today = sum(1 for e in evs if e.get("ev") == "guard"
                      and str(e.get("ts", "")).startswith(now.strftime("%Y-%m-%d")))
    base = {"armed": status.split(" ")[0] if status else "?", "holds_today": holds_today}

    if os.path.exists(os.path.join(J, "DISABLED")):
        return dict(base, state="broken", detail="guard disabled")
    if status.startswith("BROKEN"):
        return dict(base, state="broken", detail=status)
    for e in reversed(evs):
        a = age(e, now)
        if a > 600:
            break
        if e.get("ev") == "guard" and a < 25:
            return dict(base, state="hold", detail="%s: %s" % (e.get("decision"), (e.get("reason") or "")[:60]))
        if e.get("ev") == "subagent_stop" and e.get("agent") == "edidth" and e.get("verdict") == "PASS" and a < 15:
            return dict(base, state="approved", detail="EDIDTH PASS")
    recent = [e for e in evs if age(e, now) < 25]
    if any(e.get("agent") not in (None, "main") for e in recent if e.get("ev") == "tool"):
        return dict(base, state="spawning", detail="subagents working")
    if recent:
        last = recent[-1]
        return dict(base, state="thinking", detail="%s" % (last.get("tool") or last.get("ev")))
    if evs and age(evs[-1], now) < 600:
        return dict(base, state="idle", detail="standing by")
    return dict(base, state="asleep", detail="no session activity")


GLYPH = {"idle": "◆", "thinking": "◇", "spawning": "❖", "hold": "◈", "broken": "✖",
         "approved": "✔", "asleep": "·"}
ANSI = {"idle": "97", "thinking": "96", "spawning": "96", "hold": "33", "broken": "31",
        "approved": "32", "asleep": "90"}

if __name__ == "__main__":
    s = current()
    if "--line" in sys.argv:
        sys.stdout.reconfigure(encoding="utf-8")
        print("\033[%sm%s JARVIS\033[0m · %s · %s · %d holds today"
              % (ANSI[s["state"]], GLYPH[s["state"]], s["armed"], s["state"], s["holds_today"]))
    else:
        print(json.dumps(s))
