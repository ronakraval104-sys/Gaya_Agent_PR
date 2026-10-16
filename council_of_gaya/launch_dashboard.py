import os
import sys
import time
import subprocess
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(HERE, "dashboard.log")

def kill_port_4200():
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-NetTCPConnection -LocalPort 4200 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"],
            capture_output=True, timeout=5
        )
    except Exception:
        pass

def launch():
    kill_port_4200()
    time.sleep(1)
    
    log_fd = open(LOG_FILE, "a", encoding="utf-8")
    log_fd.write(f"\n--- Council of Gaya Dashboard starting at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
    log_fd.flush()
    
    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    
    proc = subprocess.Popen(
        ["cmd.exe", "/c", "npm", "run", "dev"],
        cwd=HERE,
        stdout=log_fd,
        stderr=log_fd,
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    )
    print(f"Launched Next.js dev server PID: {proc.pid}")
    
    # Poll http://localhost:4200 for readiness
    ready = False
    for attempt in range(25):
        time.sleep(1)
        try:
            req = urllib.request.Request("http://localhost:4200/", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    print(f"VERIFIED: Dashboard online at http://localhost:4200/ (HTTP 200 OK after {attempt+1}s)")
                    ready = True
                    break
        except Exception:
            pass
            
    if not ready:
        print("Warning: Server took longer than 25s to respond. Check dashboard.log.")
    return proc.pid

if __name__ == "__main__":
    launch()
