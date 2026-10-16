export type MemoryType = "user" | "feedback" | "project" | "reference" | "decision" | "win" | "gotcha" | "law" | "thread" | "unknown";

export type PersonaScope = "visual-rhyme" | "gaya-core" | "shared";

export type Priority = "boulder" | "high" | "normal";

export interface KnowledgeRecord {
  id: string;                  // stable, derived from slug
  slug: string;                // kebab-case, matches source filename
  type: MemoryType;
  title: string;               // human display title
  description: string;         // one-liner from frontmatter
  body: string;                // full markdown body
  persona: PersonaScope;
  priority: Priority;
  tags: string[];
  links: string[];             // outbound [[wiki-links]]
  source: {
    path: string;              // absolute path
    origin: "memory-dir" | "omni-gaya" | "obsidian" | "index-line" | "manual";
    originSessionId?: string;
    ingestedAt: number;
    lastModified?: number;
  };
}

export interface IngestReport {
  scannedFiles: number;
  parsedRecords: number;
  skipped: { path: string; reason: string }[];
  countsByType: Record<MemoryType, number>;
  countsByPersona: Record<PersonaScope, number>;
  boulderRules: string[];      // slugs
  brokenLinks: { fromSlug: string; toSlug: string }[];
  durationMs: number;
}
