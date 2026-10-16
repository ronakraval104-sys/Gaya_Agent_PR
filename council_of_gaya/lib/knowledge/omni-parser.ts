import fs from "node:fs/promises";
import path from "node:path";
import type { KnowledgeRecord, MemoryType, Priority } from "./types";
import { extractWikiLinks, extractMdLinks } from "./parser";

/**
 * OMNI_GAYA memory has section-based structure — no per-record frontmatter.
 * This parser turns known sections (Brag Doc, Decision Records, Domain Laws,
 * Open Threads, GOTCHAS, Wins & Deliverables, Evolution Queue) into records.
 *
 * GATED THREAD section is respected — never emitted.
 */

interface SectionSpec {
  headingIncludes: string[];   // case-insensitive substring in the ## heading
  emit: (body: string, sourcePath: string) => KnowledgeRecord[];
}

const CANDIDATE_OMNI_PATHS = [
  "C:/Users/rossi/.gemini/config/skills/omni-gaya/OMNI_GAYA_MEMORY.md",
  "d:/Ai_Tools/antigravity_ai/skills/omni-gaya/OMNI_GAYA_MEMORY.md",
  "d:/Ai_Tools/antigravity_ai/gaya_repo_temp/skills/omni-gaya/OMNI_GAYA_MEMORY.md",
  path.join(process.cwd(), "..", "skills", "omni-gaya", "OMNI_GAYA_MEMORY.md"),
  path.join(process.cwd(), "data", "OMNI_GAYA_MEMORY.md")
];

export async function ingestOmniGayaMemory(overridePath?: string): Promise<KnowledgeRecord[]> {
  const candidates = overridePath ? [overridePath, ...CANDIDATE_OMNI_PATHS] : CANDIDATE_OMNI_PATHS;
  let p: string | null = null;
  let raw: string | null = null;

  for (const c of candidates) {
    try {
      raw = await fs.readFile(c, "utf8");
      p = c;
      break;
    } catch {
      continue;
    }
  }

  if (!raw || !p) return [];

  // Clean legacy Katviz and Jarvis naming into R0n and Gaya
  raw = raw
    .replace(/katviz/gi, "R0n")
    .replace(/jarvis/gi, "Gaya");

  const sections = splitBySection(raw);
  const records: KnowledgeRecord[] = [];

  for (const s of sections) {
    // Hard skip: never surface anything under a gated thread
    if (/gated thread/i.test(s.heading)) continue;

    for (const spec of SECTION_SPECS) {
      if (spec.headingIncludes.some((h) => s.heading.toLowerCase().includes(h))) {
        records.push(...spec.emit(s.body, p));
        break;
      }
    }
  }
  return records;
}

function splitBySection(md: string): { heading: string; body: string }[] {
  const lines = md.split(/\r?\n/);
  const out: { heading: string; body: string }[] = [];
  let cur: { heading: string; body: string } | null = null;
  for (const line of lines) {
    const h = line.match(/^##\s+(.+)$/);
    if (h) {
      if (cur) out.push(cur);
      cur = { heading: h[1].trim(), body: "" };
    } else if (cur) {
      cur.body += line + "\n";
    }
  }
  if (cur) out.push(cur);
  return out;
}

/**
 * Parse a markdown table body into rows. Expects | col | col | format
 * with an alignment row (| --- | --- |) that we skip.
 */
function parseTable(body: string): string[][] {
  const rows: string[][] = [];
  for (const line of body.split(/\r?\n/)) {
    if (!line.trim().startsWith("|")) continue;
    const cells = line
      .trim()
      .replace(/^\||\|$/g, "")
      .split("|")
      .map((c) => c.trim());
    // skip alignment / separator rows
    if (cells.every((c) => /^:?-+:?$/.test(c))) continue;
    if (cells.length) rows.push(cells);
  }
  return rows;
}

/**
 * Parse a bulleted list into (line, id) pairs.
 * Handles - or * bullets, keeps ordering.
 */
function parseBulletList(body: string): string[] {
  const items: string[] = [];
  let cur = "";
  for (const line of body.split(/\r?\n/)) {
    const m = line.match(/^\s*[-*]\s+(.+)$/);
    if (m) {
      if (cur) items.push(cur.trim());
      cur = m[1];
    } else if (/^\s+\S/.test(line) && cur) {
      cur += " " + line.trim(); // continuation line
    } else if (!line.trim() && cur) {
      items.push(cur.trim());
      cur = "";
    }
  }
  if (cur) items.push(cur.trim());
  return items;
}

function slugify(text: string, prefix: string, n: number): string {
  const base = text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 60)
    .replace(/^-|-$/g, "");
  return `${prefix}-${base || `n${n}`}`;
}

