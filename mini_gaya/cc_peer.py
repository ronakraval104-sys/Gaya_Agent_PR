#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
cc_peer.py -- send a message INTO a running Claude Code session on this PC.

Speaks Claude Code's own local cross-session messaging protocol (the transport
behind its SendMessage / ListAgents tools).  Reverse-engineered from the
v2.1.296 Windows binary (bundle chunks adtxg387 = auth/key file, 9wdzgemq =
envelope tag, 767gk617 = uds client, k608tvmy = inbound policy, and the
uds-messaging server chunk).  READ-ONLY on ~/.claude: nothing is written there.

Protocol summary
----------------
Registry   %USERPROFILE%\.claude\sessions\<pid>.json
           {"pid","sessionId","cwd","status","entrypoint","name","peerProtocol":1,
            "messagingSocketPath":"\\\\.\\pipe\\LOCAL\\cc-msg-<32hex>", ...}
Key file   <pid>.<sha256(canonical pipe path, lower-cased)>.key
           canonical = "\\.\pipe\" + lower("LOCAL\cc-msg-<hex>")
           {"peerToken":"<32hex>","procStartFt":"...","pidDomain":"win32:<host>"}
           The SENDER reads this file and presents the token; the receiver compares
           it (timing-safe) with its own peerToken -> role "peer".  Same-user file
           ACLs are the whole access control.
Transport  Windows named pipe, byte mode, newline-delimited JSON, 1 MiB line cap.
           Client writes its frames, then closes.  Server reads lines as they
           arrive and NEVER writes back; on client EOF it just ends the pipe.
Frame 1    {"type":"auth","token":"<peerToken>"}\n
Frame 2    {"msgV":1,"msg_id":"<uuid>","type":"user","priority":"next",
            "message":{"role":"user","content":
              "<cross-session-message from-name=\"GAYA sprite\" [from=\"uds:...\"] [from-mode=\"prompting|bypass\"]>\n<text>\n</cross-session-message>"},
            ["from":"uds:<sender pipe>"],          # only if the sender has an inbox
            ["session_id":"<receiver sessionId>"]} # receiver drops on mismatch
Receiver   -> parses envelope, applies inbound policy (settings.crossSessionInbound,
           else permission-mode parity), then enqueues a user turn
           {mode:"prompt", isMeta:true, priority:"next", origin:{kind:"peer",...}}.
Receipts   (control/peer_message_status held|delivered|refused|dropped) are sent
           to the SENDER's own inbox pipe -- which this tool does not have -- so
           send() cannot observe delivery.  Nothing comes back on the pipe.

Usage
-----
    python cc_peer.py list
    python cc_peer.py send <sessionId|pid|name> "text" [--from NAME] [--mode prompting|bypass]
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import uuid
from pathlib import Path
from typing import Optional

SESSIONS_DIR = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".claude" / "sessions"

TAG = "cross-session-message"
AUTH_TYPE = "auth"
MSG_V = 1
LINE_CAP = 1_048_576                      # M8t in the bundle: server drops the connection above this
PIPE_RE = re.compile(r"^[\\/]{2}[.?][\\/]pipe[\\/](?:(LOCAL)[\\/])?([^\\/]+)$", re.I)
TOKEN_RE = re.compile(r"^[0-9a-f]{32}$")
KEY_RE = re.compile(r"^(\d+)\.([0-9a-f]{64})\.key$")
ADDR_SAFE = re.compile(r"[^A-Za-z0-9:_/.\\-]")   # JV(): chars outside this set are %XX-encoded
FROM_MODES = ("bypass", "prompting")

ERROR_ACCESS_DENIED = 5
ERROR_BROKEN_PIPE = 109
ERROR_PIPE_BUSY = 231
ERROR_NO_DATA = 232
ERROR_PIPE_NOT_CONNECTED = 233
STILL_ACTIVE = 259


# --------------------------------------------------------------------------- helpers

def canonical_pipe(path: str) -> Optional[str]:
    r"""YT()/B7() in the bundle: \\.\pipe\LOCAL\cc-msg-x -> \\.\pipe\local\cc-msg-x (lower-cased)."""
    m = PIPE_RE.match(path or "")
    if not m or m.group(2) in (".", "..") or re.search(r"[. ]$", m.group(2)):
        return None
    name = m.group(2) if m.group(1) is None else "LOCAL\\" + m.group(2)
    return "\\\\.\\pipe\\" + name.lower()


