# Stark Council — operator dashboard

Next.js 14 app at `http://localhost:4200`. JARVIS's face on a screen: the knowledge base (every memory
record, ingested and classified), connectors (GitHub, sites, Metricool, pricing), the council seats,
session chronicle, and mini J's live state in the top bar (`/api/jarvis-state`).

```
npm install
npm run ingest     # memory records -> data/knowledge.json (gitignored - contains identities)
npm run dev
```

Branches of record: `feature/monolith-signal` (current look), `feature/stark-council` (earlier).
