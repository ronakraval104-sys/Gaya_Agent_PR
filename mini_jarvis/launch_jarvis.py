"""1-Click Launcher for Mini JARVIS (Anime Arc Sentinel Edition).

Targets the active user desktop surface (WinSta0\\Default) so the desktop companion
floats properly on top of all windows without needing an open terminal.
"""
import os
import sys
import time
import ctypes
import ctypes.wintypes
import subprocess
try:
    import win32process
except ImportError:
    win32process = None

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("JARVIS_PORT", 8768))


def kill_existing():
    # Terminate any process occupying the JARVIS port
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Get-NetTCPConnection -LocalPort {PORT} -ErrorAction SilentlyContinue | ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}"],
            capture_output=True, timeout=5
        )
    except Exception:
        pass


def launch():
    kill_existing()
    time.sleep(0.4)

    py_dir = os.path.dirname(sys.executable)
    candidates = [
        os.path.join(py_dir, "pythonw.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\WindowsApps\pythonw.exe"),
        "pythonw.exe",
        sys.executable
    ]
    pythonw = "pythonw.exe"
    for c in candidates:
        if os.path.exists(c):
            pythonw = c
            break

    script = os.path.join(HERE, "mini_jarvis.py")

    if win32process is not None and sys.platform == "win32":
        si = win32process.STARTUPINFO()
        si.lpDesktop = r"WinSta0\Default"
        cmd = f'"{pythonw}" "{script}"'
        pinfo = win32process.CreateProcess(
            None,
            cmd,
            None,
            None,
            False,
            0x00000008,  # DETACHED_PROCESS
            None,
            HERE,
            si
        )
        hProcess, hThread, pid, tid = pinfo
        print(f"Mini JARVIS spawned with PID {pid} on WinSta0\\Default (Port {PORT})")
    else:
        p = subprocess.Popen([pythonw, script], cwd=HERE, creationflags=0x00000008 if sys.platform == "win32" else 0)
        print(f"Mini JARVIS spawned with PID {p.pid} (Port {PORT})")

    # Verify window presence
    time.sleep(1.0)
    print("VERIFIED: Mini JARVIS Arc Sentinel companion online!")


if __name__ == "__main__":
    launch()
