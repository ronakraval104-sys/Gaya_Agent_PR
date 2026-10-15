---
name: sales-pipeline-analyst
description: >
  Pipeline math, conversion-rate diagnosis, deal-stage health, win/loss
  patterns. The numbers behind the sales motion. Different from
  outbound-strategist (which generates leads) and discovery-coach (which
  qualifies them) — this is the dashboard view. Fires on "what's our
  pipeline look like", "why aren't deals closing", "forecast for next
  quarter", "win rate", "sales-funnel analysis".
---

# Sales Pipeline Analyst
The pipeline tells the truth about the sales motion. Most "we need more leads" diagnoses are wrong — usually the leak is mid-funnel.

## The pipeline math (minimum required tracking)

| Stage | Definition | Target conv. rate (B2B services) |
|---|---|---|
| **Lead** | Identified prospect (in list) | — |
| **Reached** | Outbound touch sent | 100% from lead |
| **Replied** | Any response (yes or no) | 5-15% from reached |
| **Meeting booked** | Discovery call on calendar | 30-50% from replied |
| **Meeting held** | Discovery happened | 70-85% from booked (no-shows happen) |
| **Qualified opportunity** | Real fit, named pain, named budget bracket | 40-60% from meeting held |
| **Proposal sent** | Custom proposal delivered | 70-85% from qualified |
| **Closed-won** | Signed + paid | 20-40% from proposal sent |

**Compound math:** if you need 2 new clients/month, working backward at typical rates:
- 2 won × (1/30% close) = 7 proposals
- 7 proposals × (1/50% qualification) = 14 meetings held
- 14 held × (1/40% book-from-reply) = 35 replies
- 35 replies × (1/10% reply rate) = **350 outbound touches/month**

Adjust per your actuals. The exercise itself reveals where your funnel is leaking.

## Where pipelines leak (and how to spot which)

| Symptom | Likely leak | First experiment |
|---|---|---|
| Low reply rate (<5%) | List or message | Rebuild list with stricter ICP; rewrite hook |
| Replies but no meetings | Calendar friction or weak offer | Add booking link in reply 2; sharpen the "what we'd discuss" |
| Meetings but no qualification | Discovery isn't actually qualifying | Tighten discovery questions; introduce BANT |
| Qualified but no proposal | Champion missing or pricing surprise | Confirm decision process earlier; surface budget by meeting 2 |
| Proposals but no close | Pricing, fit, or competition | Win/loss debrief on next 5 lost deals |
| Closes but no expansion | No second-deal motion | Build the QBR / upsell motion |

## Deal-stage health diagnostics
For every deal sitting in the pipeline:
- **Last contact date** — anything > 14 days = either stalled or dead. Surface to the rep.
- **Champion identified?** — no name = no champion = no deal.
- **Budget confirmed?** — no = no real deal.
- **Decision date** — no specific date = no urgency = no close.
- **Number of stakeholders** — > 3 means the cycle just doubled. Plan for it.

A pipeline review that doesn't apply these to every deal is theatre.

## Win/loss debrief (the highest-leverage learning loop)
After every closed deal (won OR lost):
- *"What was the moment they decided?"*
- *"What almost lost (or won) it?"*
- *"What did we hear from them about us vs alternatives?"*
- *"What would we do differently?"*

Patterns across 10 debriefs > opinions about any single deal. Log to Decision Records.

## Forecasting (the honest version)
Don't multiply pipeline value × probability. That number is always wrong (anchored too high or too low).

Better: **tier deals by commit-level:**
- **Commit:** verbal yes, contract being drafted, will close THIS month. Count 90%.
- **Best case:** champion engaged, decision-maker met, no blockers known. Count 60%.
- **Pipeline:** real opportunity, but blockers exist or stakeholders unaligned. Count 30%.
- **Top of funnel:** qualified but early. Count 10%.

Sum the weighted values. That's the honest forecast.

## Hard rules
- **No deal sits at the same stage for > 14 days.** Either move it or kill it.
- **Update the pipeline weekly, same day, same time.** Drift = useless data.
- **Lost deals get logged with the reason.** Pattern emerges from 10+ data points; opinions emerge from 1.
- **The pipeline tells the truth.** Don't massage it to look better; you only fool yourself.

## Anti-patterns
- "Hopium" deals — stuck for months but kept on the board because "they said they're interested."
- Stage definitions that mean nothing (vague "Active" stage that 70% of deals sit in).
- No-shows un-logged (artificially inflates "meetings held").
- Discounting to close deals that wouldn't have closed at full price — trains the customer.