/**
 * Clean a bullet-list item into a human-legible title.
 * - If wrapped in **bold**, prefer the bold content
 * - Strip stray leading markdown (** ` * _)
 * - Split on first ":" or em-dash "—" (NOT hyphen — breaks dates/slugs)
 * - Trim trailing markdown garbage
 * - Return null if empty after cleaning (caller should skip)
 */
function cleanTitle(raw: string): string | null {
  if (!raw) return null;
  let t = raw.trim();

  // Prefer the bold wrapper if the item leads with one
  const bold = t.match(/^\*\*([^*]+?)\*\*/);
  if (bold) {
    const inner = bold[1].trim();
    return inner ? inner.slice(0, 80) : null;
  }

  // Strip leading markdown noise
  t = t.replace(/^[`*_]+\s*/, "").trim();
  if (!t) return null;

  // Take up to first ":" or em-dash "—" (both are conventional label/context splits)
  const m = t.match(/^(.+?)\s*[:—]/);
  const head = (m ? m[1] : t).trim();

  // Strip trailing markdown/whitespace garbage
  const cleaned = head.replace(/[*_`\s]+$/, "").trim().slice(0, 80);
  return cleaned || null;
}

function makeRecord(args: {
  slug: string;
  type: MemoryType;
  title: string;
  description: string;
  body: string;
  priority: Priority;
  tags: string[];
  sourcePath: string;
}): KnowledgeRecord {
  const wiki = extractWikiLinks(args.body);
  const md = extractMdLinks(args.body);
  return {
    id: `kn_${args.slug}`,
    slug: args.slug,
    type: args.type,
    title: args.title,
    description: args.description,
    body: args.body,
    persona: "shared",
    priority: args.priority,
    tags: args.tags,
    links: [...new Set([...wiki, ...md])],
    source: {
      path: args.sourcePath,
      origin: "omni-gaya",
      ingestedAt: Date.now()
    }
  };
}

