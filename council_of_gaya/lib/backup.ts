import fs from "node:fs";
import path from "node:path";

const DB_DIR = path.join(process.cwd(), "data");
const DB_FILE = path.join(DB_DIR, "stark-council.json");
const BACKUP_DIR = path.join(DB_DIR, "backups");

function stamp() {
  const d = new Date();
  return d.toISOString().replace(/[:.]/g, "-");
}

if (!fs.existsSync(DB_FILE)) {
  console.log("[backup] no db file yet — nothing to back up");
  process.exit(0);
}
if (!fs.existsSync(BACKUP_DIR)) fs.mkdirSync(BACKUP_DIR, { recursive: true });
const target = path.join(BACKUP_DIR, `stark-council.${stamp()}.json`);
fs.copyFileSync(DB_FILE, target);
console.log(`[backup] snapshot -> ${target}`);