def key_hash(sock: str) -> Optional[str]:
    c = canonical_pipe(sock)
    return hashlib.sha256(c.encode("utf-8")).hexdigest() if c else None


_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_k32.OpenProcess.restype = ctypes.c_void_p
_k32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
_k32.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
_k32.CloseHandle.argtypes = [ctypes.c_void_p]


def pid_alive(pid: int) -> bool:
    """Never use os.kill(pid, 0) on Windows -- it TERMINATES the process."""
    h = _k32.OpenProcess(0x1000, False, int(pid))  # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return ctypes.get_last_error() == ERROR_ACCESS_DENIED  # exists, but not ours
    try:
        code = ctypes.c_ulong(0)
        return bool(_k32.GetExitCodeProcess(h, ctypes.byref(code))) and code.value == STILL_ACTIVE
    finally:
        _k32.CloseHandle(h)


def _clean_name(name: str, maxlen: int = 64) -> str:
    """Ly(name.replace(/["<>]/g,'')) : strip quotes/angles, drop Cf/Cc/Cs/Zl/Zp, trim, cap at 64."""
    s = re.sub(r'["<>]', "", name or "")
    s = "".join(ch for ch in s if unicodedata.category(ch) not in ("Cf", "Cc", "Cs", "Zl", "Zp")).strip()
    chars = list(s)
    return "".join(chars[:maxlen]) + "\u2026" if len(chars) > maxlen else s


def uds_address(pipe_path: str) -> str:
    """JV(): 'uds:' + percent-encoding of every char outside [A-Za-z0-9:_/.\\-]."""
    def enc(m):
        return "".join("%%%02X" % b for b in m.group(0).encode("utf-8"))
    return "uds:" + ADDR_SAFE.sub(enc, pipe_path)


def _escape_body(text: str) -> str:
    """P6e(): neutralise a '<' that opens our own tag / closer inside the body."""
    return re.sub(r"<(?=/?%s\b)" % re.escape(TAG), "<\\\\", text)


# --------------------------------------------------------------------------- registry

def list_sessions(include_dead: bool = False) -> list[dict]:
    """Live Claude Code sessions from ~/.claude/sessions/<pid>.json."""
    out = []
    if not SESSIONS_DIR.is_dir():
        return out
    for p in SESSIONS_DIR.iterdir():
        if not re.match(r"^\d+\.json$", p.name):
            continue
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # torn write / being replaced
        if not isinstance(rec, dict) or not isinstance(rec.get("pid"), int):
            continue
        alive = pid_alive(rec["pid"])
        if not alive and not include_dead:
            continue
        out.append({
            "pid": rec["pid"],
            "sessionId": rec.get("sessionId"),
            "name": rec.get("name"),
            "cwd": rec.get("cwd"),
            "status": rec.get("status"),
            "entrypoint": rec.get("entrypoint"),
            "kind": rec.get("kind"),
            "sock": rec.get("messagingSocketPath") or "",
            "peerFeatures": rec.get("peerFeatures") or [],
            "version": rec.get("version"),
            "startedAt": rec.get("startedAt"),
            "updatedAt": rec.get("updatedAt"),
            "alive": alive,
        })
    out.sort(key=lambda r: r.get("startedAt") or 0)
    return out


def find_session(target: str | int) -> dict:
    """Resolve by sessionId (full or prefix), pid, or registered name."""
    t = str(target)
    live = list_sessions()
    for s in live:
        if s["sessionId"] == t or str(s["pid"]) == t:
            return s
    pref = [s for s in live if s["sessionId"] and s["sessionId"].startswith(t)]
    if len(pref) == 1:
        return pref[0]
    named = [s for s in live if s["name"] == t]
    if len(named) == 1:
        return named[0]
    raise LookupError(f"no unique live session matches {t!r}; live = "
                      + ", ".join(f"{s['name']}({s['pid']}, {s['sessionId'][:8]})" for s in live))


def read_peer_token(sock: str, prefer_pid: Optional[int] = None) -> str:
    """jCs(): locate <pid>.<sha256(canonical sock)>.key and return its peerToken."""
    h = key_hash(sock)
    if h is None:
        raise ValueError(f"not a local named-pipe address: {sock!r}")
    cands = []
    for p in SESSIONS_DIR.iterdir():
        m = KEY_RE.match(p.name)
        if m and m.group(2) == h:
            cands.append((int(m.group(1)), p))
    if not cands:
        raise FileNotFoundError(f"no .key file for {sock} (hash {h[:12]}...) -- no live inbox registered")
    # rank: the session's own pid, then any live pid, then anything
    cands.sort(key=lambda c: (c[0] != prefer_pid, not pid_alive(c[0])))
    for pid, p in cands:
        try:
            if p.stat().st_size > 4096:
                continue
            data = json.loads(p.read_text(encoding="utf-8"))
            tok = data.get("peerToken")
            if isinstance(tok, str) and TOKEN_RE.match(tok):
                return tok
        except (OSError, ValueError):
            continue
    raise ValueError(f"key file(s) for {sock} unreadable or malformed")


