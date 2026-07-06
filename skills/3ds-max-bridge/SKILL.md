# 3ds Max Bridge — MaxLink REST API + pymxs Threading Architecture

**Domain:** 3ds Max 2024 / pymxs / MAXScript / Automation  
**Author:** Gaya (deployed for R0n, 02-Jun-2026)  
**Prerequisites:** 3ds Max 2024 with Python 3.10 and pymxs  
**Core Tool:** `autodesk-bim/MaxLink/` — HTTP bridge inside 3ds Max Python

---

## When to Use

Activate this skill when:
- Controlling 3ds Max programmatically from AI agents or external scripts
- Building an HTTP bridge between AI and 3ds Max
- Using **pymxs** and hitting the `"MAXScript call is only allowed on Python main thread"` error
- 3ds Max crashes on opening the **Material Editor** (pressing M key)
- Designing threading-safe communication with MAXScript
- Setting up auto-start scripts for 3ds Max boot
- ArchViz scene generation from AI to 3ds Max

### NOT for
- General 3ds Max modeling advice (this is about programmatic control)
- V-Ray/Corona/Redshift specific issues
- Game development in UE5 (use `unreal-engine-cpp-pro`)

---

## 🧠 CRITICAL LESSON: 3ds Max Has a Fragile Ecosystem

> **"Don't brute-force 3ds Max. It has a fragile ecosystem."** — R0n, 26-year Max veteran

**NEVER:**
- Use `SendKeys` or PowerShell window hacking to inject commands into Max
- Kill the 3ds Max process from outside
- Try to programmatically dismiss Max's modal dialogs
- Use automation to navigate Max's UI

**ALWAYS:**
- Let the user restart Max themselves
- Use programmatic APIs (MaxLink, pymxs, MAXScript) instead of UI automation
- Edit config files (`*.ini`) when Max is NOT running
- Respect that Max's UI state is delicate and interconnected

---

## 🔴 IRON LAW: pymxs Is Main-Thread Only

