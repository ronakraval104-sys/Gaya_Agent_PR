# PROJECT GOTCHAS — Online Edition

**Purpose:** Lessons learned running Gaya via cloud API.
**Last updated:** 08-Jun-2026

---

## Models & Providers

| Date | Gotcha | Impact | Fix |
|---|---|---|---|
| 2026-06 | **Free models are promotional.** They can be removed or rate-limited at any time without notice. | Lost access to a preferred model mid-session. | Always have a backup model configured. Check the Zen model list regularly. |
| 2026-06 | **Context limits differ per model.** Big Pickle caps at 200K — large conversations get truncated. | Lost context in long sessions. | Stay aware of model context limits. Use MiMo V2.5 or Nemotron 3 (1M) for long conversations. |
| 2026-06 | **API keys must use env vars.** Hardcoding keys in config risks exposure on public repos. | Security risk. | Always use `$OPENCODE_API_KEY` or equivalent. Never commit keys. |

## Configuration

| Date | Gotcha | Impact | Fix |
|---|---|---|---|
| 2026-06 | **Plugin and skill paths differ** between local and cloud setups. Superpowers plugin via git+https works in both. | Skills not found after switching config. | Document skill install method for each environment. Use plugin system for portability. |
| 2026-06 | **Model IDs change.** What's `mimo-v2.5-free` today may be `mimo-v3-free` tomorrow. | Config breaks after model deprecation. | Pin model IDs in config. Monitor the Zen model list for deprecation dates. |

## Best Practices

| Date | Gotcha | Impact | Fix |
|---|---|---|---|
| 2026-06 | **Don't send sensitive data through free tiers.** Provider logs prompts during evaluation. | Privacy risk. | Use paid tiers or local deployment for sensitive work. Free tier = assume everything is logged. |
| 2026-06 | **Rate limits exist on free models.** Aggressive use gets throttled. | Unexpected downtime. | Implement exponential backoff. Spread requests across models. |

---

*Every L is XP if you write it down. Update this file as new lessons are learned.*
