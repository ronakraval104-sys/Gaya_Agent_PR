"""Swap Coucou's 12 Claude Code hooks for the JARVIS sprite's.

    python swap_coucou_for_jarvis.py            # do it (backs up first)
    python swap_coucou_for_jarvis.py --undo     # restore the backup this made

Removes every hook entry whose command runs coucou-hook.exe and adds
jarvis_sprite_hook.py for the events the sprite uses. Every other hook
(the v10 guard, log, doctor, verdict hook) is left exactly as it is.
"""
import glob
import json
import os
import shutil
import sys
from datetime import datetime

SETTINGS = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")
PY = r"C:/Python314/python.exe"
HOOK = r"C:/Users/Ronak/Desktop/JARVIS/sprite/jarvis_sprite_hook.py"
CMD = '"%s" "%s"' % (PY, HOOK)
EVENTS = {"PermissionRequest": 120, "SessionStart": 10, "UserPromptSubmit": 10, "Notification": 10,
          "Stop": 10, "StopFailure": 10, "SubagentStart": 10, "SessionEnd": 10}


def main():
    if "--undo" in sys.argv:
        baks = sorted(glob.glob(SETTINGS + ".bak-pre-jarvis-sprite-*"))
        if not baks:
            sys.exit("no backup found")
        keep = SETTINGS + ".bak-before-undo-" + datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy(SETTINGS, keep)                    # later changes are never lost
        print("current settings saved to", keep)
        shutil.copy(baks[0], SETTINGS)                 # OLDEST = the original, pre-swap file
        print("restored", baks[0])
        return
    s = json.load(open(SETTINGS, encoding="utf-8"))
    bak = SETTINGS + ".bak-pre-jarvis-sprite-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy(SETTINGS, bak)
    hooks = s.setdefault("hooks", {})
    removed = 0
    for ev in list(hooks):
        keep = []
        for entry in hooks[ev]:
            cmds = [h.get("command", "") for h in entry.get("hooks", [])]
            if any("coucou-hook" in c.lower() for c in cmds):
                removed += 1
                continue
            keep.append(entry)
        if keep:
            hooks[ev] = keep
        else:
            del hooks[ev]
    added = 0
    for ev, timeout in EVENTS.items():
        lst = hooks.setdefault(ev, [])
        if any(HOOK.lower() in h.get("command", "").lower() for e in lst for h in e.get("hooks", [])):
            continue
        lst.append({"hooks": [{"type": "command", "command": CMD, "timeout": timeout}]})
        added += 1
    tmp = SETTINGS + ".tmp-jarvis"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2)
    json.load(open(tmp, encoding="utf-8"))               # valid JSON before it goes live
    os.replace(tmp, SETTINGS)                            # atomic swap
    print("backup: %s\nremoved %d Coucou hook entries, added %d JARVIS entries" % (bak, removed, added))


if __name__ == "__main__":
    main()
