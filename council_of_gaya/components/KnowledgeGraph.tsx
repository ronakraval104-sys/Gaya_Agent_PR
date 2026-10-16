"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useGaya } from "@/lib/store";

interface NodeRecord {
  slug: string;
  title: string;
  type: string;
  persona: string;
  priority: string;
  links: string[];
}

interface SimNode {
  slug: string;
  title: string;
  type: string;
  persona: string;
  priority: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  degree: number;
}

interface SimEdge {
  a: string;
  b: string;
}

interface Props {
  size?: number;
  padding?: number;
  showLabels?: boolean;
}

/**
 * Obsidian-style force-directed graph.
 * Nodes = KnowledgeRecords, edges = wiki-link relationships between them.
 * Boulder = red, high-priority = amber, normal = grayscale.
 * Click a node → open the record modal.
 *
 * Self-contained: hand-rolled force simulation, SVG rendering, no d3 dep.
 */
export function KnowledgeGraph({ size = 200, padding = 8, showLabels = false }: Props) {
  const openRecord = useGaya((s) => s.openRecord);
  const openRecordSlug = useGaya((s) => s.openRecordSlug);
  const persona = useGaya((s) => s.persona);
  const inPersonaScope = (p: string) => p === persona || p === "shared";
  const [records, setRecords] = useState<NodeRecord[]>([]);
  const [hover, setHover] = useState<string | null>(null);
  const [tick, setTick] = useState(0);
  const nodesRef = useRef<Map<string, SimNode>>(new Map());
  const edgesRef = useRef<SimEdge[]>([]);

  // Guard against SSR/CSR hydration mismatch: node seed positions use Math.random.
  // Render an empty svg on the first paint, then hydrate the sim on the client.
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const radius = size / 2 - padding;

  // Fetch full graph in one bulk call (client-only) — replaces the old
  // summary + per-slug enrich loop. /api/knowledge/full returns every
  // record with its links already inlined.
  useEffect(() => {
    if (!mounted) return;
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch("/api/knowledge/full").then((r) => r.json());
        if (cancelled || !res.ok) return;
        setRecords(res.nodes as NodeRecord[]);
      } catch {}
    })();
    return () => { cancelled = true; };
  }, [mounted]);

  // Build sim nodes + edges from records
  const { nodes, edges } = useMemo(() => {
    const nodeMap = new Map<string, SimNode>();
    // Seed with existing simulated positions if we already have them
    for (const r of records) {
      const existing = nodesRef.current.get(r.slug);
      const a = Math.random() * Math.PI * 2;
      const r0 = Math.random() * radius * 0.6;
      nodeMap.set(r.slug, existing ?? {
        slug: r.slug,
        title: r.title,
        type: r.type,
        persona: r.persona,
        priority: r.priority,
        x: Math.cos(a) * r0,
        y: Math.sin(a) * r0,
        vx: 0,
        vy: 0,
        degree: 0
      });
    }
    const edgeList: SimEdge[] = [];
    for (const r of records) {
      for (const l of r.links) {
        if (nodeMap.has(l) && l !== r.slug) {
          edgeList.push({ a: r.slug, b: l });
          const na = nodeMap.get(r.slug)!;
          const nb = nodeMap.get(l)!;
          na.degree += 1;
          nb.degree += 1;
        }
      }
    }
    nodesRef.current = nodeMap;
    edgesRef.current = edgeList;
    return { nodes: [...nodeMap.values()], edges: edgeList };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [records, radius]);

  // Run force simulation
  useEffect(() => {
    if (nodes.length === 0) return;
    let raf = 0;
    let ticks = 0;
    const MAX_TICKS = 400;
    const step = () => {
      const ns = [...nodesRef.current.values()];
      const es = edgesRef.current;
      const nodeMap = nodesRef.current;

      // Center pull — weak
      for (const n of ns) {
        n.vx += -n.x * 0.006;
        n.vy += -n.y * 0.006;
      }
      // Node-node repulsion within cutoff
      const CUTOFF = 40;
      const CUTOFF2 = CUTOFF * CUTOFF;
      for (let i = 0; i < ns.length; i++) {
        for (let j = i + 1; j < ns.length; j++) {
          const a = ns[i], b = ns[j];
          const dx = b.x - a.x;
          const dy = b.y - a.y;
          const d2 = dx * dx + dy * dy + 0.01;
          if (d2 < CUTOFF2) {
            const d = Math.sqrt(d2);
            const f = 60 / d2;
            const nx = dx / d;
            const ny = dy / d;
            a.vx -= nx * f;
            a.vy -= ny * f;
            b.vx += nx * f;
            b.vy += ny * f;
          }
        }
      }
      // Edge springs
      const TARGET_LEN = 22;
      for (const e of es) {
        const a = nodeMap.get(e.a);
        const b = nodeMap.get(e.b);
        if (!a || !b) continue;
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const d = Math.sqrt(dx * dx + dy * dy) + 0.01;
        const f = (d - TARGET_LEN) * 0.03;
        const nx = dx / d;
        const ny = dy / d;
        a.vx += nx * f;
        a.vy += ny * f;
        b.vx -= nx * f;
        b.vy -= ny * f;
      }
      // Damping + integrate + circular clamp
      for (const n of ns) {
        n.vx *= 0.82;
        n.vy *= 0.82;
        n.x += n.vx;
        n.y += n.vy;
        const r = Math.sqrt(n.x * n.x + n.y * n.y);
        if (r > radius * 0.95) {
          n.x = (n.x / r) * radius * 0.95;
          n.y = (n.y / r) * radius * 0.95;
          n.vx *= -0.35;
          n.vy *= -0.35;
        }
      }

      ticks += 1;
      setTick((t) => t + 1);
      if (ticks < MAX_TICKS) {
        raf = requestAnimationFrame(step);
      }
    };
    raf = requestAnimationFrame(step);
    return () => cancelWaf(raf);
  }, [nodes.length, edges.length, radius]);

  const isNeighbor = (slug: string) => {
    if (!hover) return false;
    return edges.some(
      (e) => (e.a === hover && e.b === slug) || (e.b === hover && e.a === slug)
    );
  };

  const nodeColor = (n: SimNode, active: boolean) => {
    if (active) return "#f2f2f2";
    if (n.priority === "boulder") return "#ff2d3f";
    if (n.priority === "high") return "#ffb000";
    return "#5c5c5c";
  };

  const cx = size / 2;
  const cy = size / 2;

  // Server render (and first client paint pre-hydration): empty svg — no
  // Math.random-seeded positions leak into the HTML.
  if (!mounted) {
    return (
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        style={{ display: "block" }}
      />
    );
  }

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      style={{ display: "block" }}
    >
      <g transform={`translate(${cx}, ${cy})`}>
        {/* edges (drawn first so nodes sit on top) */}
        {edges.map((e, i) => {
          const a = nodesRef.current.get(e.a);
          const b = nodesRef.current.get(e.b);
          if (!a || !b) return null;
          const active = hover === e.a || hover === e.b;
          // Dim edges where either endpoint is out of persona scope
          const inScope = inPersonaScope(a.persona) && inPersonaScope(b.persona);
          return (
            <line
              key={i}
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              stroke={active ? "#f2f2f2" : "#3a3a3a"}
              strokeWidth={active ? 0.9 : 0.4}
              opacity={active ? 0.85 : inScope ? 0.3 : 0.06}
            />
          );
        })}
        {/* nodes */}
        {nodes.map((n) => {
          const isHover = hover === n.slug;
          const isOpen = openRecordSlug === n.slug;
          const isNear = isNeighbor(n.slug);
          const active = isHover || isOpen || isNear;
          const inScope = inPersonaScope(n.persona);
          const r = n.priority === "boulder" ? 2.4 : n.priority === "high" ? 2.0 : 1.5;
          return (
            <g key={n.slug} opacity={inScope || active ? 1 : 0.18}>
              {active && (
                <circle
                  cx={n.x}
                  cy={n.y}
                  r={r + 2}
                  fill="none"
                  stroke="#f2f2f2"
                  strokeWidth={0.6}
                  opacity={0.5}
                />
              )}
              <circle
                cx={n.x}
                cy={n.y}
                r={isHover || isOpen ? r + 0.6 : r}
                fill={nodeColor(n, isHover || isOpen)}
                onClick={(e) => {
                  e.stopPropagation();
                  openRecord(n.slug);
                }}
                onMouseEnter={() => setHover(n.slug)}
                onMouseLeave={() => setHover(null)}
                style={{ cursor: "pointer" }}
              >
                <title>
                  {n.title} ({n.priority} · {n.persona})
                </title>
              </circle>
            </g>
          );
        })}
        {/* label for hovered node */}
        {hover && (() => {
          const n = nodesRef.current.get(hover);
          if (!n) return null;
          return (
            <text
              x={n.x + 5}
              y={n.y - 5}
              fontSize={7.5}
              fontFamily="JetBrains Mono, monospace"
              fill="#f2f2f2"
              pointerEvents="none"
              style={{ textShadow: "0 0 4px #0a0a0a" }}
            >
              {n.title.slice(0, 32)}
            </text>
          );
        })()}
      </g>
    </svg>
  );
}

// small util because rAF-cancel typo-guard
function cancelWaf(id: number) {
  if (typeof cancelAnimationFrame !== "undefined") cancelAnimationFrame(id);
}
