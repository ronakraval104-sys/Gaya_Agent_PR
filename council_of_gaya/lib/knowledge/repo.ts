import { Low } from "lowdb";
import { JSONFile } from "lowdb/node";
import path from "node:path";
import fs from "node:fs";
import type { KnowledgeRecord, PersonaScope, MemoryType, Priority } from "./types";
import { classifySeat } from "./classifier";
import type { CouncilSeatId } from "../council";

export interface KnowledgeDb {
  records: KnowledgeRecord[];
  meta: {
    lastIngestAt?: number;
    lastIngestReport?: any;
  };
}

const DB_DIR = path.join(process.cwd(), "data");
const DB_FILE = path.join(DB_DIR, "knowledge.json");

function ensureDir() {
  if (!fs.existsSync(DB_DIR)) fs.mkdirSync(DB_DIR, { recursive: true });
}

let _db: Low<KnowledgeDb> | null = null;

export async function getKnowledgeDb(): Promise<Low<KnowledgeDb>> {
  if (_db) return _db;
  ensureDir();
  const defaults: KnowledgeDb = { records: [], meta: {} };
  const db = new Low<KnowledgeDb>(new JSONFile<KnowledgeDb>(DB_FILE), defaults);
  await db.read();
  db.data ||= defaults;
  _db = db;
  return db;
}

export async function replaceAll(records: KnowledgeRecord[], report: any): Promise<void> {
  const db = await getKnowledgeDb();
  db.data!.records = records;
  db.data!.meta.lastIngestAt = Date.now();
  db.data!.meta.lastIngestReport = report;
  await db.write();
}

export async function addRecord(record: KnowledgeRecord): Promise<void> {
  const db = await getKnowledgeDb();
  db.data!.records.push(record);
  await db.write();
}

export interface ListFilter {
  type?: MemoryType;
  persona?: PersonaScope;
  priority?: Priority;
  tag?: string;
  q?: string;
  seat?: CouncilSeatId;
}

export async function list(filter: ListFilter = {}): Promise<KnowledgeRecord[]> {
  const db = await getKnowledgeDb();
  await db.read(); // pick up out-of-band writes (npm run ingest)
  let rows = db.data?.records ?? [];
  if (filter.type) rows = rows.filter((r) => r.type === filter.type);
  if (filter.persona) rows = rows.filter((r) => r.persona === filter.persona);
  if (filter.priority) rows = rows.filter((r) => r.priority === filter.priority);
  if (filter.tag) rows = rows.filter((r) => r.tags.includes(filter.tag!));
  if (filter.seat) rows = rows.filter((r) => classifySeat(r) === filter.seat);
  if (filter.q) {
    const q = filter.q.toLowerCase();
    rows = rows.filter(
      (r) =>
        r.title.toLowerCase().includes(q) ||
        r.description.toLowerCase().includes(q) ||
        r.slug.includes(q) ||
        r.body.toLowerCase().includes(q)
    );
  }
  // Prioritize by priority then persona-match: boulder > high > normal
  const rank = (p: Priority) => (p === "boulder" ? 0 : p === "high" ? 1 : 2);
  return [...rows].sort((a, b) => rank(a.priority) - rank(b.priority));
}

export async function get(slug: string): Promise<KnowledgeRecord | null> {
  const db = await getKnowledgeDb();
  await db.read();
  return db.data?.records.find((r) => r.slug === slug) ?? null;
}

export async function counts(): Promise<{
  total: number;
  byType: Record<string, number>;
  byPersona: Record<string, number>;
  byPriority: Record<string, number>;
  boulderCount: number;
  brokenLinkCount: number;
  lastIngestAt?: number;
}> {
  const db = await getKnowledgeDb();
  await db.read();
  const rows = db.data?.records ?? [];
  const byType: Record<string, number> = {};
  const byPersona: Record<string, number> = {};
  const byPriority: Record<string, number> = {};
  for (const r of rows) {
    byType[r.type] = (byType[r.type] ?? 0) + 1;
    byPersona[r.persona] = (byPersona[r.persona] ?? 0) + 1;
    byPriority[r.priority] = (byPriority[r.priority] ?? 0) + 1;
  }
  return {
    total: rows.length,
    byType,
    byPersona,
    byPriority,
    boulderCount: byPriority["boulder"] ?? 0,
    brokenLinkCount: db.data?.meta?.lastIngestReport?.brokenLinks?.length ?? 0,
    lastIngestAt: db.data?.meta?.lastIngestAt
  };
}
