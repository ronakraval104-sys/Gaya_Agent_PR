"""What is Gaya / Antigravity doing right now?
Reads live from Google Antigravity session transcripts with fallback to legacy .jarvis events.

    python gaya_state.py          -> JSON  {"state": ..., "detail": ..., "source": ...}
    python gaya_state.py --line   -> one status-line string

States: broken > hold > approved > spawning > thinking > idle > asleep
"""
import glob
import json
import os
import sys
import time
from datetime import datetime

USER_HOME = os.path.expanduser("~")
G = os.path.join(USER_HOME, ".gaya")
J = G if os.path.exists(G) else os.path.join(USER_HOME, ".jarvis")
LEGACY_LOG = os.path.join(J, "logs", "events.jsonl")
BRAIN_DIR = os.path.join(USER_HOME, ".gemini", "antigravity", "brain")

GLYPH = {
    "idle": "◆",
    "thinking": "◇",
    "spawning": "❖",
    "hold": "◈",
    "broken": "✖",
    "approved": "✔",
    "asleep": "·",
}
ANSI = {
    "idle": "97",
    "thinking": "96",
    "spawning": "96",
    "hold": "33",
    "broken": "31",
    "approved": "32",
    "asleep": "90",
}


def get_active_transcript_path():
    """Find the most recently updated Antigravity session transcript."""
    try:
        if not os.path.isdir(BRAIN_DIR):
            return None
        transcripts = glob.glob(
            os.path.join(BRAIN_DIR, "*", ".system_generated", "logs", "transcript.jsonl")
        )
        if not transcripts:
            return None
        transcripts.sort(key=os.path.getmtime, reverse=True)
        return transcripts[0]
    except Exception:
        return None


def get_active_log_path():
    """Returns live Antigravity transcript if active, otherwise legacy .jarvis log."""
    t_path = get_active_transcript_path()
    if t_path and os.path.exists(t_path):
        age_s = time.time() - os.path.getmtime(t_path)
        if age_s < 600:
            return t_path
    return LEGACY_LOG


# Legacy tail
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


def get_antigravity_state():
    """Extract live state from the most recent Antigravity session transcript."""
    t_path = get_active_transcript_path()
    if not t_path or not os.path.exists(t_path):
        return None

    mtime = os.path.getmtime(t_path)
    now = time.time()
    file_age = now - mtime
    if file_age > 600:
        return None

    # Read tail of transcript
    steps = tail(t_path, n=20)
    if not steps:
        return {
            "state": "idle",
            "detail": "Antigravity standing by",
            "armed": "PASS",
            "holds_today": 0,
            "source": "antigravity",
            "last_active_ago": int(file_age),
        }

    last_step = steps[-1]
    step_ts = last_step.get("created_at")
    step_age = file_age
    if step_ts:
        try:
            clean_ts = step_ts.split("+")[0].strip().replace("Z", "")
            dt = datetime.fromisoformat(clean_ts)
            step_age = max(0, time.time() - dt.timestamp())
        except Exception:
            pass

    # Inspect the recent steps within 45 seconds for active states
    state = "idle"
    detail = "Antigravity standing by"
    active_tool = None

    if step_age < 45 or file_age < 25:
        for s in reversed(steps[-6:]):
            content = str(s.get("content", ""))
            tool_calls = s.get("tool_calls") or []

            if "[🛡️ LOGOS]" in content and "PASS" in content:
                state = "approved"
                detail = "🛡️ LOGOS: PASS Gate Verified"
                break

            if tool_calls and isinstance(tool_calls, list):
                tc = tool_calls[0]
                t_name = tc.get("name", "tool")
                args = tc.get("args") or {}
                t_summary = args.get("toolSummary") or args.get("toolAction") or t_name
                active_tool = t_name

                if t_name == "ask_question":
                    state = "hold"
                    detail = f"Awaiting input: {t_summary}"
                    break
                elif t_name == "invoke_subagent":
                    state = "spawning"
                    detail = f"Subagents active: {t_summary}"
                    break
                else:
                    state = "thinking"
                    detail = f"{t_summary}"
                    break

            if s.get("type") == "PLANNER_RESPONSE":
                state = "thinking"
                detail = "Deep thinking & planning"
                break
    elif file_age < 600:
        state = "idle"
        mins = int(file_age // 60)
        detail = f"Antigravity standing by ({mins}m ago)" if mins > 0 else "Antigravity standing by"
    else:
        state = "asleep"
        detail = "No recent session activity"

    sid = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(t_path))))
    return {
        "state": state,
        "detail": detail,
        "armed": "PASS",
        "holds_today": 0,
        "active_tool": active_tool,
        "step_index": last_step.get("step_index", 0),
        "session_id": sid,
        "last_active_ago": int(min(file_age, step_age)),
        "source": "antigravity",
    }


def current():
    """Return unified live state: prioritizes active Antigravity session."""
    # 1. Check live Antigravity first
    agy = get_antigravity_state()
    if agy and agy["state"] != "asleep":
        return agy

    # 2. Legacy .jarvis fallback
    now = datetime.now()
    status = ""
    try:
        with open(os.path.join(J, "STATUS")) as f:
            status = f.read().strip()
    except OSError:
        pass
    evs = tail(LEGACY_LOG)
    holds_today = sum(
        1
        for e in evs
        if e.get("ev") == "guard" and str(e.get("ts", "")).startswith(now.strftime("%Y-%m-%d"))
    )
    base = {
        "armed": status.split(" ")[0] if status else "?",
        "holds_today": holds_today,
        "source": "legacy",
    }

    if os.path.exists(os.path.join(J, "DISABLED")):
        return dict(base, state="broken", detail="guard disabled")
    if status.startswith("BROKEN"):
        return dict(base, state="broken", detail=status)
    for e in reversed(evs):
        a = age(e, now)
        if a > 600:
            break
        if e.get("ev") == "guard" and a < 25:
            return dict(
                base,
                state="hold",
                detail="%s: %s" % (e.get("decision"), (e.get("reason") or "")[:60]),
            )
        if (
            e.get("ev") == "subagent_stop"
            and (e.get("agent") in ("edidth", "logos"))
            and e.get("verdict") == "PASS"
            and a < 15
        ):
            return dict(base, state="approved", detail="LOGOS PASS")
    recent = [e for e in evs if age(e, now) < 25]
    if any(e.get("agent") not in (None, "main") for e in recent if e.get("ev") == "tool"):
        return dict(base, state="spawning", detail="subagents working")
    if recent:
        last = recent[-1]
        return dict(base, state="thinking", detail="%s" % (last.get("tool") or last.get("ev")))
    if evs and age(evs[-1], now) < 600:
        return dict(base, state="idle", detail="standing by")

    # If Antigravity was detected but in standby
    if agy:
        return agy

    return dict(base, state="asleep", detail="no session activity")


# Backwards compatibility export
LOG = LEGACY_LOG

if __name__ == "__main__":
    s = current()
    if "--line" in sys.argv:
        sys.stdout.reconfigure(encoding="utf-8")
        glyph = GLYPH.get(s["state"], "·")
        ansi_code = ANSI.get(s["state"], "90")
        print(
            "\033[%sm%s GAYA\033[0m · %s · %s · %s"
            % (ansi_code, glyph, s["armed"], s["state"], s.get("detail", ""))
        )
    else:
        print(json.dumps(s, indent=2))