**pymxs** (3ds Max's Python bridge) runs **ONLY on 3ds Max's main thread**. Any call to `rt.*` functions from a background Python thread raises:

```
RuntimeError: MAXScript call is only allowed on Python main thread
```

This applies to:
- HTTP server handler threads (must use `ThreadingMixIn` carefully)
- .NET thread pool timers (`System.Timers.Timer`)
- Python `threading.Thread` created from within Max's Python

### How to Fix: MAXScript Timer Bridge (The Only Reliable Pattern)

The ONLY reliable pattern for calling pymxs from background threads:

```
┌─────────────────────────────────────────────────────────┐
│  MAXScript Timer (fires on MAXSCRIPT MAIN THREAD)       │
│                                                         │
│  fn MaxLink_drainQueue = (                              │
│      python.Execute "import maxlink; maxlink._drain()"  │
│  )                                                      │
│  MaxLink_timer = timers.create()                        │
│  MaxLink_timer.interval = 50                            │
│  MaxLink_timer.onTimeEvent = MaxLink_drainQueue         │
└───────────────────────────┬─────────────────────────────┘
                            │ fires every 50ms on MAIN thread
                            ▼
┌─────────────────────────────────────────────────────────┐
│  python.Execute (runs on Max's main thread)             │
│  → calls _drain_queue() in Python                      │
│    → executes queued pymxs commands                     │
│      → sets threading.Event to wake HTTP handler        │
└─────────────────────────────────────────────────────────┘
```

**Key insight:** The MAXScript timer must be created from the **MAXScript startup file** (not from Python via `rt.execute()`), because:
1. The startup script runs on the main thread automatically
2. MAXScript timers reliably fire callbacks on the main thread
3. `python.Execute` bridges to Python on that same main thread
4. The timer survives Python module reloads (it calls `python.Execute` with the module name)

**DO NOT use these (they fire on background threads):**
- `System.Timers.Timer` (.NET thread pool — ❌)
- `rt.doTimer(python_callback)` (callback runs on thread pool — ❌)
- `threading.Thread` polling loop (background thread — ❌)

**DO use (in MAXScript startup script):**
```maxscript
-- This goes in startup\MaxLink_Startup.ms:
global fn MaxLink_drainQueue = (
    python.Execute "import maxlink_server; maxlink_server._drain_queue()"
)
if globalVars.isDefined #MaxLink_timer do (
    try (timers.destroy MaxLink_timer) catch()
)
global MaxLink_timer = timers.create()
MaxLink_timer.interval = 50
MaxLink_timer.onTimeEvent = MaxLink_drainQueue
```

---

## 🛠️ MaxLink Bridge Architecture

```
┌──────────────┐     HTTP (port 9876)     ┌──────────────────────┐
│  AI Agent    │ ◄──────────────────────► │  3ds Max Python      │
│  (Gaya/Bob)  │                          │  maxlink_server.py   │
│  maxlink_    │                          │                      │
│  client.py   │                          │  ThreadedHTTPServer  │
└──────────────┘                          │  (background thread) │
                                          │         │            │
                                          │         ▼            │
                                          │  _pymxs_queue[]      │
                                          │  (thread-safe list)  │
                                          │         │            │
                                          │         ▼            │
                                          │  MAXScript Timer     │
                                          │  (main thread, 50ms) │
                                          │         │            │
                                          │         ▼            │
                                          │  _drain_queue()      │
                                          │  → pymxs rt.* calls  │
                                          │  → threading.Event   │
                                          └──────────────────────┘
```

### Project Structure
```
autodesk-bim/MaxLink/
├── server/
│   ├── maxlink_server.py      # HTTP server (runs INSIDE 3ds Max Python)
│   └── maxlink_startup.ms     # MAXScript auto-start for boot
├── client/
│   └── maxlink_client.py      # Client library for AI agents
└── examples/
    ├── test_connection.py     # 8-test suite (run this first)
    ├── ai_to_max_demo.py      # Full archviz scene demo
    └── quick_test.py          # Quick connection test
```

### Startup Script Location
```
%LOCALAPPDATA%\Autodesk\3dsMax\2024 - 64bit\ENU\scripts\startup\MaxLink_Startup.ms
```

### Server Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/status` | Server health check |
| `GET` | `/api/version` | 3ds Max version info |
| `GET` | `/api/scene/list` | List all objects |
| `POST` | `/api/scene/clear` | Delete all objects |
| `POST` | `/api/scene/create-box` | Create box primitive |
| `POST` | `/api/scene/create-sphere` | Create sphere |
| `POST` | `/api/scene/create-cylinder` | Create cylinder |
| `POST` | `/api/scene/create-plane` | Create plane |
| `POST` | `/api/scene/import` | Import FBX/OBJ/STL |
| `POST` | `/api/scene/export` | Export to FBX |
| `POST` | `/api/scene/select` | Select object by name |
| `POST` | `/api/scene/delete` | Delete object |
| `POST` | `/api/scene/transform` | Move/rotate/scale |
| `POST` | `/api/material/standard` | Assign standard material |
| `POST` | `/api/render` | Render viewport |
| `POST` | `/api/script/run` | Run MAXScript |
| `POST` | `/api/execute` | Run Python code |

Auth: `Authorization: Bearer maxlink-token`

---

## 🔧 Material Editor Crash Fix (M Key Crash)

### Symptom
Pressing M (or opening material editor via UI) crashes 3ds Max. Common with V-Ray/Corona.

### Root Cause
Corrupted ENU user preferences + Slate Material Editor triggering a UI bug.

### Fix Steps
1. **Exit 3ds Max completely**
2. **Rename ENU folder** to reset user preferences:
   ```
   %LOCALAPPDATA%\Autodesk\3dsMax\2024 - 64bit\ENU  →  ENU_backup_YYYYMMDD
   ```
3. **Set default editor to Compact** (not Slate) in `CurrentDefaults.ini`:
   ```
   %LOCALAPPDATA%\...\ENU\en-US\defaults\MAX\CurrentDefaults.ini
   ```
   Change: `EditorMode=1` → `EditorMode=0`
   - `0` = Basic/Compact mode (safe)
   - `1` = Advanced/Slate mode (triggers crash)
4. **Restart 3ds Max** — fresh ENU created, compact editor loads by default

### Notes
- The crash is a known Autodesk UI bug (multiple forum threads, 2020-2025)
- Some users report VC++ Redistributable (vcomp140.dll) also causing this
- ENU reset removes all custom UI, toolbars, and preferences — backup if needed

---

## 🧪 Testing MaxLink

### Basic Connection Test
```powershell
# From project directory:
python examples\test_connection.py
```

### Manual curl Tests
```powershell
# Health check
curl.exe -s http://localhost:9876/api/status

# Version (requires pymxs main-thread)
curl.exe -s -G http://localhost:9876/api/version -H "Authorization: Bearer maxlink-token"

# Create box
curl.exe -s -X POST http://localhost:9876/api/scene/create-box `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer maxlink-token" `
  -d '{"length":50,"width":50,"height":50,"name":"Test_Box","position":[0,0,25]}'

# Run MAXScript
curl.exe -s -X POST http://localhost:9876/api/script/run `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer maxlink-token" `
  -d '{"script":"return 42 + 58"}'
```

### Python Client
```python
from maxlink_client import MaxLink

max = MaxLink()
print(max.status())
box = max.create_box(length=50, width=50, height=50, name="Box1", position=[0, 0, 25])
max.assign_material("Box1", diffuse=[200, 50, 50], glossiness=50)
max.move("Box1", [100, 0, 25])
max.run_script('return "Hello from MAXScript"')
max.clear_scene()
```

---

## 💾 Module Reload Pattern

When updating MaxLink code while Max is running, use the `/api/execute` endpoint to reload:

```python
import sys
# Stop old server
try:
    import maxlink_server as old_mls
    old_mls.stop()
except:
    pass
# Remove old module references
for k in list(sys.modules.keys()):
    if "maxlink" in k:
        del sys.modules[k]
# Load updated file
exec(open(r"D:\...\maxlink_server.py").read())
# Start new server
result = start(port=9876)
```

**Note:** The MAXScript timer (created in the startup script) survives the reload because it calls `python.Execute "import maxlink_server; maxlink_server._drain_queue()"` — which picks up the updated module.

---

## 🚫 Anti-Patterns (Painful Lessons Learned)

| What NOT To Do | Why It Fails |
|---|---|
| `System.Timers.Timer` to drain pymxs queue | Fires on .NET thread pool, not Max main thread |
| `rt.doTimer(python_callback)` with Python function | Callback runs on background thread in pymxs |
| `SendKeys` to inject commands into MAXScript Listener | Fragile, unescaped chars crash Max, garbled input |
| `PostMessage(WM_CLOSE)` to dismiss dialogs | Can close main window, hide all UI |
| `ShowWindow` + `SetForegroundWindow` for UI automation | Race conditions, unreliable with Qt dialogs |
| `threading.Thread` polling loop with `rt.*` calls | `"MAXScript call only allowed on Python main thread"` |
| Killing 3ds Max process from PowerShell | Can corrupt scene files and preferences |

---

## 📁 Key File Paths

| Path | Purpose |
|---|---|
| `D:\Ai_Tools\Open_code\project_folder\autodesk-bim\MaxLink\server\maxlink_server.py` | Server code (runs inside Max Python) |
| `D:\...\MaxLink\client\maxlink_client.py` | Client library for AI agents |
| `D:\...\MaxLink\examples\test_connection.py` | 8-test connection suite |
| `D:\...\MaxLink\examples\ai_to_max_demo.py` | Archviz scene demo |
| `%LOCALAPPDATA%\Autodesk\3dsMax\2024 - 64bit\ENU\scripts\startup\MaxLink_Startup.ms` | Auto-start script |
| `%LOCALAPPDATA%\Autodesk\3dsMax\2024 - 64bit\ENU\3dsMax.ini` | Main config (EditorMode etc.) |
| `%LOCALAPPDATA%\Autodesk\3dsMax\2024 - 64bit\ENU\en-US\defaults\MAX\CurrentDefaults.ini` | Material editor defaults |

---

## 📜 Version History

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 02-Jun-2026 | Initial — MaxLink bridge, threading architecture, ENU fix |
