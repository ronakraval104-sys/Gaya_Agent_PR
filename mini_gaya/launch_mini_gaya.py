import os
import sys
import time
import ctypes
import ctypes.wintypes
import subprocess
import win32process

HERE = os.path.dirname(os.path.abspath(__file__))

def kill_existing():
    # Terminate any process occupying port 8767
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-NetTCPConnection -LocalPort 8767 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"],
            capture_output=True, timeout=5
        )
    except Exception:
        pass

def launch_on_default_desktop():
    kill_existing()
    time.sleep(0.5)

    # Locate pythonw executable
    py_dir = os.path.dirname(sys.executable)
    candidates = [
        os.path.join(py_dir, "pythonw.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\WindowsApps\pythonw.exe"),
        "pythonw.exe"
    ]
    pythonw = "pythonw.exe"
    for c in candidates:
        if os.path.exists(c):
            pythonw = c
            break

    script = os.path.join(HERE, "mini_gaya.py")
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
    print(f"Mini Gaya spawned with PID {pid} targeted to WinSta0\\Default")

    user32 = ctypes.windll.user32
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)

    # Verify window registration on the interactive desktop
    for attempt in range(12):
        time.sleep(0.5)
        hDesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hDesk:
            hwnds = []
            def win_cb(h, lp):
                p = ctypes.wintypes.DWORD()
                user32.GetWindowThreadProcessId(h, ctypes.byref(p))
                if p.value == pid:
                    hwnds.append(h)
                return True
            user32.EnumDesktopWindows(hDesk, WNDENUMPROC(win_cb), 0)
            user32.CloseDesktop(hDesk)
            if hwnds:
                print(f"VERIFIED: Mini Gaya physical widget online with {len(hwnds)} windows on WinSta0\\Default!")
                return pid

    print(f"Mini Gaya spawned with PID {pid}. Desktop registration in progress.")
    return pid

if __name__ == "__main__":
    launch_on_default_desktop()
