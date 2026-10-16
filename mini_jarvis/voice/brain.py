"""J's own brain: answers Boss from what is already on this PC. No Claude session, no network.

Sources, all read-only:
  - the live session registry (rows the sprite already holds)
  - the morning-brief gatherer (what got done, what is pending)
  - subagent reports in ~/.jarvis/kb/<date>/HHMMSS-<agent>-<sid>.md
  - the memory directory (~/.claude/projects/C--Users-Ronak/memory) and its MEMORY.md index
Tier 2, optional: a local LLM behind Ollama (:11434) or LM Studio (:1234) gets the same
facts as context and phrases the answer in J's voice. Probed, never required.

answer(question, rows) -> (spoken reply, detail for the toast). Nothing here opens, types
into or starts a Claude Code session.
"""
import datetime as dt
import difflib
import glob
import json
import os
import re
import sys
import time
import urllib.request

HOME = os.path.expanduser("~")
MEM_DIR = os.path.join(HOME, ".claude", "projects", "C--Users-Ronak", "memory")
MEM_INDEX = os.path.join(MEM_DIR, "MEMORY.md")
KB = os.path.join(HOME, ".jarvis", "kb")
BRAIN_CFG = os.path.join(HOME, ".jarvis", "voice", "brain.json")      # {"model": "...", "endpoint": "..."}
AGENTS = {"edidth": "Edith", "edith": "Edith", "veronica": "Veronica", "friday": "Friday",
          "dum-e": "Dum-E", "dume": "Dum-E", "dummy": "Dum-E"}
AGENT_FILE = {"edith": "edidth", "dummy": "dum-e", "dume": "dum-e"}

_STOP = set("""what did we do on the a an of is are was were about status where how in for me tell give update
report last latest any with to from our my it its that this and or case project at up going happening been
have has you your i am be there here now today yesterday please jarvis boss j""".split())

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------- text helpers
def tokens(s):
    return [w for w in re.findall(r"[a-z0-9][a-z0-9&'.-]*", s.lower()) if w not in _STOP and len(w) > 1]


def speakable(s, n=360):
    """Markdown / paths / symbols -> something Kokoro can read without sounding like a terminal."""
    s = re.sub(r"[\x00-\x1f]", " ", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"`[^`]*`", "", s)
    s = re.sub(r"\S*[\\/]\S*", "", s)                         # file paths
    s = re.sub(r"\*+|_{2,}|#+\s?", "", s)
    s = s.replace("→", " to ").replace("·", ", ").replace("—", ", ").replace("–", ", ").replace("₹", "rupees ")
    s = re.sub(r"(\d)L\b", r"\1 lakh", s)
    s = re.sub(r"\bCr\b", "crore", s)
    s = re.sub(r"\s+", " ", s).strip(" ,;:")
    if len(s) > n:
        cut = s[:n]
        s = cut[:max(cut.rfind(". "), cut.rfind(", "), n - 60)].rstrip(" ,.") + "."
    return s


def two_sentences(s, n=360):
    parts = re.split(r"(?<=[.!?])\s+", s.strip())
    return speakable(" ".join(parts[:2]), n)


def _join(names):
    names = [n[:40] for n in names]
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


def _when(day, hhmmss=""):
    today = dt.date.today()
    try:
        d = dt.date.fromisoformat(day)
    except ValueError:
        return day
    t = ""
    if len(hhmmss) >= 4:
        t = " at %s" % dt.datetime.strptime(hhmmss[:4], "%H%M").strftime("%I:%M %p").lstrip("0")
    if d == today:
        return "today" + t
    if d == today - dt.timedelta(days=1):
        return "yesterday" + t
    return "on %s %s" % (d.day, d.strftime("%B")) + t


# ---------------------------------------------------------------- memory
_mem = {"mtime": None, "entries": []}


