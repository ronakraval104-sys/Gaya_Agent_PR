# PROJECT DOMAIN LAWS — Online Edition

**Purpose:** Non-negotiable constraints when running Gaya via cloud API.
**Last updated:** 08-Jun-2026

---

## General

- **API costs are real.** Free models may be rate-limited or deprecated. Monitor usage.
- **Never hardcode API keys.** Use environment variables (`OPENCODE_API_KEY`, etc.).
- **Context windows vary by model.** Big Pickle: 200K. MiMo V2.5 & Nemotron 3: 1M.
- **Free models are promotional.** They can be removed or rate-limited at any time. Have a fallback plan.
- **All prompts and output may be logged** by model providers during free evaluation periods. Do not send sensitive/confidential data through free-tier endpoints.
- **Token tracking after every action** — log input/output/tool counts. Report in debrief.

## Agent-Specific

| Agent | Constraint |
|---|---|
| Gaya (Big Pickle) | 200K context limit. Strategic reasoning. |
| Freya (MiMo V2.5 Free) | 1M context. Omnimodal (text + image + video + audio). Higher temp for creativity. |
| Bob (Nemotron 3 Super Free) | 1M context. Precision coding. Low temp (0.2). |

## Session Management

- **8-hour session limit** — remind at 2h, 4h, 6h, force stop at 8h.
- **Monitor rate limits** — free tier may have request caps. If rate-limited, back off and retry.
- **Model deprecation** — check OpenCode Zen model list periodically. Some models cycle out.
- **XP is tracked** in `agents/profiles/gaya.json`. Sync if using across machines.

---

*These laws apply to the cloud-operated version of Gaya. Local/offline deployments may have different constraints.*