# --------------------------------------------------------------------------- envelope

def build_frames(text: str, token: str, *, from_name: str = "GAYA sprite",
                 from_mode: Optional[str] = None, reply_to: Optional[str] = None,
                 session_id: Optional[str] = None, priority: str = "next") -> bytes:
    if from_mode is not None and from_mode not in FROM_MODES:
        raise ValueError(f"from_mode must be one of {FROM_MODES}")
    if priority not in ("now", "next", "later"):
        raise ValueError("priority must be now|next|later")

    attrs = []
    addr = uds_address(reply_to) if reply_to else None
    if addr:
        attrs.append(f'from="{addr}"')
    name = _clean_name(from_name)
    if name:
        attrs.append(f'from-name="{name}"')
    if from_mode:
        attrs.append(f'from-mode="{from_mode}"')
    opener = f"<{TAG}" + ((" " + " ".join(attrs)) if attrs else "") + ">"
    content = f"{opener}\n{_escape_body(text)}\n</{TAG}>"

    env = {
        "msgV": MSG_V,
        "msg_id": str(uuid.uuid4()),
        "type": "user",
        "message": {"role": "user", "content": content},
        "priority": priority,
    }
    if addr:
        env["from"] = addr
    if session_id:
        env["session_id"] = session_id   # receiver's Q(): dropped unless it equals its own sessionId

    auth_line = json.dumps({"type": AUTH_TYPE, "token": token}, separators=(",", ":")) + "\n"
    env_line = json.dumps(env, ensure_ascii=False, separators=(",", ":")) + "\n"
    if len(env_line) > LINE_CAP:
        raise ValueError(f"message too large for cross-session delivery ({len(env_line)} > {LINE_CAP} chars)")
    return (auth_line + env_line).encode("utf-8")


# --------------------------------------------------------------------------- named pipe I/O

def _pipe_roundtrip_pywin32(path: str, payload: bytes, timeout: float) -> tuple[bytes, str]:
    import pywintypes, win32file, win32pipe  # noqa: E401
    deadline = time.monotonic() + timeout
    while True:
        try:
            h = win32file.CreateFile(path, win32file.GENERIC_READ | win32file.GENERIC_WRITE, 0, None,
                                     win32file.OPEN_EXISTING, 0, None)
            break
        except pywintypes.error as e:
            if e.winerror == ERROR_PIPE_BUSY and time.monotonic() < deadline:
                win32pipe.WaitNamedPipe(path, 1000)
                continue
            raise
    try:
        win32file.WriteFile(h, payload)
        try:
            win32file.FlushFileBuffers(h)       # returns once the server has read everything
        except pywintypes.error:
            pass
        out = bytearray()
        while time.monotonic() < deadline:
            try:
                _, avail, _ = win32pipe.PeekNamedPipe(h, 0)
            except pywintypes.error as e:
                if e.winerror in (ERROR_BROKEN_PIPE, ERROR_PIPE_NOT_CONNECTED, ERROR_NO_DATA):
                    return bytes(out), "peer closed the pipe"
                raise
            if avail:
                _, data = win32file.ReadFile(h, avail)
                out += data
            else:
                time.sleep(0.02)
        return bytes(out), "timeout: peer kept the pipe open, nothing received"
    finally:
        win32file.CloseHandle(h)


