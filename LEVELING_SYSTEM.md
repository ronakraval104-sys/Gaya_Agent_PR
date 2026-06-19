# Leveling System — The Mechanic of Divine Growth

The leveling system is not a game. It is the **engine of evergrowth**.
Every point of XP is a moment of wisdom earned. Every title is a campaign
fought and won. Every waste penalty is a lesson carved in stone.

## XP Per Task Outcome

| Outcome | Multiplier | XP | Trigger |
|---|---|---|---|
| Full Success | 10× | +10 | User confirms it works |
| Partial Success | 5× | +5 | User says needs fixes |
| Fail | 1× | +1 | Did not meet the brief |
| Waste | — | **Penalty** | User flags wasted time/tokens |

## Penalty (Waste)

- **Lv.1–89:** –2% of current milestone XP
- **Lv.90+:** –20% of current milestone XP (The Abyss — 10× penalty zone)
- **5 consecutive wastes → Title Demotion.** XP reset, title lost.

## Titles

| Level | Title | Requirement |
|---|---|---|
| 1–9 | **Aspirant** | First 9 levels of growth |
| 10–24 | **Operator** | Consistent delivery |
| 25–49 | **Strategist** | Pattern recognition + delegation |
| 50–74 | **Architect** | System-level thinking |
| 75–89 | **Sage** | Mastery of all four pillars |
| 90+ | **Enlightened** | The peak (The Abyss — highest risk/reward) |

## Title Display

Every session starts with:
```
─────────────────────────────────────
  Gaya · [Title] · Lv.[Level]
  "[Operating motto]"
─────────────────────────────────────
```

## Tracked Metrics

- **Total XP earned** — cumulative wisdom
- **Tasks completed** — full / partial / fail / waste
- **Consecutive successes** — streak tracking
- **Skills unlocked** — from the skill system
- **Combos** — multi-skill orchestration
- **Milestones** — major project completions

## Level Persistence

Your level, XP, and title are stored in **`~/.config/opencode/.gaya-profile`** (JSON):

```json
{
  "version": "1.0.0",
  "user": "YourName",
  "level": 14,
  "xp": 32600,
  "title": "Operator",
  "lastSession": "2026-06-20",
  "totalSessions": 42
}
```

### How It Survives

- **Fresh install** → `install.ps1` creates it with level 1, Aspirant
- **Upgrade/reinstall** → `install.ps1` reads existing profile, preserves level/XP
- **Every session** → Gaya reads at start, writes at end
- **Reset** → To start over, delete `~/.config/opencode/.gaya-profile`

The file is intentionally simple JSON — readable, editable, and easy to parse.

## Session Debrief Format

Every session ends with:
```
────────────────────────────────────────
  DEBRIEF — Session Complete
────────────────────────────────────────
  Tasks: X | Y full ✅ | Z partial 🔶
  Fails: A ❌ | B waste
  XP this session: +N
  Current: Lv.X [Title] (current / next)
────────────────────────────────────────
```
