"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useGaya } from "@/lib/store";

interface CountsPayload {
  ok: boolean;
  total: number;
  byType: Record<string, number>;
  byPersona: Record<string, number>;
  byPriority: Record<string, number>;
  boulderCount: number;
  lastIngestAt?: number;
}

interface PillarSpec {
  id: string;
  label: string;
  color: string;
  getCount: (c: CountsPayload) => number;
}

/**
 * Isometric obelisk field — 6 pillars of light on a hex platform.
 * Each pillar height reflects live counts from /api/knowledge/counts,
 * normalized against the tallest pillar in the current set.
 */
export function KnowledgeCore({ width = 640, height = 380 }: { width?: number; height?: number }) {
  const persona = useGaya((s) => s.persona);
  const [counts, setCounts] = useState<CountsPayload | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const res = await fetch("/api/knowledge/counts");
        const data = (await res.json()) as CountsPayload;
        if (!cancelled) setCounts(data);
      } catch {
        // swallow — pillars fall back to zero-state
      }
    };
    load();
    const id = setInterval(load, 15000); // refresh every 15s so a re-ingest reflects live
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  const personaVenturesColor = "#D4AF37";

  const specs: PillarSpec[] = [
    {
      id: "ventures",
      label: "VENTURES",
      color: personaVenturesColor,
      getCount: (c) => c.total ?? 0
    },
    {
      id: "wins",
      label: "WINS",
      color: "#FFB454",
      getCount: (c) => c.byType.win ?? 0
    },
    {
      id: "projects",
      label: "PROJECTS",
      color: "#4FE3FF",
      getCount: (c) => c.byType.project ?? 0
    },
    {
      id: "knowledge",
      label: "KNOWLEDGE",
      color: "#7A5CFF",
      getCount: (c) => c.total
    },
    {
      id: "agents",
      label: "AGENTS",
      color: "#E5D9FF",
      getCount: (c) => (c.byType.decision ?? 0) + (c.byType.law ?? 0)
    },
    {
      id: "rules",
      label: "RULES",
      color: "#FF7A1A",
      getCount: (c) => c.boulderCount
    }
  ];

  const pillarData = specs.map((s) => ({
    ...s,
    count: counts ? s.getCount(counts) : 0
  }));

  const maxCount = Math.max(1, ...pillarData.map((p) => p.count));
  const pillars = pillarData.map((p) => ({
    ...p,
    heightPct: 0.15 + (p.count / maxCount) * 0.85 // ensure min-height so pillar stays visible
  }));

  const cx = width / 2;
  const cy = height / 2 + 30;
  const hexR = 130;
  const iso = { scaleY: 0.5 };
  const totalDisplay = counts?.total ?? 0;
  const stamp = counts?.lastIngestAt
    ? new Date(counts.lastIngestAt).toLocaleString("en-IN", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "short" })
    : "—";

  return (
    <div className="relative" style={{ width, height }}>
      <svg width={width} height={height} className="absolute inset-0" style={{ overflow: "visible" }}>
        {/* iso grid platform */}
        <g transform={`translate(${cx}, ${cy}) scale(1, ${iso.scaleY})`}>
          <polygon
            points={hexPoints(hexR).map((p) => `${p[0]},${p[1]}`).join(" ")}
            fill="rgba(79, 227, 255, 0.04)"
            stroke="var(--hud-line)"
            strokeWidth={1}
          />
          {hexPoints(hexR).map((p, i) => (
            <line
              key={i}
              x1={0}
              y1={0}
              x2={p[0]}
              y2={p[1]}
              stroke="var(--hud-line)"
              strokeWidth={0.6}
              opacity={0.5}
            />
          ))}
          {[0.66, 0.33].map((s, i) => (
            <polygon
              key={i}
              points={hexPoints(hexR * s).map((p) => `${p[0]},${p[1]}`).join(" ")}
              fill="none"
              stroke="var(--hud-line)"
              strokeWidth={0.5}
              opacity={0.4}
            />
          ))}
        </g>

        {/* pillars — depth-sorted so back pillars render first, front pillars occlude naturally */}
        {pillars
          .map((p, i) => {
            const hp = hexPoints(hexR * 0.7)[i];
            return { ...p, _hp: hp, _px: cx + hp[0], _py: cy + hp[1] * iso.scaleY, _origIdx: i };
          })
          .sort((a, b) => a._py - b._py)
          .map((p) => {
          const px = p._px;
          const py = p._py;
          const i = p._origIdx;
          const pillarH = 150 * p.heightPct;
          return (
            <g key={p.id}>
              <ellipse cx={px} cy={py} rx={14} ry={7} fill={p.color} opacity={0.15} />
              <motion.rect
                x={px - 8}
                y={py - pillarH}
                width={16}
                height={pillarH}
                fill={`url(#pillar-${p.id})`}
                animate={{ scaleY: [1, 1.02, 1] }}
                transition={{ duration: 6, ease: "easeInOut", repeat: Infinity, delay: i * 0.4 }}
                style={{ transformOrigin: `${px}px ${py}px` }}
              />
              <defs>
                <linearGradient id={`pillar-${p.id}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={p.color} stopOpacity="0" />
                  <stop offset="20%" stopColor={p.color} stopOpacity="0.4" />
                  <stop offset="100%" stopColor={p.color} stopOpacity="1" />
                </linearGradient>
              </defs>
              <circle cx={px} cy={py - pillarH} r={4} fill={p.color} opacity={0.9} />
              <circle cx={px} cy={py - pillarH} r={9} fill={p.color} opacity={0.25} filter="blur(4px)" />

              {/* count number above cap */}
              <text
                x={px}
                y={py - pillarH - 14}
                textAnchor="middle"
                fontFamily="General Sans, system-ui, sans-serif"
                fontWeight={600}
                fontSize={16}
                fill={p.color}
                opacity={0.95}
              >
                {p.count}
              </text>

              {/* label below base */}
              <text
                x={px}
                y={py + 22}
                textAnchor="middle"
                fontFamily="JetBrains Mono, monospace"
                fontSize={9}
                letterSpacing="0.15em"
                fill={p.color}
                opacity={0.85}
              >
                {p.label}
              </text>
            </g>
          );
        })}
      </svg>

      <div
        className="absolute top-2 left-4 hud-label"
        style={{ color: "var(--arc-teal)" }}
      >
        // KNOWLEDGE CORE
      </div>
      <div
        className="absolute top-2 right-4 hud-label"
        style={{ color: "var(--arc-teal)", opacity: 0.55 }}
      >
        {totalDisplay} RECORDS · SYNC {stamp}
      </div>
    </div>
  );
}

function hexPoints(r: number): [number, number][] {
  return Array.from({ length: 6 }, (_, i) => {
    const a = (Math.PI / 3) * i - Math.PI / 2;
    return [Math.cos(a) * r, Math.sin(a) * r];
  });
}
