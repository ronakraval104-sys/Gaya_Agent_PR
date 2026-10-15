import { NextResponse } from "next/server";
import { list } from "@/lib/knowledge/repo";

/**
 * Bulk knowledge dump for graph views: every record with slim projection
 * + a pre-computed edge list (unique undirected pairs from record.links).
 *
 * 118 records @ ~200 bytes each = ~24KB — well under any concern budget.
 * Called by KnowledgeGraph.tsx to seed the force sim with real topology.
 */
export async function GET() {
  const rows = await list({});

  // Projection — everything the graph needs, nothing it doesn't
  const nodes = rows.map((r) => ({
    slug: r.slug,
    title: r.title,
    type: r.type,
    persona: r.persona,
    priority: r.priority,
    tags: r.tags,
    links: r.links
  }));

  // Build undirected edge list, dedup by canonical (min,max) pair
  const nodeSlugs = new Set(nodes.map((n) => n.slug));
  const seen = new Set<string>();
  const edges: { a: string; b: string }[] = [];
  for (const n of nodes) {
    for (const l of n.links) {
      if (!nodeSlugs.has(l)) continue;
      if (l === n.slug) continue;
      const key = n.slug < l ? `${n.slug}|${l}` : `${l}|${n.slug}`;
      if (seen.has(key)) continue;
      seen.add(key);
      edges.push({ a: n.slug, b: l });
    }
  }

  return NextResponse.json({
    ok: true,
    count: nodes.length,
    edgeCount: edges.length,
    nodes,
    edges
  });
}
