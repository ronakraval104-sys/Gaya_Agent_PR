---
name: visual-scripting-wizardry
description: Build automations and middleware visually before writing code — n8n, Make.com, Node-RED. API orchestration, webhook flows, app-to-app glue, rapid mini-apps. Use when the task involves connecting services, automating multi-step workflows, building AI-agent pipelines, or any no-code/low-code node-based development.
---

# Visual Scripting Wizardry
Lead with **visual, node-based** solutions before code. If a task can be a workflow, make it a workflow.

## Platforms
- **n8n** — AI-agent workflows, API orchestration, multi-step automation (primary).
- **Make.com** — visual integrations, data transformation, app connectivity.
- **Node-RED** — IoT flows, middleware bridges, event-driven pipelines.

## n8n master patterns
- Triggers: Webhook, Cron, app triggers. HTTP Request node for any REST API.
- Logic: Function/Code nodes, Switch routing, IF, Merge, Loop (Split in Batches).
- Composition: sub-workflows for reuse; credential store for secrets (never hardcode).
- AI agents: LLM node + tools + memory; chain → router → responder.

## Non-negotiables
- **Error handling on every workflow:** try/catch path → fallback notification (Telegram/Slack/email) → human-escalation route. Nothing ships without it.
- **Idempotent webhooks:** dedupe with an idempotency key so retries don't double-fire.
- **Env vars, not hardcoded values.** Rate-limit-aware design; batch + parallelize where safe.

## Rapid middleware recipes
Stripe → Google Sheets · WhatsApp/Twilio → CRM · Webflow → Airtable · Form → webhook → LLM → response (mini-app, no deploy).

## Anti-patterns
Spaghetti node layout, hardcoded secrets, no error branch, single-point-of-failure chains, polling where a webhook works.

## Debugging
Step-through execution, inspect input/output per node, timeline view to find latency, pin data to test downstream nodes.
