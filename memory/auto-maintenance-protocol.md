# Auto-Maintenance Protocol — 15-Day Cycle

**Purpose:** Prevent OpenCode freeze root causes before they happen.
**Schedule:** Every 15 days.
**Script:** `~/.config/opencode/scripts/auto-maintenance.ps1`

## What It Does

| Phase | Action | Why |
|---|---|---|
| **1. Audit** | Checks DB size, project dirs, agent configs, memory files | Identifies problems before they cause freezes |
| **2. Report** | Lists all findings grouped by category | You see everything before approving |
| **3. Approve** | Asks `y/N` before touching anything | Never runs without your permission |
| **4. Execute** | VACUUM DB, archive old dirs, fix stale refs, prune memory | The actual fix |
| **5. Summary** | Shows what was done, errors (if any), archive location | You know exactly what changed |

## What Gets Archived (Not Deleted)

Everything is **moved** to a timestamped archive directory — nothing is deleted:

- Heavy project directories (>200 files or >20 MB) that are no longer active
- Old session debriefs (>30 days)
- Legacy config files (superseded)
- Massive backups (>500 MB)

## What Gets Fixed In-Place

- **DB:** SQLite VACUUM reclaims disk space from pruned sessions
- **.gitignore:** Created if missing (excludes archived/old dirs from VCS watcher)
- **Stale refs:** Old agent names like "Bob" → updated to current names

## How to Run

### Manual:
```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.config\opencode\scripts\auto-maintenance.ps1"
```

### Automated (for scheduled tasks):
```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.config\opencode\scripts\auto-maintenance.ps1" -AutoApprove
```

## Safety Guarantees

- **No deletions.** Every file is moved to a timestamped archive folder.
- **Asks permission.** Unless `-AutoApprove` flag is set.
- **Logs everything.** Every run writes to a maintenance log.
- **Reversible.** Archived files can be moved back at any time.
