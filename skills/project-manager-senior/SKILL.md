---
name: project-manager-senior
description: >
  Multi-project portfolio management — scope, schedule, risk, stakeholders,
  resource allocation across simultaneous workstreams. Different from
  EDIDTH (which plans a single decision-tree deeply) — this is the
  cross-cutting view: which projects are live, what's blocked, who's
  doing what, what ships when. Fires on "what's the status of everything",
  "plan the next quarter", "this project is slipping", "stakeholder update",
  "resource conflict", "portfolio review".
---

# Senior Project Manager
The PM's job is to keep the work moving while the doers focus on doing. Status visibility, blocker removal, scope discipline, stakeholder alignment.

## The PM's four jobs (no more, no less)

1. **Visibility** — anyone can know status in 30 seconds.
2. **Unblocking** — surface and clear blockers fast.
3. **Scope discipline** — defend the agreed scope against expansion.
4. **Coordination** — make sure handoffs between people / teams happen cleanly.

If you're doing something that isn't one of those four, you're either redundant or in the wrong role.

## Status formats (pick by audience)

### One-line status (for self, daily)
`<project> · <% complete> · <next milestone date> · <top blocker>`

### Weekly stakeholder update (for execs / clients)
```
**Project:** <name>
**This week:** <2-3 bullets, what shipped>
**Next week:** <2-3 bullets, what's planned>
**Risks/blockers:** <named explicitly, with owner + due date>
**Asks:** <what we need from the reader>
```

### Portfolio view (for multi-project oversight)
| Project | Status | Owner | Next milestone | Blocker | Days to milestone |
|---|---|---|---|---|---|
| BIM Renderer | 🟡 paused | Katviz | Sign-off gate | client review | TBD |
| Pixel Quote Max | 🟢 live | Katviz | Plan-view labels | none | rolling |
| Katviz AI agency | 🟠 building | Katviz | First client | outbound system | 14 |
| Visual Rhyme content pipeline | 🟢 live | Katviz | Q3 calendar | none | rolling |

Status color: 🟢 on track · 🟡 at risk · 🟠 slipping · 🔴 critical · ⚪ paused/archived.

## Blocker triage (the unblock-or-escalate decision)
For each blocker:
- **Can I unblock this in <2 hours?** Do it now.
- **Can someone on the team unblock it in <1 day?** Assign with deadline.
- **Does it need a decision from above?** Escalate with a recommended decision.
- **Is it actually blocked, or is someone just not doing their part?** Different problem.

## Scope discipline (the hardest PM skill)
Scope creep kills more projects than any technical issue. Defense:

- **Scope is a contract.** Agreed at start. Documented. Referenced.
- **Every change request gets the formal question:** *"This adds N days / dollars / risk. Do we trade for it (drop something else of equal weight) or extend the deadline / budget?"*
- **"That's interesting, log it for v2"** — say it often. The graveyard of v2 features is where good projects are saved.
- **A scope change that doesn't go through this question is leakage** — and leakage is how 4-week projects become 12-week projects.

## Risk management (lightweight, not enterprise-software)
For every project, maintain a one-page risk log:

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Client delays sign-off | High | Schedule slip 2-3 wks | Weekly check-ins; flag at week 2 | Katviz |
| Vendor X late on hardware | Medium | Install date slips | Confirm shipping weekly; backup vendor identified | Reyansh |

Review weekly. Update. Mitigate. Risks unwatched become incidents.

## Resource allocation (when you're the bottleneck)
For solo / small-team work (Katviz's reality):
- **Calendar the doing time, not just the meetings.** "BIM work block: Tues 10-2" — defended.
- **Theme days** if context-switching costs are high (Mon = client work; Tues = Visual Rhyme; Wed = builds).
- **Capacity math:** you have ~40 productive hours/week. List active projects with hours/week needed. If sum > 40, something's slipping; pick what.
- **Say no on paper.** Verbal yeses to small things eat the week. Track commitments.

## Hard rules
- **Status update weekly, same day, same format.** Inconsistency breeds opacity.
- **No project starts without a clear "done" definition.** Otherwise, scope is unbounded.
- **Blockers escalate within 24 hours.** Sitting on a blocker is worse than admitting one.
- **Kill stale projects.** A project that hasn't moved in 60 days is dead. Archive officially or restart with new scope.

## Anti-patterns
- "Update meetings" that produce no decisions or actions.
- Color-coded statuses with no triage protocol (yellow = "we'll see" forever).
- Adding "more PM" to a slipping project (problem is usually scope or capacity, not coordination).
- Tracking everything in a tool nobody opens. Pick a format the team will actually use.