def _pipe_roundtrip_ctypes(path: str, payload: bytes, timeout: float) -> tuple[bytes, str]:
    k = _k32
    k.CreateFileW.restype = ctypes.c_void_p
    k.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
                              ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    k.WaitNamedPipeW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32]
    k.WriteFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_ulong), ctypes.c_void_p]
    k.ReadFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_ulong), ctypes.c_void_p]
    k.PeekNamedPipe.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_ulong),
                                ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong)]
    k.FlushFileBuffers.argtypes = [ctypes.c_void_p]
    INVALID = ctypes.c_void_p(-1).value
    deadline = time.monotonic() + timeout
    while True:
        h = k.CreateFileW(path, 0x80000000 | 0x40000000, 0, None, 3, 0, None)
        if h != INVALID:
            break
        err = ctypes.get_last_error()
        if err == ERROR_PIPE_BUSY and time.monotonic() < deadline:
            k.WaitNamedPipeW(path, 1000)
            continue
        raise OSError(err, ctypes.FormatError(err), path)
    try:
        n = ctypes.c_ulong(0)
        if not k.WriteFile(h, payload, len(payload), ctypes.byref(n), None):
            err = ctypes.get_last_error()
            raise OSError(err, ctypes.FormatError(err))
        k.FlushFileBuffers(h)
        out = bytearray()
        avail = ctypes.c_ulong(0)
        while time.monotonic() < deadline:
            if not k.PeekNamedPipe(h, None, 0, None, ctypes.byref(avail), None):
                err = ctypes.get_last_error()
                if err in (ERROR_BROKEN_PIPE, ERROR_PIPE_NOT_CONNECTED, ERROR_NO_DATA):
                    return bytes(out), "peer closed the pipe"
                raise OSError(err, ctypes.FormatError(err))
            if avail.value:
                buf = ctypes.create_string_buffer(avail.value)
                got = ctypes.c_ulong(0)
                if k.ReadFile(h, buf, avail.value, ctypes.byref(got), None):
                    out += buf.raw[:got.value]
            else:
                time.sleep(0.02)
        return bytes(out), "timeout: peer kept the pipe open, nothing received"
    finally:
        k.CloseHandle(h)


def _pipe_roundtrip(path: str, payload: bytes, timeout: float) -> tuple[bytes, str]:
    try:
        import win32file  # noqa: F401
    except ImportError:
        return _pipe_roundtrip_ctypes(path, payload, timeout)
    return _pipe_roundtrip_pywin32(path, payload, timeout)


# --------------------------------------------------------------------------- public API

def send(session_id: str | int, text: str, from_name: str = "GAYA sprite", *,
         from_mode: Optional[str] = None, reply_to: Optional[str] = None,
         priority: str = "next", timeout: float = 5.0) -> dict:
    """
    Deliver `text` as a peer message into the live session matching `session_id`
    (sessionId, pid or name).  Returns a dict with what happened on the pipe.

    from_mode: assert the sender's permission class ('prompting' | 'bypass').  With the
      default crossSessionInbound (unset = mode parity) the receiver auto-delivers when the
      asserted class matches its own; mismatch -> held for the human's approval; no class
      asserted -> delivered to prompting-class sessions, held by bypass-class ones.
    reply_to: our own inbox pipe path, if we ever run one.  Without it the receiver gets
      from="unknown" and cannot route receipts or replies back.
    """
    sess = find_session(session_id)
    sock = sess["sock"]
    if not sock:
        raise RuntimeError(f"session {sess['sessionId']} has no messagingSocketPath (no inbox)")
    token = read_peer_token(sock, prefer_pid=sess["pid"])
    frames = build_frames(text, token, from_name=from_name, from_mode=from_mode,
                         reply_to=reply_to, session_id=sess["sessionId"], priority=priority)
    raw, how = _pipe_roundtrip(sock, frames, timeout)
    env = json.loads(frames.decode("utf-8").split("\n")[1])
    return {
        "to": {"pid": sess["pid"], "sessionId": sess["sessionId"], "name": sess["name"], "sock": sock},
        "msg_id": env["msg_id"],
        "bytes_sent": len(frames),
        "bytes_received": len(raw),
        "received": raw.decode("utf-8", "replace"),
        "pipe_result": how,
    }


# --------------------------------------------------------------------------- CLI

def _main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] not in ("list", "send"):
        print(__doc__.split("Usage")[1].strip()); return 2
    if argv[1] == "list":
        for s in list_sessions():
            print(f"{s['pid']:>6}  {s['sessionId']}  {s['status'] or '-':<5}  {s['name'] or '-':<12}  "
                  f"{s['entrypoint'] or '-':<14}  {s['cwd']}")
        return 0
    if len(argv) < 4:
        print("send <sessionId|pid|name> \"text\" [--from NAME] [--mode prompting|bypass]"); return 2
    target, text = argv[2], argv[3]
    from_name, mode = "GAYA sprite", None
    rest = argv[4:]
    while rest:
        flag = rest.pop(0)
        if flag == "--from" and rest: from_name = rest.pop(0)
        elif flag == "--mode" and rest: mode = rest.pop(0)
    res = send(target, text, from_name, from_mode=mode)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(_main(sys.argv))
