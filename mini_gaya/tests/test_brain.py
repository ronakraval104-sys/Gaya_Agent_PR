"""J's brain against the real memory directory and kb (read-only).   python tests/test_brain.py"""
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "voice"))
import brain  # noqa: E402

ROWS = [
    {"title": "all docs", "status": "working", "live": True, "sid": "a1", "prompt_full": "print the Whiteland quote"},
    {"title": "JARVIS", "status": "waiting", "live": True, "sid": "b2"},
    {"title": "old one", "status": "closed", "live": False, "sid": "c3"},
]

CASES = [  # (question, regex the spoken answer must match)
    ("who are you", r"Mini Gaya|JARVIS"),
    ("what's happening", r"2 Antigravity sessions open.*all docs is working.*JARVIS is waiting"),
    ("status", r"sessions open"),
    ("what did we do on laxcon", r"(?i)laxcon|don't have that in memory"),
    ("what did we do on laxcan", r"(?i)laxcon|don't have that in memory"),                  # Whisper's spelling
    ("where are we on the whiteland room", r"(?i)whiteland|don't have that in memory"),
    ("tell me about the audit kit", r"(?i)audit kit|don't have that in memory"),
    ("what's pending on the power calc doc", r"(?i)power calc|resume|not built|don't have that in memory"),
    ("give me edidth's last report", r"(?i)edith|no report"),
    ("what did veronica say", r"(?i)veronica"),
    ("what did we do today", r"(?i)ros|boss|yesterday|today"),
    ("what's on my list", r"(?i)list|pending"),
    ("what's the weather in rajkot", r"(?i)don't have that in memory|via (ollama|lmstudio)|closest i have"),
]

fails = 0
for q, pat in CASES:
    t0 = time.time()
    reply, detail = brain.answer(q, ROWS)
    ms = (time.time() - t0) * 1000
    ok = bool(re.search(pat, reply)) and len(reply) <= 460 and "\\" not in reply and "`" not in reply
    fails += not ok
    print("%s %4.0f ms %-42r -> %r%s" % ("ok  " if ok else "FAIL", ms, q, reply[:150], (" [%s]" % detail[:40]) if detail else ""))
print("\n%d/%d pass" % (len(CASES) - fails, len(CASES)))
sys.exit(1 if fails else 0)
