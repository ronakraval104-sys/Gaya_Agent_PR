import fs from "node:fs/promises";
import path from "node:path";
import { parseFrontmatter, extractWikiLinks, extractMdLinks, titleFrom } from "./parser";
import { classifyPersona, classifyPriority, classifyType, extractTags } from "./classifier";
import type { KnowledgeRecord, IngestReport, MemoryType, PersonaScope } from "./types";

const DEFAULT_MEMORY_DIR = "C:/Users/Ronak/.claude/projects/C--Users-Ronak/memory";

interface IngestOptions {
  memoryDir?: string;
  includeIndex?: boolean; // include MEMORY.md as an index-line source
}

export async function ingestMemoryDir(opts: IngestOptions = {}): Promise<{
  records: KnowledgeRecord[];
  report: IngestReport;
}> {
  const start = Date.now();
  const dir = opts.memoryDir ?? DEFAULT_MEMORY_DIR;
  const entries = await fs.readdir(dir).catch(() => [] as string[]);
  const mdFiles = entries.filter(
    (f) => f.endsWith(".md") && (opts.includeIndex || f !== "MEMORY.md")
  );

  const records: KnowledgeRecord[] = [];
  const skipped: IngestReport["skipped"] = [];
  const countsByType: Record<MemoryType, number> = {
    user: 0, feedback: 0, project: 0, reference: 0,
    decision: 0, win: 0, gotcha: 0, law: 0, thread: 0, unknown: 0
  };
  const countsByPersona: Record<PersonaScope, number> = {
    "visual-rhyme": 0, "gaya-core": 0, shared: 0
  };
  const boulderRules: string[] = [];

  for (const file of mdFiles) {
    const full = path.join(dir, file);
    try {
      const stat = await fs.stat(full);
      const raw = await fs.readFile(full, "utf8");
      const { data, body } = parseFrontmatter(raw);

      // Slug rules:
      //   - if data.name is slug-shaped ([a-z0-9_-]+), use it (normalized to hyphens)
      //   - else fall back to filename-derived slug, and use the name as the display title
      const rawName = String(data.name ?? "").trim();
      const isSlugShaped = rawName.length > 0 && /^[a-z0-9_-]+$/i.test(rawName);
      const fileSlug = file.replace(/\.md$/i, "").replace(/_/g, "-").toLowerCase();
      const slug = isSlugShaped ? rawName.toLowerCase().replace(/_/g, "-") : fileSlug;

      const slugPrefix = file.split("_")[0];
      const fmType = data?.metadata?.type;
      const type = classifyType(fmType, slugPrefix);
      const description = String(data.description ?? "").trim();
      const title = !isSlugShaped && rawName ? rawName : titleFrom(rawName || slug, body);
      const persona = classifyPersona(slug, description, body);
      const priority = classifyPriority(slug, description, body);
      const tags = extractTags(slug, type, body);
      const wiki = extractWikiLinks(body);
      const md = extractMdLinks(body);
      const links = [...new Set([...wiki, ...md])];

      const record: KnowledgeRecord & { _fileSlug?: string } = {
        id: `kn_${slug}`,
        slug,
        type,
        title,
        description,
        body,
        persona,
        priority,
        tags,
        links,
        source: {
          path: full,
          origin: "memory-dir",
          originSessionId: data?.metadata?.originSessionId,
          ingestedAt: Date.now(),
          lastModified: stat.mtimeMs
        },
        _fileSlug: fileSlug
      };

      records.push(record);
      countsByType[type] = (countsByType[type] ?? 0) + 1;
      countsByPersona[persona] += 1;
      if (priority === "boulder") boulderRules.push(slug);
    } catch (err) {
      skipped.push({ path: full, reason: String((err as Error).message ?? err) });
    }
  }

  // build slug-alias table. Keys and canonicals are normalized to lowercase-hyphen form.
  const normalize = (s: string) => s.toLowerCase().replace(/_/g, "-").trim();
  const aliasToCanonical = new Map<string, string>();
  for (const r of records as (KnowledgeRecord & { _fileSlug?: string })[]) {
    const canonical = normalize(r.slug);
    const stripped = canonical.replace(new RegExp(`^${r.type}-`), "");
    const fileSlug = r._fileSlug ? normalize(r._fileSlug) : null;
    const fileStripped = fileSlug
      ? fileSlug.replace(new RegExp(`^${r.type}-`), "")
      : null;
    const aliases = new Set<string>(
      [
        canonical,
        stripped,
        `${r.type}-${canonical}`,
        `${r.type}-${stripped}`,
        fileSlug,
        fileStripped,
        fileSlug ? `${r.type}-${fileSlug}` : null,
        fileStripped ? `${r.type}-${fileStripped}` : null
      ].filter((x): x is string => !!x)
    );
    for (const a of aliases) {
      const key = normalize(a);
      if (!aliasToCanonical.has(key)) aliasToCanonical.set(key, canonical);
    }
    // strip the transient field before persisting
    delete (r as any)._fileSlug;
  }

  // resolve outbound links via alias table, mark truly broken ones
  const brokenLinks: IngestReport["brokenLinks"] = [];
  for (const r of records) {
    const resolved: string[] = [];
    for (const link of r.links) {
      const key = normalize(link);
      const canonical = aliasToCanonical.get(key);
      if (canonical) {
        resolved.push(canonical);
      } else {
        brokenLinks.push({ fromSlug: r.slug, toSlug: link });
      }
    }
    r.links = [...new Set(resolved)];
  }

  const report: IngestReport = {
    scannedFiles: mdFiles.length,
    parsedRecords: records.length,
    skipped,
    countsByType,
    countsByPersona,
    boulderRules,
    brokenLinks,
    durationMs: Date.now() - start
  };

  return { records, report };
}