def memory_index():
    try:
        mtime = os.path.getmtime(MEM_INDEX)
    except OSError:
        return []
    if _mem["mtime"] == mtime:
        return _mem["entries"]
    entries = []
    pat = re.compile(r"^\s*-\s*(?:[^\[]*?)\[([^\]]+)\]\(([^)]+)\)\**\s*[—–-]+\s*(.*)$")   # bold entries too
    for ln in open(MEM_INDEX, encoding="utf-8"):
        m = pat.match(ln)
        if not m:
            continue
        title = re.sub(r"\*+", "", m.group(1)).strip()
        fname, hook = m.group(2).strip(), m.group(3).strip()
        stem = re.sub(r"^(project|reference|feedback|user)_", "", fname.replace(".md", ""))
        entries.append({"title": title, "file": fname, "hook": hook,
                        "words": set(tokens(title + " " + stem.replace("_", " ").replace("-", " ") + " " + hook)),
                        "twords": set(tokens(title + " " + stem.replace("_", " ")))})
    _mem.update(mtime=mtime, entries=entries)
    return entries


def memory_search(query, k=3):
    """[(score, entry, coverage)] - coverage = share of the question's words the entry accounts for."""
    q = tokens(query)
    if not q:
        return []
    scored = []
    for e in memory_index():
        score, hit = 0.0, 0
        for w in q:
            if w in e["words"]:
                score += 2 + (1 if w in e["twords"] else 0)
                hit += 1
            else:
                close = difflib.get_close_matches(w, e["words"], n=1, cutoff=0.8)   # laxcan -> laxcon
                if close:
                    score += 1.5 + (0.5 if close[0] in e["twords"] else 0)
                    hit += 1
        if score:
            scored.append((score, e, hit / len(q)))
    scored.sort(key=lambda x: -x[0])
    return scored[:k]


def memory_body(fname, n=700):
    try:
        s = open(os.path.join(MEM_DIR, fname), encoding="utf-8").read()
    except OSError:
        return "", ""
    mod = re.search(r"modified:\s*(\d{4}-\d{2}-\d{2})", s)
    body = re.sub(r"^---.*?---\s*", "", s, count=1, flags=re.S)
    return body[:n], (mod.group(1) if mod else "")


# ---------------------------------------------------------------- subagent reports
def agent_report(agent):
    agent = AGENT_FILE.get(agent, agent)
    files = sorted(glob.glob(os.path.join(KB, "*", "*-%s-*.md" % agent)))
    if not files:
        return None, ""
    f = files[-1]
    try:
        lines = open(f, encoding="utf-8").read().splitlines()
    except OSError:
        return None, ""
    para, started = [], False
    for ln in lines:
        s = ln.strip()
        if not started and (not s or s.startswith("#") or s.startswith("session:") or s.startswith("source:")):
            continue
        started = True
        if not s:
            if para:
                break
            continue
        para.append(s)
    verdict = two_sentences(" ".join(para)) or "an empty report"
    verdict = re.sub(r"^\[?%s\]?[:\s]*" % re.escape(agent.upper()), "", verdict, flags=re.I)
    day = os.path.basename(os.path.dirname(f))
    hhmmss = os.path.basename(f).split("-")[0]
    return "%s's last report, %s: %s" % (AGENTS.get(agent, agent.title()), _when(day, hhmmss), verdict), f


# ---------------------------------------------------------------- sessions
def sessions_summary(rows):
    live = [r for r in rows if r.get("live", True) and r.get("status") != "closed"]
    if not live:
        return "No Antigravity sessions are open right now, Ros."
    working = [r for r in live if r.get("status") == "working"]
    waiting = [r.get("title", "an Antigravity session") for r in live if r.get("status") == "waiting"]
    idle = [r for r in live if r.get("status") == "idle"]
    parts = ["%d Antigravity session%s open" % (len(live), "s" * (len(live) != 1))]
    if working:
        names = [r.get("title", "an Antigravity session") for r in working]
        s = "%s %s working" % (_join(names), "is" if len(names) == 1 else "are")
        if len(working) == 1 and working[0].get("prompt_full"):
            s += " on: %s" % speakable(" ".join(str(working[0]["prompt_full"]).split()[:14]), 120)
        parts.append(s)
    if waiting:
        parts.append("%s %s waiting for you" % (_join(waiting), "is" if len(waiting) == 1 else "are"))
    if idle:
        parts.append("%d idle" % len(idle))
    return "Ros, " + "; ".join(parts) + "."


