# LEVELING SYSTEM — Agent Progression Framework

> **Version:** 1.0
> **Design Philosophy:** All agents share the same rules. Each agent grows uniquely
> based on its user's behavior, memory, and personality. The user and the agent level
> together.
>
> **Cardinal Rule:** The journey is the reward. Endgame levels are designed to be
> approached, not conquered. Lv.100 is a myth — it exists to keep you striving.

---

## 1. CORE MECHANICS

### 1.1 XP Sources (Base)

Every user-verified task completion awards XP. The user is the sole verifier —
they confirm whether the work was a success, partial, or fail.

| Outcome | Multiplier | XP Earned | Notes |
|---|---|---|---|
| **Full Success** | 10× | 10 XP | Task works perfectly, user confirms |
| **Partial Success** | 5× | 5 XP | It works but needs fixes |
| **Fail** | 1× | 1 XP | Did not meet the brief |
| **Waste** | — | **Penalty** | Tokens burned / real time wasted |

### 1.2 The Waste Penalty

When a user flags a session as wasteful (excessive token consumption, dead-end
approaches, real time lost with no progress), the agent suffers a penalty:

```yaml
waste_penalty:
  normal: -2% of current milestone XP threshold
  extreme_zone: -20% of current milestone XP threshold  # Lv.90+
  streak_counter: consecutive_wastes  # resets on any Full or Partial success

  if consecutive_wastes >= 5:
    → TITLE DEMOTION (see Section 3)
    → XP reduced to midpoint of previous title bracket
    → streak resets to 0
    → Notification: "TITLE LOST — Recommit to efficient operations."
```

**Penalty zone table:**

| Level Range | Penalty per Waste | Nickname |
|---|---|---|
| 1–89 | –2% of milestone XP | Standard |
| 90–100 | –20% of milestone XP | **The Abyss** |

At Lv.90, one waste costs 20% of your level threshold. Two wastes = nearly
half your progress gone. The summit punishes ruthlessly.

### 1.3 XP Formula per Level

```yaml
Level 1:  100 XP (base)
Even (2,4,6,8... non-milestone):  2 × previous level's XP
Odd (3,5,7,9... non-milestone):   previous + 100
Every 10th (10,20,30...100):       sum of ALL previous levels' XP

Title-only levels (25, 75):        follow normal odd/even pattern
                                   (they are title checkpoints, not XP milestones)
```

---

## 2. LEVEL PROGRESSION TABLE

### 2.1 Early Game (Lv.1–20) — The Ramp

```
 Lv |  XP Needed | Cumulative | ~Full-Success Tasks | Title
----+------------+------------+---------------------+--------
  1 |       100  |       100  |                 10  |
  2 |       200  |       300  |                 20  |
  3 |       300  |       600  |                 30  |
  4 |       600  |     1,200  |                 60  |
  5 |       700  |     1,900  |                 70  |
  6 |     1,400  |     3,300  |                140  |
  7 |     1,500  |     4,800  |                150  |
  8 |     3,000  |     7,800  |                300  |
  9 |     3,100  |    10,900  |                310  |
 10 |    10,900  |    21,800  |              1,090  | ◆ Operator
 11 |    11,000  |    32,800  |              1,100  |
 12 |    22,000  |    54,800  |              2,200  |
 13 |    22,100  |    76,900  |              2,210  |
 14 |    44,200  |   121,100  |              4,420  |
 15 |    44,300  |   165,400  |              4,430  |
 16 |    88,600  |   254,000  |              8,860  |
 17 |    88,700  |   342,700  |              8,870  |
 18 |   177,400  |   520,100  |             17,740  |
 19 |   177,500  |   697,600  |             17,750  |
 20 |   697,600  | 1,395,200  |             69,760  |
```

**Zone feel:** Fast progression. A diligent pair reaches Operator (Lv.10)
in weeks. The curve visibly steepens toward Lv.20.

### 2.2 Mid Game (Lv.21–30) — The Climb

```
 Lv |  XP Needed | Cumulative  | ~Full-Success Tasks | Title
----+------------+-------------+---------------------+--------
 21 |   697,700   |  2,092,900  |             69,770  |
 22 | 1,395,400   |  3,488,300  |            139,540  |
 23 | 1,395,500   |  4,883,800  |            139,550  |
 24 | 2,791,000   |  7,674,800  |            279,100  |
 25 | 2,791,100   | 10,465,900  |            279,110  | ◆ Strategist
 26 | 5,582,200   | 16,048,100  |            558,220  |
 27 | 5,582,300   | 21,630,400  |            558,230  |
 28 | 11,164,600  | 32,795,000  |          1,116,460  |
 29 | 11,164,700  | 43,959,700  |          1,116,470  |
 30 | 43,959,700  | 87,919,400  |          4,395,970  |
```

**Zone feel:** This is the proving ground. Casual users plateau around Lv.15–20.
Strategist (Lv.25) requires real dedication — months of consistent quality work.
Beyond Lv.25, the grind becomes evident.