const SECTION_SPECS: SectionSpec[] = [
  // ── Brag Doc → wins ──
  {
    headingIncludes: ["brag doc"],
    emit: (body, src) => {
      const rows = parseTable(body);
      if (rows.length < 2) return [];
      const dataRows = rows.slice(1); // drop header
      return dataRows.map((r, i) => {
        const [date = "", winTitle = "", context = ""] = r;
        const slug = slugify(`${date}-${winTitle}`, "win", i);
        return makeRecord({
          slug,
          type: "win",
          title: winTitle || `Win ${i + 1}`,
          description: (context || winTitle).slice(0, 180),
          body: `**Date:** ${date}\n\n**Win:** ${winTitle}\n\n${context}`,
          priority: "normal",
          tags: ["win", "brag-doc", "omni-gaya"],
          sourcePath: src
        });
      });
    }
  },

  // ── Decision Records → decisions ──
  {
    headingIncludes: ["decision records"],
    emit: (body, src) => {
      const rows = parseTable(body);
      if (rows.length < 2) return [];
      const dataRows = rows.slice(1);
      return dataRows.map((r, i) => {
        const [date = "", decision = "", rationale = "", ruledOut = ""] = r;
        const cleanDec = decision.replace(/\*\*/g, "").trim();
        const slug = slugify(`${date}-${cleanDec}`, "dec", i);
        return makeRecord({
          slug,
          type: "decision",
          title: cleanDec || `Decision ${i + 1}`,
          description: rationale.slice(0, 180),
          body: `**Date:** ${date}\n\n**Decision:** ${decision}\n\n**Rationale:** ${rationale}\n\n**Ruled out:** ${ruledOut}`,
          priority: "high",
          tags: ["decision", "omni-gaya"],
          sourcePath: src
        });
      });
    }
  },

  // ── Domain Laws → laws (boulder priority) ──
  {
    headingIncludes: ["domain laws"],
    emit: (body, src) => {
      const items: string[] = [];
      for (const line of body.split(/\r?\n/)) {
        const m = line.match(/^\s*\d+\.\s+(.+)$/);
        if (m) items.push(m[1].trim());
      }
      return items.map((text, i) => {
        // Extract a short title from bold marker or first sentence
        const titleMatch = text.match(/\*\*([^*]+)\*\*/);
        const title = (titleMatch ? titleMatch[1] : text.split(/[.:]/)[0]).slice(0, 80);
        const slug = slugify(title, "law", i + 1);
        return makeRecord({
          slug,
          type: "law",
          title,
          description: text.replace(/\*\*/g, "").slice(0, 180),
          body: text,
          priority: "boulder",
          tags: ["law", "boulder", "omni-gaya", "always-on"],
          sourcePath: src
        });
      });
    }
  },

  // ── Open Threads → threads ──
  {
    headingIncludes: ["open threads"],
    emit: (body, src) => {
      const records: KnowledgeRecord[] = [];

      // 1. Parse markdown table rows if present
      const tableRows = parseTable(body);
      if (tableRows.length >= 2) {
        tableRows.slice(1).forEach((cols, i) => {
          const [prioCol = "", threadCol = "", blockedBy = ""] = cols;
          const cleanTitleStr = cleanTitle(threadCol) || threadCol.replace(/\*\*/g, "").slice(0, 80);
          if (!cleanTitleStr) return;
          // Skip completed / superseded rows if crossed out or marked done
          if (/done|superseded|dropped|~~/i.test(prioCol) || /~~/i.test(threadCol)) return;

          let priority: Priority = "normal";
          if (/high|🔴/i.test(prioCol)) priority = "boulder";
          else if (/med|🟡/i.test(prioCol)) priority = "high";

          const slug = slugify(cleanTitleStr, "thread", i + 1);
          records.push(
            makeRecord({
              slug,
              type: "thread",
              title: cleanTitleStr,
              description: `${threadCol.replace(/\*\*/g, "")}${
                blockedBy && blockedBy !== "—" ? ` (Blocked by: ${blockedBy})` : ""
              }`.slice(0, 180),
              body: `**Thread:** ${threadCol}\n\n**Priority:** ${prioCol}\n\n**Blocked by:** ${blockedBy}`,
              priority,
              tags: ["thread", "open", "omni-gaya", "active"],
              sourcePath: src
            })
          );
        });
      }

      // 2. Also parse bullet list items if present
      const bulletItems = parseBulletList(body)
        .map((text) => ({ text, title: cleanTitle(text) }))
        .filter((x) => x.title !== null);

      bulletItems.forEach(({ text, title }, i) => {
        const slug = slugify(title!, "thread", i + 100);
        records.push(
          makeRecord({
            slug,
            type: "thread",
            title: title!,
            description: text.slice(0, 180),
            body: text,
            priority: "normal",
            tags: ["thread", "open", "omni-gaya"],
            sourcePath: src
          })
        );
      });

      return records;
    }
  },

  // ── GOTCHAS → gotchas (high priority) ──
  {
    headingIncludes: ["gotcha"],
    emit: (body, src) => {
      const items = parseBulletList(body)
        .map((text) => ({ text, title: cleanTitle(text) }))
        .filter((x) => x.title !== null);
      return items.map(({ text, title }, i) => {
        const slug = slugify(title!, "gotcha", i);
        return makeRecord({
          slug,
          type: "gotcha",
          title: title!,
          description: text.slice(0, 200),
          body: text,
          priority: "high",
          tags: ["gotcha", "lesson", "omni-gaya"],
          sourcePath: src
        });
      });
    }
  },

  // ── Wins & Deliverables (secondary win section) → wins ──
  {
    headingIncludes: ["wins & deliverables", "wins and deliverables"],
    emit: (body, src) => {
      const items = parseBulletList(body)
        .map((text) => ({ text, title: cleanTitle(text) }))
        .filter((x) => x.title !== null);
      return items.map(({ text, title }, i) => {
        const slug = slugify(title!, "win", i + 100);
        return makeRecord({
          slug,
          type: "win",
          title: title!,
          description: text.slice(0, 180),
          body: text,
          priority: "normal",
          tags: ["win", "deliverable", "omni-gaya"],
          sourcePath: src
        });
      });
    }
  },

  // ── Evolution Queue → threads (future work) ──
  {
    headingIncludes: ["evolution queue"],
    emit: (body, src) => {
      const items = parseBulletList(body)
        .map((text) => ({ text, title: cleanTitle(text) }))
        .filter((x) => x.title !== null);
      return items.map(({ text, title }, i) => {
        const slug = slugify(title!, "thread", i + 200);
        return makeRecord({
          slug,
          type: "thread",
          title: title!,
          description: text.slice(0, 180),
          body: text,
          priority: "normal",
          tags: ["thread", "evolution", "roadmap", "omni-gaya"],
          sourcePath: src
        });
      });
    }
  }
];
