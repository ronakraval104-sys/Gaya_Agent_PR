# Gaya Harness & Agent Integration Guide
<!-- Machine-readable & human-readable integration specification for Gaya Operator OS -->

This document provides exact connection protocols, authentication handshakes, and drop-in code snippets so any AI harness, IDE agent, or subagent (Antigravity, Claude Code, Cursor, Windsurf, custom Python/Node runners) can instantly connect to **Mini Gaya (Desktop Sprite)** and the **Council of Gaya Dashboard** at session startup.

---

## 1. Architecture Topology

```
┌────────────────────────────────────────────────────────┐
│                      AI HARNESS                        │
│    (Google Antigravity / Claude Code / Custom Agent)   │
└──────────────┬───────────────────────────┬─────────────┘
               │                           │
   TCP Socket  │                           │ HTTP REST / SSE
   Port 8767   │                           │ Port 4200
               ▼                           ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│          MINI GAYA           │  │       COUNCIL OF GAYA        │
│    Desktop Interactive Sprite│  │    Operator OS Dashboard     │
│  - Animated Gold Avatar      │  │  - Active Gaya Reactor Core  │
│  - TTS (Microsoft Heera)     │  │  - Threads & Gotchas Board   │
│  - STT (CUDA Whisper Turbo)  │  │  - GPU & Integrations Grid   │
│  - Windows Tray Notification │  │  - Council Specialists Graph │
└──────────────────────────────┘  └──────────────────────────────┘
```

---

## 2. Ports & Health Verification

| Service | Protocol & Port | Health Probe | Expected Response |
| :--- | :--- | :--- | :--- |
| **Mini Gaya Sprite** | TCP `127.0.0.1:8767` | TCP Socket Connect | Accepts connection, expects JSON handshake |
| **Council Dashboard** | HTTP `127.0.0.1:4200` | `GET http://localhost:4200/api/gaya-state` | `{"state":"idle", ...}` (HTTP 200) |
| **Knowledge Engine** | HTTP `127.0.0.1:4200` | `GET http://localhost:4200/api/knowledge/full` | `{"ok":true,"nodes":[...],"count":51}` |

---

## 3. Mini Gaya TCP Socket Protocol (Port 8767)

### Authentication Handshake
Mini Gaya's local socket requires HMAC-SHA256 authentication using the secret key stored on the machine:
- **Key Path**: `~/.gaya/key` (or `%USERPROFILE%\.gaya\key`)

### Step-by-Step Handshake:
1. Connect via TCP to `127.0.0.1:8767`.
2. Generate a random alphanumeric token: `<token>`.
3. Compute signature: `HMAC_SHA256(key, "hook|<token>")` in hex.
4. Send line:
   ```json
   {"hello": "<token>", "auth": "<signature>"}\n
   ```
5. Receive line from Mini Gaya confirming:
   ```json
   {"ready": "<expected_ready_signature>"}\n
   ```
6. Send events formatted as JSON lines:
   ```json
   {"event": "<EventName>", "payload": { ... }}\n
   ```

### Supported Event Types:
* **`Say`**: Speaks text through TTS and shows HUD speech toast.
  ```json
  {"event": "Say", "payload": {"text": "LOGOS passed the build, R0n."}}\n
  ```
* **`ToolStart`**: Animates Mini Gaya into `thinking` state with tool indicator.
  ```json
  {"event": "ToolStart", "payload": {"tool_name": "run_command", "summary": "Running build tests"}}\n
  ```
* **`ToolDone`**: Returns sprite to `idle` or `approved`.
  ```json
  {"event": "ToolDone", "payload": {"tool_name": "run_command", "status": "ok"}}\n
  ```
* **`PermissionRequest`**: Prompts user via floating approval card.
  ```json
  {"event": "PermissionRequest", "payload": {"tool_name": "git_push", "message": "Allow commit to master?"}}\n
  ```

---

## 4. Council Dashboard REST API (Port 4200)

### Telemetry State: `/api/gaya-state`
* **GET `/api/gaya-state`**: Returns current state of the Operator OS.
  ```json
  {
    "state": "idle",
    "detail": "Council standing by",
    "modelName": "Gemini 2.5 Pro (Thinking)",
    "harness": "Google Antigravity",
    "activeSeat": "bob",
    "isProcessing": false,
    "stepIndex": 42
  }
  ```
* **POST `/api/gaya-state`**: Update active agent state, current tool, and status.
  ```json
  {
    "state": "thinking",
    "detail": "Executing git synchronization",
    "activeSeat": "bob",
    "toolName": "run_command"
  }
  ```

### Knowledge & Threads Board: `/api/knowledge/full`
* **GET `/api/knowledge/full`**:
  Returns all 51 active knowledge nodes:
  - 10 Open Threads (age, priority, title, description, context)
  - 6 Gotchas (historical engineering traps & solutions)
  - 16 Decision Records
  - 11 Domain Laws
  - 8 Shipped Wins

---

## 5. Instant Drop-In Python Connector (`gaya_harness.py`)

Any agent can drop this file in and use it directly:

```python
import socket
import json
import hmac
import hashlib
import os
import secrets

class GayaHarness:
    def __init__(self, port=8767):
        self.port = port
        home = os.environ.get("USERPROFILE") or os.environ.get("HOME") or ""
        self.keyfile = os.path.join(home, ".gaya", "key")
        self.key = open(self.keyfile, "rb").read().strip() if os.path.exists(self.keyfile) else b""

    def send_event(self, event: str, payload: dict) -> bool:
        if not self.key:
            return False
        try:
            with socket.create_connection(("127.0.0.1", self.port), timeout=2.0) as sock:
                token = secrets.token_hex(16)
                sig = hmac.new(self.key, f"hook|{token}".encode(), hashlib.sha256).hexdigest()
                handshake = json.dumps({"hello": token, "auth": sig}) + "\n"
                sock.sendall(handshake.encode("utf-8"))
                
                resp = sock.recv(1024).decode("utf-8")
                if "ready" in resp:
                    msg = json.dumps({"event": event, "payload": payload}) + "\n"
                    sock.sendall(msg.encode("utf-8"))
                    return True
        except Exception:
            return False
        return False

    def say(self, text: str):
        return self.send_event("Say", {"text": text})

    def tool_start(self, tool_name: str, summary: str = ""):
        return self.send_event("ToolStart", {"tool_name": tool_name, "summary": summary})

    def tool_done(self, tool_name: str, status: str = "ok"):
        return self.send_event("ToolDone", {"tool_name": tool_name, "status": status})

# Example Usage:
if __name__ == "__main__":
    gaya = GayaHarness()
    gaya.say("Antigravity harness linked successfully, R0n!")
```

---

## 6. Autostart Commands (If Services Are Offline)

If a harness detects that Mini Gaya or the Dashboard is not running:

1. **Launch Mini Gaya Desktop Sprite**:
   ```powershell
   python d:\Ai_Tools\antigravity_ai\mini_gaya\launch_mini_gaya.py
   ```
   *(Uses Win32 `CreateProcessW` to mount on `WinSta0\Default` with system tray registration)*

2. **Launch Council of Gaya Dashboard**:
   ```powershell
   python d:\Ai_Tools\antigravity_ai\council_of_gaya\launch_dashboard.py
   ```
   *(Detached Next.js process tree on port 4200 with automated port cleanup and HTTP health check)*
