# Council of Gaya — Operator Dashboard

Next.js 14 operator console at `http://localhost:4200`. Gaya's Command Core on a screen: the living knowledge base (threads, decisions, gotchas, domain laws, wins), real-time connectors (Antigravity harness, Mini Gaya desktop sprite, GPU telemetry, Skills armory, MCP servers, ComfyUI), council specialists (Logos, Bob, Freya, Tvashtar, Archivist, Sage, Oracle), session chronicle, and live state in the top bar (`/api/gaya-state`).

## Setup & Running

```bash
npm install
npm run ingest     # ingests OMNI_GAYA_MEMORY.md -> data/knowledge.json
npm run dev        # starts on port 4200
```

Alternatively, launch the automated detached runner:
```bash
python launch_dashboard.py
```
