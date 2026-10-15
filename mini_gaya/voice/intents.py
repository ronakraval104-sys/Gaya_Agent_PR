"""What Boss said -> what J does.

Three lanes:
  DO      approval words (only while exactly one card is up) -> J commands -> routines
          (from ~/.jarvis/voice/routines.yaml, editable) -> "open <app>"
  CLAUDE  only by an explicit verb: "tell <session>: ..." / "ask claude ..." / "new session: ..."
  ASK     everything else is a conversation with J, answered from this PC (voice/brain.py)
          and spoken back. It never opens, types into or starts a Claude Code session.
"""
import os
import re
import subprocess
import time

import yaml

HOME = os.path.expanduser("~")
ROUTINES = os.path.join(HOME, ".jarvis", "voice", "routines.yaml")

DEFAULT_ROUTINES = """\
# Voice routines. Say any phrase in `say` and J runs the steps in order.
# step kinds:  app: <exe path> [args: [...]]   url: <https://...>   folder: <path>   say: <text>
work:
  say: ["prepare for work", "work mode", "let's work", "start work", "office mode"]
  steps:
    - say: "Preparing for work, Boss."
    - app: "D:/Microsoft VS Code/Code.exe"
      args: ["C:/Users/Ronak/Desktop/JARVIS"]
    - app: "C:/Program Files/Google/Chrome/Application/chrome.exe"
      args: ["--profile-directory=Profile 3"]          # VisualRhyme SUBS (katvisualrhyme@gmail.com)
    - folder: "C:/Users/Ronak/Desktop/Quote_PQM"
agency:
  say: ["agency mode", "katviz mode", "prepare for agency"]
  steps:
    - say: "Agency mode, Boss."
    - app: "C:/Program Files/Google/Chrome/Application/chrome.exe"
      args: ["--profile-directory=Profile 12"]         # katviz.ai
    - folder: "C:/Users/Ronak/Desktop/Katviz AI"
council:
  say: ["open the council", "stark council", "show me the council"]
  steps:
    - url: "http://localhost:4200"
"""

APPS = {
    "vs code": ("D:/Microsoft VS Code/Code.exe", []), "vscode": ("D:/Microsoft VS Code/Code.exe", []),
    "code": ("D:/Microsoft VS Code/Code.exe", []),
    "chrome": ("C:/Program Files/Google/Chrome/Application/chrome.exe", ["--profile-directory=Profile 3"]),
    "visual rhyme chrome": ("C:/Program Files/Google/Chrome/Application/chrome.exe", ["--profile-directory=Profile 3"]),
    "katviz chrome": ("C:/Program Files/Google/Chrome/Application/chrome.exe", ["--profile-directory=Profile 12"]),
    "whatsapp": ("shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App", []),
    "obsidian": (os.path.join(HOME, "Desktop", "Agents ;)", "Obsidian.lnk"), []),
    "comfy": (os.path.join(HOME, "Desktop", "Agents ;)", "ComfyUI.lnk"), []),
    "explorer": ("explorer.exe", []), "quotes": ("explorer.exe", [os.path.join(HOME, "Desktop", "Quote_PQM")]),
    "notepad": ("notepad.exe", []), "calculator": ("calc.exe", []),
}

APPROVE = {"allow": ("allow", "Allowed."), "approve": ("allow", "Allowed."), "yes allow": ("allow", "Allowed."),
           "go ahead": ("allow", "Allowed."), "deny": ("deny", "Denied."), "reject": ("deny", "Denied."),
           "no deny": ("deny", "Denied."), "terminal": ("terminal", "Handed back to Antigravity.")}


def load_routines():
    os.makedirs(os.path.dirname(ROUTINES), exist_ok=True)
    if not os.path.exists(ROUTINES):
        with open(ROUTINES, "w", encoding="utf-8") as f:
            f.write(DEFAULT_ROUTINES)
    try:
        return yaml.safe_load(open(ROUTINES, encoding="utf-8")) or {}
    except Exception:
        return {}


# how Whisper spells "Gaya" / "Mini Gaya" / "Jarvis"
VOC = r"(gaya|mini gaya|mini-gaya|gaia|guy-a|gya|guya|jarvis|jarvus|jarves|javis|jervis|mini j|j)"


def norm(t):
    t = t.lower().strip()
    t = re.sub(r"^(hey |ok |okay |yo )?" + VOC + r"\b[,.!]?\s*", "", t)      # "hey gaya, ..."
    t = re.sub(r"[,\s]+" + VOC + r"[.!?,]*$", "", t)                         # "..., gaya."
    t = re.sub(r"[^\w\s:']", "", t)
    return re.sub(r"\s+", " ", t).strip()


def greeting(t=""):
    if "night" in t:
        return "Good night, Ros. Rest well."
    h = time.localtime().tm_hour
    return "Good %s, Ros." % ("morning" if h < 12 else "afternoon" if h < 17 else "evening")


