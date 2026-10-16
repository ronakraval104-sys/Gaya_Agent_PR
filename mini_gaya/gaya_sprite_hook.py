#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gaya_sprite_hook.py - relays Claude Code hook events to the GAYA sprite.

Wired for: PermissionRequest (blocking, waits for Boss's click) and the
lifecycle events SessionStart, UserPromptSubmit, Notification, Stop,
StopFailure, SubagentStart, SessionEnd (fire-and-forget).

THE RULE (same as Coucou's): nothing is ever allowed without a decision a
human clicked. No sprite running, no proof of key, no ack within 0.8 s, a bad
signature, a timeout, garbage, or any error -> print nothing, exit 0 ->
Claude Code asks in its own terminal exactly as if GAYA did not exist.

Handshake (EDIDTH 2026-10-12): the hook says hello {id, auth}; the sprite must
answer {ready: HMAC} BEFORE the hook sends a single byte of the payload, so a
program squatting the port never sees prompts or commands.

"Always" echoes ONLY Claude Code's own `addRules` + `allow` suggestions whose
rules are specific (no whole-tool rule unless mcp__*, no "*" / ":*"); never
setMode. Answers to AskUserQuestion are validated against the questions
asked, and are covered by the decision signature.
"""

import hashlib
import hmac
import json
import os
import socket
import sys
import time
import uuid

GDIR = os.path.join(os.path.expanduser("~"), ".gaya")
JDIR = GDIR if os.path.exists(GDIR) else os.path.join(os.path.expanduser("~"), ".jarvis")
KEYFILE = os.path.join(JDIR, "secrets", "sprite.key")
PORT = 8767
CONNECT_S = 0.3
ACK_S = 0.8
DECIDE_S = 108
CAP = 2000


def sig(key, *parts):
    return hmac.new(key, "|".join(parts).encode(), hashlib.sha256).hexdigest()


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


FULL_KEYS = ("command",)                                  # shown whole on the card (scrollable)
PREVIEW_KEYS = ("content", "new_string", "old_string", "new_source")   # card shows a preview + size
PREVIEW = 400


def trim(v, flag, top=False, key=None, sizes=None):
    """Display copy for the sprite. Marks anything it had to cut that the card
    needs in full. File bodies are previews by design (the card prints the real
    size from `sizes`), so cutting them never locks Allow. Only the TOP-LEVEL
    tool_response/tool_output are dropped - a key of that name inside tool_input
    (e.g. an MCP argument) is shown like any other (EDIDTH r3)."""
    if isinstance(v, str):
        if key in PREVIEW_KEYS:
            if len(v) > PREVIEW:
                if sizes is not None:
                    sizes[key] = len(v)
                return v[:PREVIEW]
            return v
        limit = 60000 if key in FULL_KEYS else CAP
        if len(v) > limit:
            flag["cut"] = True
            return v[:limit]
        return v
    if isinstance(v, dict):
        if len(v) > 60:
            flag["cut"] = True
        return {k: trim(x, flag, key=k, sizes=sizes) for k, x in list(v.items())[:60]
                if not (top and k in ("tool_response", "tool_output"))}
    if isinstance(v, list):
        if len(v) > 60:
            flag["cut"] = True
        return [trim(x, flag, sizes=sizes) for x in v[:60]]
    return v


def safe_rule(r):
    if not isinstance(r, dict):
        return False
    tool = str(r.get("toolName", ""))
    content = r.get("ruleContent")
    if content is None or str(content).strip() == "":
        return tool.startswith("mcp__")             # whole-tool rule only for one MCP tool
    c = str(content).strip()
    return c not in ("*", ":*", "**") and not c.startswith(":*")


def safe_suggestions(payload):
    out = []
    for s in payload.get("permission_suggestions") or []:
        if (isinstance(s, dict) and s.get("type") == "addRules" and s.get("behavior") == "allow"
                and isinstance(s.get("rules"), list) and s["rules"] and all(safe_rule(r) for r in s["rules"])):
            out.append(s)
    return out


def answers_fit(question, answers):
    items = question.get("questions") if isinstance(question, dict) else None
    if not isinstance(items, list) or not items or not isinstance(answers, dict):
        return False
    texts = [i.get("question") for i in items]
    if len(set(texts)) != len(texts) or set(texts) != set(answers):
        return False
    for item in items:
        labels = [o.get("label") for o in item.get("options") or [] if isinstance(o, dict)]
        pick = answers.get(item.get("question"))
        if item.get("multiSelect"):
            if not (isinstance(pick, list) and pick and len(set(pick)) == len(pick)
                    and all(isinstance(p, str) and p in labels for p in pick)):
                return False
        elif not (isinstance(pick, str) and pick in labels):
            return False
    return True


def decision_output(payload, reply):
    d = reply.get("decision")
    tool = payload.get("tool_name", "")
    if d == "answer":
        q = payload.get("tool_input") or {}
        ans = reply.get("answers")
        if tool != "AskUserQuestion" or not answers_fit(q, ans):
            return None
        dec = {"behavior": "allow", "updatedInput": dict(q, answers=ans)}
    elif d == "allow":
        dec = {"behavior": "allow"}
    elif d == "always":
        dec = {"behavior": "allow"}
        safe = safe_suggestions(payload)
        if safe:
            dec["updatedPermissions"] = safe
    elif d == "deny":
        dec = {"behavior": "deny", "message": "Denied by Boss from the GAYA sprite."}
    else:
        return None                                   # "terminal", unknown -> silence
    return {"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": dec}}


class Lines:
    """Line reader that keeps leftover bytes (ack + decision may arrive together)."""

    def __init__(self, sock):
        self.sock, self.buf = sock, b""

    def read(self, deadline):
        while b"\n" not in self.buf:
            left = deadline - time.time()
            if left <= 0:
                return None
            self.sock.settimeout(left)
            chunk = self.sock.recv(65536)
            if not chunk:
                return None
            self.buf += chunk
            if len(self.buf) > 262144:
                return None
        line, self.buf = self.buf.split(b"\n", 1)
        return json.loads(line.decode("utf-8"))


def log(event, what):
    """One line per hook run -> ~/.jarvis/logs/hook.log (no payloads, no secrets)."""
    try:
        p = os.path.join(JDIR, "logs", "hook.log")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write("%s %-18s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), event, what))
    except OSError:
        pass


def main():
    raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    payload = json.loads(raw or "{}")
    event = payload.get("hook_event_name", "")
    tool = payload.get("tool_name", "")
    try:
        key = open(KEYFILE, "rb").read().strip()
    except OSError:
        log(event, "no key file -> silence")
        return                                        # sprite never set up -> silence
    rid = uuid.uuid4().hex
    try:
        s = socket.create_connection(("127.0.0.1", PORT), timeout=CONNECT_S)
    except OSError:
        log(event, "sprite not running -> silence")
        return
    try:
        rd = Lines(s)
        s.sendall((json.dumps({"hello": rid, "auth": sig(key, "hook", rid)}) + "\n").encode())
        ready = rd.read(time.time() + ACK_S)
        if not ready or not hmac.compare_digest(str(ready.get("ready", "")), sig(key, "ready", rid)):
            log(event, "no valid ready -> silence")
            return                                    # impostor / not ours -> it never sees the payload
        flag, sizes = {}, {}
        shown = trim(payload, flag, top=True, sizes=sizes)
        s.sendall((json.dumps({"event": event, "payload": shown, "truncated": bool(flag),
                               "sizes": sizes}) + "\n").encode())
        if event != "PermissionRequest":
            return
        ack = rd.read(time.time() + ACK_S)
        if not ack or not hmac.compare_digest(str(ack.get("ack", "")), sig(key, "ack", rid)):
            log(event, "%s: card not acked -> terminal" % tool)
            return                                    # card not on screen -> terminal
        t0 = time.time()
        reply = rd.read(time.time() + DECIDE_S)
        if not reply:
            log(event, "%s: no decision in %.0fs -> terminal" % (tool, time.time() - t0))
            return
        d = str(reply.get("decision", ""))
        want = sig(key, "decision", rid, d, canon(reply.get("answers")))
        if not hmac.compare_digest(str(reply.get("sig", "")), want):
            log(event, "%s: bad decision signature -> silence" % tool)
            return
        out = decision_output(payload, reply)
        log(event, "%s: %s after %.1fs -> %s" % (tool, d, time.time() - t0, "sent" if out else "terminal"))
        if out:
            sys.stdout.write(json.dumps(out))
    finally:
        s.close()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass                                          # any failure = silence = terminal asks
    sys.exit(0)
