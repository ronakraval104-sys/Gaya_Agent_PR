"""Router only (no Qt, no mic): what Boss said -> which lane.   python tests/test_intents.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "voice"))
import intents  # noqa: E402

SILENT = {"deck_close", "sessions", "jump", "hide", "time", "greet"}   # reply comes from the handler

CASES = [  # (heard, pending cards, expected kind, expected payload head)
    # greetings - with the name mangled, with extra words, with a command after
    ("Hey Jarvis.", 0, "command", "greet"),
    ("Hello, Jols.", 0, "command", "greet"),                 # 15 Oct 11:41 - Whisper's "Jarvis"
    ("Good morning, toast.", 0, "command", "greet"),         # 15 Oct 11:41
    ("Good morning down the street.", 0, "command", "greet"),  # 15 Oct 11:59 - this one opened a session
    ("Good morning, Jarvis", 0, "command", "greet"),
    ("good night j", 0, "command", "greet"),
    ("hey open the deck", 0, "command", "deck"),
    ("good morning jarvis what's waiting on me", 0, "command", "sessions"),
    ("Thanks, J.", 0, "command", "thanks"),
    # J commands
    ("Jarvis, what time is it?", 0, "command", "time"),
    ("what's the date", 0, "command", "time"),
    ("open the deck, jarvis", 0, "command", "deck"),
    ("what is waiting on me", 0, "command", "sessions"),
    ("jump to all docs", 0, "command", "jump"),
    ("hide", 0, "command", "hide"),
    # routines / apps
    ("jarvis prepare for work", 0, "routine", "work"),
    ("open katviz chrome", 0, "open", "katviz chrome"),
    ("open vs code", 0, "open", "vs code"),
    # approvals - one card, short, never always/all
    ("allow", 1, "approve", "allow"),
    ("yes allow", 1, "approve", "allow"),
    ("deny", 1, "approve", "deny"),
    ("allow", 0, "ask", "allow"),                             # no card up -> a question for J, not an approval
    ("allow", 2, "ask", "allow"),                             # two cards -> never guess
    ("always allow", 1, "ask", "always allow"),               # never "always" by voice
    ("allow all", 1, "ask", "allow all"),
    # into Claude Code - explicit verbs only
    ("tell all docs: print it", 0, "tell", "all docs"),
    ("tell all docs to print it", 0, "tell", "all docs"),
    ("ask claude: what is the microtronix gstin", 0, "tell", "antigravity"),
    ("send this to jarvis rebuild the quote", 0, "tell", "antigravity"),
    ("new session: audit the kit", 0, "new", "audit the kit"),
    # conversation with J - answered locally, never a session
    ("what did we do on laxcon", 0, "ask", "what did we do on laxcon"),
    ("give me edidth's last report", 0, "ask", "give me edidth's last report"),
    ("what's happening", 0, "ask", "what's happening"),
    ("who are you", 0, "ask", "who are you"),
    ("", 0, "none", None),
]


def head_of(payload):
    return payload[0] if isinstance(payload, tuple) else payload


fails = 0
for heard, cards, kind, head in CASES:
    k, payload, reply = intents.route(heard, cards)
    got = head_of(payload)
    ok = k == kind and (head is None or got == head or (isinstance(got, str) and got.startswith(head)))
    if ok and k == "command" and got not in SILENT:
        ok = bool(reply)                                      # a command Boss can hear back
    if ok and k == "command" and got == "greet":
        ok = reply.startswith(("Good ", "Yes, Ros", "Yes, Boss", "Yes, R0n"))
    if ok and k == "ask":
        ok = reply == ""                                      # the brain speaks, not the router
    fails += not ok
    print("%s %-42r cards=%d -> %-8s %-16r %r" % ("ok  " if ok else "FAIL", heard, cards, k, got, reply))
print("\n%d/%d pass" % (len(CASES) - fails, len(CASES)))
sys.exit(1 if fails else 0)