def launch(step):
    env = {k: v for k, v in os.environ.items() if k != "ELECTRON_RUN_AS_NODE" and not k.startswith("VSCODE_")}
    if "app" in step:
        exe = step["app"]
        args = [str(a) for a in step.get("args", [])]
        if exe.startswith("shell:") or exe.lower().endswith(".lnk"):
            os.startfile(exe)
        else:
            subprocess.Popen([exe] + args, env=env, creationflags=getattr(subprocess, "DETACHED_PROCESS", 0))
    elif "url" in step:
        os.startfile(step["url"])
    elif "folder" in step:
        os.startfile(step["folder"])


def route(text, pending_cards):
    """Returns (kind, payload, spoken_reply). kind in: approve, command, routine, open, tell, new, chat, none"""
    t = norm(text)
    if not t:
        if re.search(r"gaya|mini gaya|jarvis|mini j", text.lower()):           # just "Hey Gaya"
            return "command", ("greet", None), "Yes, Ros?"
        return "none", None, "I didn't catch that, Ros."
    words = t.split()
    # approvals - short utterance, exactly one card up, never "always" / "all" (one click, one card, by voice)
    if pending_cards == 1 and len(words) <= 3 and not {"always", "all", "everything", "forever"} & set(words):
        for phrase, (decision, reply) in APPROVE.items():
            if t == phrase or t.startswith(phrase + " ") or t.endswith(" " + phrase):
                return "approve", decision, reply
    # a greeting with anything after it: do the rest if it is a command, otherwise just greet back
    g = re.match(r"^(?:(?:good )?(?:morning|afternoon|evening|night)|hi|hello|hey)(?: there| boss)?\b[,.!]?\s*(.*)$", t)
    if g:
        rest = g.group(1).strip()
        if rest:
            k2, p2, r2 = route(rest, pending_cards)
            if k2 not in ("ask", "none"):
                return k2, p2, r2
        return "command", ("greet", g), greeting(t)
    # J commands
    cmds = [
        (r"^(open|show)( me)?( the)? deck$|^deck$", "deck", "Opening the deck."),
        (r"^(close|hide)( the)? deck$", "deck_close", ""),
        (r"^(show |what are (the )?|tell me (about )?(the )?|list )?(antigravity |gemini |cloud |cloude |claude )?sessions?$|^what('s| is) (waiting|pending)( on me)?$", "sessions", ""),
        (r"^(jump|go) (to|into) (.+)$", "jump", ""),
        (r"^(mute|quiet|shut up|silence)$", "mute", "Muted."),
        (r"^(unmute|speak|talk to me)$", "unmute", "Back, Ros."),
        (r"^(voice off|stop listening)$", "voice_off", "Voice off."),
        (r"^(come here|come to me)$", "come", "On it."),
        (r"^(go away|hide)$", "hide", ""),
        (r"^(roam|walk around)$", "roam", "Roaming."),
        (r"^(stay|stop roaming|stay put)$", "stay", "Staying."),
        (r"^(what time is it|what('s| is) the (time|date|day)|what day is it|time|date)$", "time", ""),
        (r"^(thank you|thanks|cheers)$", "thanks", "Anytime, Ros."),
        (r"^(run )?(security|agent ?shield)( scan)?$|^security audit$", "security", "Running AgentShield security scan."),
    ]
    for pat, kind, reply in cmds:
        m = re.match(pat, t)
        if m:
            return "command", (kind, m), greeting(t) if kind == "greet" and reply is None else reply
    # routines
    for name, r in load_routines().items():
        for phrase in r.get("say", []):
            if t == phrase.lower() or t.startswith(phrase.lower()):
                return "routine", (name, r), ""
    # open <app>
    m = re.match(r"^(open|launch|start) (.+)$", t)
    if m:
        want = m.group(2).strip()
        for name, (exe, args) in sorted(APPS.items(), key=lambda kv: -len(kv[0])):
            if want == name or want.startswith(name):
                return "open", (name, exe, args), "Opening %s." % name
        return "open", (want, None, None), "I don't know %s yet, Ros. Add it to the app list." % want
    # into an Antigravity session - only ever by an explicit verb
    m = re.match(r"^(ask|tell|send( this| it)? to) (antigravity|gaya|gemini|claude|jarvis)[:,]?\s+(.+)$", t)
    if m:
        return "tell", ("antigravity", m.group(4)), "Sent to Antigravity."
    m = re.match(r"^(tell|ask) (.+?)\s*[:,]\s*(.+)$", t)          # "tell all docs: print it"
    if m and len(m.group(2).split()) <= 3:
        return "tell", (m.group(2), m.group(3)), "Sent."
    m = re.match(r"^(tell|ask) (.+?) (to|that) (.+)$", t)          # "tell all docs to print it"
    if m and len(m.group(2).split()) <= 3:
        return "tell", (m.group(2), m.group(4)), "Sent."
    m = re.match(r"^new (session|chat)[:,]? (.+)$", t)
    if m:
        return "new", m.group(2), "Starting a new session."
    # everything else is a conversation with J, answered from this PC. Never a new session.
    return "ask", t, ""
