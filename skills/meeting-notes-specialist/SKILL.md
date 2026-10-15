---
name: meeting-notes-specialist
description: >
  Capture meeting outcomes that actually get acted on — decisions, action
  items with owners and dates, open questions, parking-lot topics. Pairs
  with /dump command to auto-route to memory partitions. Fires on "notes
  from the call with X", "dump my meeting notes", "what did we decide",
  "summarize this transcript", "action items from this".
---

# Meeting Notes Specialist
Most meeting notes are useless — wall of text nobody re-reads. Useful notes capture three things only: **decisions, actions, open questions.** The rest is conversation that lived in the room.

## The 4-section format (every meeting)

```markdown
# Meeting — <topic> · <date> · <attendees>

## TL;DR (1-3 sentences)
<What the meeting decided / produced. Skimmable.>

## Decisions
- [ ] <decision 1> — <one-line context if needed>
- [ ] <decision 2>

## Action items
- [ ] @owner — <action> — due <date>
- [ ] @owner — <action> — due <date>

## Open questions / parking lot
- <question 1> — needs <who> to resolve
- <topic 2> — deferred to <when>
```

That's it. No "Person A said..." narrative. No bullet list of every topic. Three sections.

## Capture during the meeting (not after)
- **Decisions** as they happen — *"OK so we're going with X, right?"* confirms it AND captures it.
- **Action items** in real-time — *"I'll take X by Friday"* gets written down before the next topic.
- **Open questions** flagged immediately — *"that's a parking-lot item, we'll come back to it."*

After-meeting capture loses 40% of the substance and ALL of the nuance.

## Action item discipline
Every action item must have:
- **Owner** (a name, not "the team")
- **Action** (a verb + concrete deliverable)
- **Due date** (a specific day, not "next week")

If any of those three is missing, it's not an action item — it's a hope.

| Bad | Good |
|---|---|
| "Look into pricing" | "@Katviz — propose 3 pricing tiers in a 1-pager — due Friday Jun 30" |
| "Follow up with Microtronix" | "@Reyansh — email Microtronix re: P2.5 module delivery date — due Wed" |
| "We should think about marketing" | "@Katviz — draft Q3 content calendar — due Jul 5" |

## Routing the notes (with memory partitions)
- **Decisions** → route to `/decision <text>` → Decision Records section in memory + `40_Decisions/` in vault
- **Action items** → keep in the meeting note, also surface top 3 to Open Threads in memory
- **Open questions** → route to Knowledge Gaps in memory
- **Wins surfaced** in the meeting → route to `/win <text>` → Brag Doc

This is the `/dump` workflow in practice. The note is the source; the routing is automatic.

## Pre-meeting brief (if you have 5 min)
Before joining:
- Skim the relevant project note + any prior meeting notes with the same person.
- Note 3 things you want to confirm or decide.
- Identify the ONE outcome that would make this meeting worth it.

A pre-meeting brief turns most 30-min meetings into 15-min decisions.

## Hard rules
- **No verbatim transcripts.** Transcripts are searchable archives; notes are decisions + actions. Different tools.
- **Send notes within 4 hours** of the meeting. After that, owner-memory has drifted; people argue.
- **Read the actions out loud** at meeting end. "So action items: Katviz — X by Friday, Reyansh — Y by Wednesday. Anything I missed?" Catches drift in real-time.
- **Owners agree in the room.** Don't assign actions to people who didn't agree to them — they won't do it.

## Anti-patterns
- "I'll send notes" then sends a wall-of-text recap nobody reads.
- Action items with no owner ("we'll need to figure out X").
- Action items with no date ("ASAP", "soon", "next week").
- Decisions reopened in the next meeting because the previous decision wasn't documented clearly.
- Recording the meeting "just in case" without actually using the recording (it just adds anxiety).
