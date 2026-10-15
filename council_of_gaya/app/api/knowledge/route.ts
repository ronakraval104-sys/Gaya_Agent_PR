import { NextResponse } from "next/server";
import { list, type ListFilter } from "@/lib/knowledge/repo";
import type { MemoryType, PersonaScope, Priority } from "@/lib/knowledge/types";
import type { CouncilSeatId } from "@/lib/council";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const filter: ListFilter = {
    type: (url.searchParams.get("type") as MemoryType) ?? undefined,
    persona: (url.searchParams.get("persona") as PersonaScope) ?? undefined,
    priority: (url.searchParams.get("priority") as Priority) ?? undefined,
    tag: url.searchParams.get("tag") ?? undefined,
    q: url.searchParams.get("q") ?? undefined,
    seat: (url.searchParams.get("seat") as CouncilSeatId) ?? undefined
  };
  const rows = await list(filter);
  return NextResponse.json({
    ok: true,
    count: rows.length,
    records: rows.map((r) => ({
      slug: r.slug,
      title: r.title,
      description: r.description,
      type: r.type,
      persona: r.persona,
      priority: r.priority,
      tags: r.tags
    }))
  });
}
