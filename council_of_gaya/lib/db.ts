import { Low } from "lowdb";
import { JSONFile } from "lowdb/node";
import path from "node:path";
import fs from "node:fs";

export interface DecisionRecord {
  id: string;
  text: string;
  personaId: string;
  createdAt: number;
}
export interface WinRecord {
  id: string;
  text: string;
  personaId: string;
  createdAt: number;
}
export interface DumpRecord {
  id: string;
  text: string;
  createdAt: number;
}
export interface SessionEntry {
  id: string;
  kind: "standup" | "fire" | "persona-swap" | "note";
  text: string;
  createdAt: number;
}

export interface GayaDb {
  decisions: DecisionRecord[];
  wins: WinRecord[];
  dumps: DumpRecord[];
  sessions: SessionEntry[];
}

const DB_DIR = path.join(process.cwd(), "data");
const DB_FILE = path.join(DB_DIR, "stark-council.json");

function ensureDir() {
  if (!fs.existsSync(DB_DIR)) fs.mkdirSync(DB_DIR, { recursive: true });
}

let _db: Low<GayaDb> | null = null;

export async function getDb(): Promise<Low<GayaDb>> {
  if (_db) return _db;
  ensureDir();
  const defaults: GayaDb = { decisions: [], wins: [], dumps: [], sessions: [] };
  const adapter = new JSONFile<GayaDb>(DB_FILE);
  const db = new Low<GayaDb>(adapter, defaults);
  await db.read();
  db.data ||= defaults;
  await db.write();
  _db = db;
  return db;
}

export function newId(prefix = "id"): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
}