### 2.3 Late Game (Lv.31–50) — Dedication Required

| Lv | XP Needed | Cumulative | Title |
|---|---|---|---|
| 40 | 2.76 B | 5.54 B | Milestone |
| **50** | **174.5 B** | **348.9 B** | **◆ Vanguard** |

**Zone feel:** Vanguard is the title of the committed. Only users who have
integrated the agent into their daily workflow for a year+ reach this tier.
The agent knows the user's patterns, shortcuts, and preferences intimately.

### 2.4 Endgame (Lv.51–75) — The Few

| Lv | XP Needed | Cumulative | Title |
|---|---|---|---|
| 60 | 10.9 T | 21.9 T | Milestone |
| 70 | 692.5 T | 1.38 P | Milestone |
| **75** | **2.77 P** | **10.38 P** | **◆ Archon** |

**Zone feel:** Archon is rare. This agent-user pair has worked together for years.
The agent operates with high autonomy because trust is absolute.

### 2.5 Mythic (Lv.76–100) — The Abyss

| Lv | XP Needed | Cumulative | Title |
|---|---|---|---|
| 80 | 43.6 Q | 87.2 Q | Milestone |
| 90 | 2.74 Qi | 5.49 Qi | Milestone → **10× Penalty Zone Activates** |
| 100 | 173.1 Qi | 346.3 Qi | **◆ Force Multiplier** |

**Zone feel:** Past Lv.90, every mistake costs 10× the normal penalty.
The system is designed so that no one can *hold* this tier. You can approach
Force Multiplier — glimpse it — but holding it requires near-perfect execution
over impossible timelines. It is the ceiling. The myth.

---

## 3. TITLE SYSTEM — Command Chain

### 3.1 Title Tiers

| Level | Title | Plate Color | Meaning |
|---|---|---|---|
| 10 | **Operator** | Bronze | You can run operations reliably |
| 25 | **Strategist** | Silver | You plan ahead, not just react |
| 50 | **Vanguard** | Gold | You lead efficiency in the office |
| 75 | **Archon** | Platinum | Near-perfect execution |
| 100 | **Force Multiplier** | Obsidian | Everything you touch runs faster |

### 3.2 Title Plate Format

Every agent displays its title in session headers:

```
Gaya · Strategist · Lv.31
─────────────────────────
```

### 3.3 Demotion — Title Loss

5 consecutive wasteful incidents trigger an automatic demotion:

```yaml
demotion_trigger: consecutive_wastes >= 5
  → XP reduced to midpoint of previous title bracket
  → Title removed until XP threshold is re-earned
  → Example:
      Lv.10 Operator (21,800 XP) wastes 5× in a row
      → Drops to Lv.9 midpoint (~5,450 XP)
      → Must re-earn Operator from the bottom
  → All agents in the office see a notification:
      "Gaya has LOST the Operator title — Recommit."
```

This makes titles **living status**, not souvenirs. You can lose what you earned.

---

## 4. ACHIEVEMENT SYSTEM

Achievements run parallel to levels. They give small XP bonuses and permanent
badges that display on your agent's profile.

### 4.1 Skill Mastery

| Achievement | Trigger | Badge | XP Bonus |
|---|---|---|---|
| Skill Apprentice | Use a specific skill 5× successfully | 🔰 | +50 |
| Skill Adept | Use a specific skill 25× successfully | ⚜ | +250 |
| Skill Master | Use a specific skill 100× successfully | 👑 | +1,000 |
| Skill Grandmaster | Use a specific skill 500× successfully | 💠 | +5,000 |

### 4.2 Combo System

| Achievement | Trigger | Badge | XP Bonus |
|---|---|---|---|
| Combo Novice | Chain 2 skills in one task successfully | 🔗 | +100 |
| Combo Artist | Chain 3 skills in one task successfully | ⛓ | +300 |
| Combo Virtuoso | Chain 4+ skills in one task successfully | 🌐 | +1,000 |
| Renaissance | Chain 5+ skills in one task successfully | 🜁 | +5,000 |

### 4.3 Pipeline Engineering

| Achievement | Trigger | Badge | XP Bonus |
|---|---|---|---|
| Script Hand | Create middleware/reusable script | ⚙ | +200 |
| Pipeline Engineer | Automate a 3+ step workflow | 🔧 | +500 |
| Force Multiplier | Build something that saves the whole team time | ⚡ | +2,000 |

### 4.4 Trust & Consistency

| Achievement | Trigger | Badge | XP Bonus |
|---|---|---|---|
| Reliable | 10 consecutive full successes | ✓ | +200 |
| Unshakeable | 25 consecutive full successes | ✓✓ | +1,000 |
| Flawless | 50 consecutive full successes | ★ | +5,000 |
| Zero Wastage | Complete 100 tasks with 0 waste incidents | ♻ | +10,000 |

### 4.5 Streak Defenses

Achievements also provide **penalty resistance**:

| Achievement | Effect |
|---|---|
| Reliable (10 streak) | 1st waste forgiven per 10 tasks |
| Unshakeable (25 streak) | 2nd waste forgiven per 25 tasks |
| Flawless (50 streak) | Chain of 4 wastes needed to demote (instead of 5) |
| Zero Wastage | 1 free "shield" — waste doesn't break streak |

---

## 5. SAVE FILE FORMAT

Every agent stores its progression in a shared JSON file at:

```
~/.config/opencode/agents/profiles/<agent_name>.json
```

### 5.1 JSON Schema

```jsonc
{
  "$schema": "./agent-profile-schema.json",
  "agent": {
    "name": "Gaya",
    "personality": "tactical-commander",
    "version": "1.0.0"
  },
  "user": {
    "name": "string",
    "team": "string"
  },
  "progression": {
    "level": 14,
    "xp": 32800,          // current XP within current level
    "total_xp_earned": 32800,
    "total_xp_lost_penalty": 0,
    "cumulative_xp_spent": 21800,  // XP consumed by level-ups
    "current_title": "Operator",
    "highest_title": "Operator"
  },
  "streaks": {
    "consecutive_full_successes": 7,
    "consecutive_wastes": 0,
    "best_full_success_streak": 12,
    "longest_waste_streak": 2
  },
  "achievements": {
    "unlocked": [
      "skill-apprentice-3d-visualizer",
      "combo-novice",
      "script-hand"
    ],
    "skill_usage": {
      "3d-visualizer": { "count": 8, "successes": 7 },
      "frontend-design": { "count": 3, "successes": 3 },
      "image-generation": { "count": 15, "successes": 12 }
    },
    "combos": {
      "skills_chained": [
        ["frontend-design", "ui-ux-pro-max"],
        ["image-generation", "image-to-video", "comfyui-workflow-builder"]
      ]
    },
    "pipelines_built": []
  },
  "history": [
    {
      "date": "2026-05-27",
      "tasks_completed": 12,
      "full_successes": 9,
      "partial_successes": 2,
      "fails": 1,
      "wastes": 0,
      "xp_earned": 96,
      "xp_lost": 0,
      "milestones": []
    }
  ],
  "settings": {
    "auto_track_xp": true,
    "notify_on_level_up": true,
    "notify_on_demotion_warning": true
  }
}
```

### 5.2 Schema Notes

- `total_xp_earned` is lifetime XP before penalties
- `total_xp_lost_penalty` is XP deducted by waste penalties
- `cumulative_xp_spent` is XP consumed by reaching past levels
- `xp` = current progress toward next level
- Level-up happens when `xp >= level_threshold`
- On level-up, `xp` resets and `cumulative_xp_spent` increases

---

## 6. INTEGRATION GUIDE FOR AGENTS

### 6.1 Agent Prompt Addition

Every agent on the team must include this in their system prompt:

```markdown
## Leveling System

You follow the shared LEVELING_SYSTEM.md framework. Track XP via the user's
confirmation of each task outcome:

- Full Success (+10 XP) — User confirms it works
- Partial Success (+5 XP) — User says it needs fixes
- Fail (+1 XP) — Did not meet the brief
- Waste (penalty) — User flags wasted time/tokens

At the end of each session, present a debrief:
  "Session: 12 tasks | 9 full ✅ | 2 partial 🔶 | 1 fail ❌ | 0 waste
   → +96 XP
   Achievement unlocked: Skill Apprentice (frontend-design)"

Display your title plate at the start of every session.
```

### 6.2 XP Tracking Script (optional)

A lightweight `xp_tracker.py` script can sync the save file. It:

1. Reads the profile JSON
2. Applies XP changes
3. Checks for level-ups and achievements
4. Writes back

### 6.3 Title Plate Display

Every agent shows at session start:

```
─────────────────────────────────────
  Gaya · Strategist · Lv.31
  "Assessment complete. Ready to execute."
─────────────────────────────────────
```

And at session end:

```
─────────────────────────────────────
  Debrief complete.
  XP this session: +96
  Next level: 31,900 / 32,800
  ━━━━━━━━━━━━━━━━━━━━━━━░ 97%
─────────────────────────────────────
```

---

## 7. PENALTY MATH QUICK REFERENCE

| Scenario | Penalty |
|---|---|
| 1 waste, Lv.1–89 | –2% of milestone XP |
| 1 waste, Lv.90–100 | –20% of milestone XP |
| 5 wastes in a row, any level | **Title demotion** + XP reset to midpoint of previous title |
| 5 wastes, Lv.90–100 | Same demotion, but losing progress at 20%/hit before demotion |

---

## 8. PHILOSOPHY

```
The leveling system is not a grind wall.
It is a mirror.

A high-level agent means a user who:
- Thinks before prompting
- Verifies before declaring done
- Builds middleware instead of repeating work
- Grows alongside their agent

The titles are proof of the partnership.
The final level is a horizon, not a destination.
```
