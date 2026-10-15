import { NextResponse } from "next/server";
import { addRecord, list } from "@/lib/knowledge/repo";
import type { KnowledgeRecord, MemoryType, PersonaScope, Priority } from "@/lib/knowledge/types";

interface LogBody {
  kind: "decision" | "win" | "dump" | "gotcha" | "thread" | "note";
  text: string;
  personaId?: PersonaScope;
}

function slugify(text: string, prefix: string): string {
  const base = text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 60)
    .replace(/^-|-$/g, "");
  const stamp = Date.now().toString(36).slice(-4);
  return `${prefix}-${base || "entry"}-${stamp}`;
}

const KIND_TO_TYPE: Record<LogBody["kind"], MemoryType> = {
  decision: "decision",
  win: "win",
  dump: "unknown",
  gotcha: "gotcha",
  thread: "thread",
  note: "unknown"
};

const KIND_TO_PRIORITY: Record<LogBody["kind"], Priority> = {
  decision: "high",
  win: "normal",
  dump: "normal",
  gotcha: "high",
  thread: "normal",
  note: "normal"
};

const KIND_TO_TAGS: Record<LogBody["kind"], string[]> = {
  decision: ["decision", "logged-live", "console"],
  win: ["win", "logged-live", "console"],
  dump: ["dump", "logged-live", "console"],
  gotcha: ["gotcha", "lesson", "logged-live", "console"],
  thread: ["thread", "open", "logged-live", "console"],
  note: ["note", "logged-live", "console"]
};

export async function POST(req: Request) {
  const body = (await req.json()) as LogBody;
  const { kind, text, personaId } = body;
  if (!text || !text.trim()) {
    return NextResponse.json({ ok: false, error: "text required" }, { status: 400 });
  }

  const type = KIND_TO_TYPE[kind] ?? "unknown";
  const priority = KIND_TO_PRIORITY[kind] ?? "normal";
  const tags = KIND_TO_TAGS[kind] ?? ["console"];
  const persona: PersonaScope = personaId ?? "shared";

  const title = text.split(/[.:\n—]/)[0].slice(0, 80).trim() || `${kind} entry`;
  const slug = slugify(title, kind);

  const now = Date.now();
  const record: KnowledgeRecord = {
    id: `kn_${slug}`,
    slug,
    type,
    title,
    description: text.slice(0, 180),
    body: text,
    persona,
    priority,
    tags,
    links: [],
    source: {
      path: "console://slash-console",
      origin: "manual",
      ingestedAt: now
    }
  };

  await addRecord(record);
  return NextResponse.json({ ok: true, slug, record: { slug, title, type } });
}

export async function GET() {
  const rows = await list({});
  return NextResponse.json({ ok: true, count: rows.length });
}