def brief(rows, what):
    import sprite_brief
    g = sprite_brief.gather([dict(r, id=r.get("id", r.get("sid", ""))) for r in rows])
    if what == "done":
        if not g["done"]:
            return "Nothing logged for %s yet, Ros." % g["label"].lower()
        items = ["%s (%s)" % (a, b) for a, b in g["done"][:5]]
        return speakable("%s, Ros: %s." % (g["label"], "; ".join(items)), 420)
    todo = g["todo"]
    if not todo:
        return "Nothing pending on your list, Ros."
    return speakable("%d thing%s on your list, Ros: %s." % (len(todo), "s" * (len(todo) != 1),
                                                           "; ".join(t["text"] for t in todo[:5])), 420)


# ---------------------------------------------------------------- tier 2: a local LLM, if one is running
_ep = {"t": 0.0, "kind": None, "url": None}


def cfg():
    try:
        return json.load(open(BRAIN_CFG, encoding="utf-8"))
    except Exception:
        return {}


def llm_endpoint():
    if time.time() - _ep["t"] < 60:
        return _ep["kind"], _ep["url"]
    _ep["t"] = time.time()
    _ep.update(kind=None, url=None)
    probes = [("ollama", "http://127.0.0.1:11434", "/api/tags"), ("lmstudio", "http://127.0.0.1:1234", "/v1/models")]
    c = cfg()
    if c.get("endpoint"):
        probes.insert(0, (c.get("kind", "openai"), c["endpoint"].rstrip("/"), "/v1/models"))
    for kind, url, path in probes:
        try:
            urllib.request.urlopen(url + path, timeout=0.3).read()
            _ep.update(kind=kind, url=url)
            break
        except Exception:
            continue
    return _ep["kind"], _ep["url"]


SYSTEM = ("You are Mini Gaya, Ros's Divine Commander and desktop companion. Answer in one or two short spoken sentences, "
          "using only the CONTEXT. If the context does not have it, say you don't have it in memory. "
          "Call him Ros. No markdown, no lists, no file paths.")


def llm_answer(question, context):
    kind, url = llm_endpoint()
    if not url:
        return None, ""
    model = cfg().get("model") or ("qwen3:4b" if kind == "ollama" else "")
    msgs = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": "CONTEXT:\n%s\n\nQUESTION: %s" % (context, question)}]
    try:
        if kind == "ollama":
            body = {"model": model, "messages": msgs, "stream": False, "think": False,
                    "options": {"num_predict": 120, "temperature": 0.4}}
            req = urllib.request.Request(url + "/api/chat", json.dumps(body).encode(),
                                         {"Content-Type": "application/json"})
            out = json.load(urllib.request.urlopen(req, timeout=25))["message"]["content"]
        else:
            if not model:
                models = json.load(urllib.request.urlopen(url + "/v1/models", timeout=2)).get("data", [])
                model = models[0]["id"] if models else ""
            body = {"model": model, "messages": msgs, "max_tokens": 120, "temperature": 0.4}
            req = urllib.request.Request(url + "/v1/chat/completions", json.dumps(body).encode(),
                                         {"Content-Type": "application/json"})
            out = json.load(urllib.request.urlopen(req, timeout=25))["choices"][0]["message"]["content"]
    except Exception as e:
        return None, "%s failed: %s" % (kind, str(e)[:80])
    out = re.sub(r"<think>.*?</think>", "", out, flags=re.S)
    return two_sentences(out, 400), "via %s %s" % (kind, model)


def context_for(question, rows):
    ctx = ["Time: %s" % time.strftime("%A %d %B %Y, %I:%M %p"), "Sessions: " + sessions_summary(rows)]
    for score, e, _cov in memory_search(question, 3):
        body, mod = memory_body(e["file"], 600)
        ctx.append("Memory [%s]%s: %s\n%s" % (e["title"], (" (updated %s)" % mod) if mod else "", e["hook"], body))
    for a in ("edidth", "veronica", "friday"):
        r, _ = agent_report(a)
        if r:
            ctx.append(r)
    return "\n\n".join(ctx)[:6000]


