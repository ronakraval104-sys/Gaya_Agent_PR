import fs from "node:fs/promises";
import path from "node:path";
import { parseFrontmatter, extractWikiLinks, extractMdLinks } from "./parser";
import { classifyPersona, classifyPriority } from "./classifier";
import type { KnowledgeRecord, MemoryType } from "./types";

const DEFAULT_VAULT_ROOT = "D:/Obsedian/Gaya"; // note spelling per vault reference

// Directory prefix → type mapping (Obsidian PARA-like structure)
const DIR_TYPE_MAP: Array<{ match: RegExp; type: MemoryType; tags: string[] }> = [
  { match: /^10_Projects$/i,   type: "project",   tags: ["project", "obsidian"] },
  { match: /^20_Knowledge$/i,  type: "reference", tags: ["reference", "knowledge", "obsidian"] },
  { match: /^30_Daily$/i,      type: "thread",    tags: ["daily", "journal", "obsidian"] },
  { match: /^40_Council$/i,    type: "thread",    tags: ["council", "session", "obsidian"] },
  { match: /^40_Decisions$/i,  type: "decision",  tags: ["decision", "obsidian"] },
  { match: /^50_Wins$/i,       type: "win",       tags: ["win", "obsidian"] },
  { match: /^00_Inbox$/i,      type: "unknown",   tags: ["inbox", "capture", "obsidian"] }
];

// Files/dirs to hard-skip regardless of contents
const SKIP_PATTERNS: RegExp[] = [
  /^99_Private$/i,        // OFF-LIMITS per vault CLAUDE.md
  /^\.git$/,
  /^\.obsidian$/,
  /^snippets$/i,
  /^node_modules$/
];

const SKIP_FILES: RegExp[] = [
  /^CLAUDE\.md$/i,        // vault operating manual, meta
  /^Home\.md$/i,          // vault index page
  /^Untitled/i            // empty scratch notes
];

interface IngestOptions {
  vaultRoot?: string;
}

export interface ObsidianIngestReport {
  scannedFiles: number;
  parsedRecords: number;
  skipped: { path: string; reason: string }[];
  countsByType: Record<string, number>;
  durationMs: number;
}

function slugifyTitle(text: string, prefix: string): string {
  const base = text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 70)
    .replace(/^-|-$/g, "");
  return `${prefix}-${base || "untitled"}`;
}

function extractInlineTags(md: string): string[] {
  const tags = new Set<string>();
  // #tag (but not markdown headings, not URLs, not #123 numbers)
  const re = /(?:^|[^\w#])#([a-zA-Z][a-zA-Z0-9_\-\/]{1,40})/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(md)) !== null) {
    tags.add(m[1].toLowerCase());
  }
  return [...tags];
}

async function walk(dir: string, root: string, acc: string[] = []): Promise<string[]> {
  const entries = await fs.readdir(dir, { withFileTypes: true }).catch(() => []);
  for (const e of entries) {
    if (SKIP_PATTERNS.some((p) => p.test(e.name))) continue;
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      await walk(full, root, acc);
    } else if (e.isFile() && e.name.toLowerCase().endsWith(".md")) {
      if (SKIP_FILES.some((p) => p.test(e.name))) continue;
      acc.push(full);
    }
  }
  return acc;
}

export async function ingestObsidianVault(
  opts: IngestOptions = {}
): Promise<{ records: KnowledgeRecord[]; report: ObsidianIngestReport }> {
  const start = Date.now();
  const root = opts.vaultRoot ?? DEFAULT_VAULT_ROOT;

  const rootExists = await fs
    .stat(root)
    .then((s) => s.isDirectory())
    .catch(() => false);

  if (!rootExists) {
    return {
      records: [],
      report: {
        scannedFiles: 0,
        parsedRecords: 0,
        skipped: [{ path: root, reason: "vault-root-not-found" }],
        countsByType: {},
        durationMs: Date.now() - start
      }
    };
  }

  const files = await walk(root, root);
  const records: KnowledgeRecord[] = [];
  const skipped: ObsidianIngestReport["skipped"] = [];
  const countsByType: Record<string, number> = {};

  for (const full of files) {
    try {
      const rel = path.relative(root, full).replace(/\\/g, "/");
      const parts = rel.split("/");
      const topDir = parts[0];

      const dirRule = DIR_TYPE_MAP.find((r) => r.match.test(topDir));
      if (!dirRule) {
        // Top-level file with no rule (shouldn't happen after SKIP_FILES); classify as unknown
        skipped.push({ path: full, reason: `no-dir-rule for ${topDir}` });
        continue;
      }

      const stat = await fs.stat(full);
      const raw = await fs.readFile(full, "utf8");
      const { data, body } = parseFrontmatter(raw);

      const filename = path.basename(full, ".md");
      const title = String(data.title ?? data.name ?? filename).trim();
      const slug = slugifyTitle(title, dirRule.type);
      const description = String(data.description ?? "").trim() ||
        body.replace(/\r?\n/g, " ").slice(0, 180).trim();

      const persona = classifyPersona(slug, description, body);
      const priority = classifyPriority(slug, description, body);

      const wiki = extractWikiLinks(body);
      const md = extractMdLinks(body);
      const inline = extractInlineTags(body);
      const links = [...new Set([...wiki, ...md])];

      // preserve vault subdir chain as tags: 10_Projects/BIM Construction Renderer.md
      // → ["10-projects"]
      const dirTags = parts.slice(0, -1).map((p) =>
        p.toLowerCase().replace(/^\d+_/, "").replace(/\s+/g, "-")
      );

      const tags = [
        ...new Set([
          ...dirRule.tags,
          ...dirTags,
          ...inline,
          filename.toLowerCase().replace(/\s+/g, "-").slice(0, 40)
        ])
      ];

      records.push({
        id: `kn_${slug}`,
        slug,
        type: dirRule.type,
        title,
        description,
        body,
        persona,
        priority,
        tags,
        links,
        source: {
          path: full,
          origin: "obsidian",
          ingestedAt: Date.now(),
          lastModified: stat.mtimeMs
        }
      } as KnowledgeRecord & { source: { origin: "obsidian" } });

      countsByType[dirRule.type] = (countsByType[dirRule.type] ?? 0) + 1;
    } catch (err) {
      skipped.push({ path: full, reason: String((err as Error).message ?? err) });
    }
  }

  return {
    records,
    report: {
      scannedFiles: files.length,
      parsedRecords: records.length,
      skipped,
      countsByType,
      durationMs: Date.now() - start
    }
  };
}