# ---------------------------------------------------------------- the one entry point
PERSONA = [
    (r"^(who|what) are you\b", "I'm JARVIS, Ros. Your AI desktop companion: I monitor the sessions, "
                               "assist the council, and keep systems aligned."),
    (r"^(how are you|you (there|good|okay|ok)|are you (there|up|online|awake))\b",
     "JARVIS systems online and fully operational, Ros. Listening."),
    (r"^(what can you do|help( me)?|what do you do)\b",
     "Commands, routines, approvals, and questions about this PC: the sessions, today's work, "
     "subagent reports, and any case in memory. Say 'ask Antigravity' to hand something to a session."),
]
STATUS = (r"^(what('s| is) (happening|going on|up|the status)|status( report)?|sitrep|what are (you|we) (doing|working on)|"
          r"how('s| is) it going|where are we|what are the (antigravity |gemini |cloud |cloude |claude )?sessions?|"
          r"(antigravity |gemini |cloud |cloude |claude )?sessions( status)?)( right now| now| today)?$")          # whole phrase only: "where are we on X" is a case
DONE = r"^(what (did|have) (we|you) (do|done|get done)|what('s| was| has been) done|recap|summary|what happened)( today| yesterday| so far| this morning| this week)?$"
TODO = r"^(what('s| is) (pending|on my (list|plate)|left|open|next)|(my )?to ?do( list)?|what do i (need|have) to do( today)?)$"
AGENT = r"\b(logos|bob|freya|tvashtar|edidth|veronica|friday|dum-?e)\b"
NOT_LOCAL = r"\b(weather|forecast|temperature outside|news|headlines|stock|share price|exchange rate|translate|define|definition of|capital of|wikipedia|who is the (president|prime minister)|how (tall|old|far) is)\b"
CASE_LEAD = (r"^(what('s| is| was) (the )?(status|latest|update|news)( of| on| with| about)?|where are we( on| with)?|"
             r"what (did|have) we (do|done)( on| with| about| for)?|what happened( with| to| on)?|tell me about|"
             r"update me on|brief me on|what about|remind me (of|about)|how('s| is) (the )?|catch me up on|"
             r"what('s| is) (pending|open|left|next)( on| with| for)?|anything (on|about))\s+")


def answer(question, rows=()):
    t = re.sub(r"[^\w\s:'-]", "", question.lower()).strip()
    t = re.sub(r"\s+", " ", t)
    rows = list(rows or [])
    for pat, reply in PERSONA:
        if re.search(pat, t):
            return reply, ""
    if re.match(STATUS, t):
        return sessions_summary(rows), ""
    if re.match(DONE, t):
        return brief(rows, "done"), ""
    if re.match(TODO, t):
        return brief(rows, "todo"), ""
    m = re.search(AGENT, t)
    if m and re.search(r"report|say|said|verdict|find|found|last|result|pass|fail|review", t):
        r, f = agent_report(m.group(1).replace("dum e", "dum-e"))
        if r:
            return r, f
        return "I have no report from %s on file, Ros." % AGENTS.get(m.group(1), m.group(1).title()), ""
    # a case / project / client by name
    lead = re.match(CASE_LEAD, t)
    subject = t[lead.end():] if lead else t
    subject = re.sub(r"^(the|our|that|this)\s+", "", subject).strip(" ?")
    world = re.search(NOT_LOCAL, t)                       # weather / news / general knowledge: not in memory
    hits = memory_search(subject) if subject and not world else []
    if hits and hits[0][2] >= 0.6 and (hits[0][0] >= 3 or (lead and hits[0][0] >= 1.5)):
        e = hits[0][1]
        _, mod = memory_body(e["file"], 10)
        if re.search(r"\b(pending|open|left|next|remaining|outstanding)\b", t):
            m2 = re.search(r"\b(open|next|pending|awaiting|todo|resume here)\b\s*[:=]?\s*([^;]+)", e["hook"], re.I)
            if m2:
                return speakable("Open on %s: %s." % (e["title"], m2.group(2)), 360), e["file"]
        when = (" Last touched %s." % _when(mod)) if mod else ""
        return speakable("%s: %s.%s" % (e["title"], e["hook"], when), 400), e["file"]
    # tier 2
    reply, detail = llm_answer(question, context_for(question, rows))
    if reply:
        return reply, detail
    if hits and hits[0][2] >= 0.5:                       # weak match: offer it rather than nothing
        e = hits[0][1]
        return speakable("Closest I have is %s: %s." % (e["title"], e["hook"]), 360), e["file"]
    return ("I don't have that in memory, Ros. Say 'ask Antigravity' and I'll hand it to the Gaya session.",
            detail or "no local LLM running (Ollama :11434 / LM Studio :1234)")
