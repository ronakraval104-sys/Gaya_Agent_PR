"use client";

import { motion, useAnimation } from "framer-motion";
import { useEffect, useMemo } from "react";
import { useGaya } from "@/lib/store";
import { KnowledgeGraph } from "./KnowledgeGraph";

interface Props {
  size?: number;
}

/**
 * ArcReactor v3 — Monolith rework. The reactor is now a FRAME, and its
 * interior is the live knowledge graph. Katviz's brain becomes the reactor's
 * light source.
 *
 * Layers outside → in:
 *   1. Outer segmented telemetry ring (60 seg, orange per active task) — kept
 *   2. Persona counter-rotating dashed ring — kept
 *   3. Silver metallic housing + rivets — kept, restyled to Monolith greys
 *   4. Deep matte bezel well
 *   5. LIVE KNOWLEDGE GRAPH sitting in the well — replaces petals + core
 */
export function ArcReactor({ size = 240 }: Props) {
  const activeTasks = useGaya((s) => s.activeTasks);
  const persona = useGaya((s) => s.persona);
  const flare = useGaya((s) => s.reactorFlare);
  const flareCtrl = useAnimation();

  useEffect(() => {
    if (flare > 0) {
      flareCtrl.start({
        opacity: [0.35, 0.75, 0.35],
        transition: { duration: 0.9, ease: [0.22, 1, 0.36, 1] }
      });
    }
  }, [flare, flareCtrl]);

  const SEGMENTS = 60;
  const segments = useMemo(() => Array.from({ length: SEGMENTS }, (_, i) => i), []);
  const activeSegments = activeTasks.length;

  const cx = size / 2;
  const cy = size / 2;
  const rOuter = size / 2 - 4;
  const rPersona = rOuter - 18;
  const rHousing = rPersona - 8;
  const rHousingInner = rHousing - 14;

  // Center graph fills the bezel well minus a small padding
  const graphSize = (rHousingInner - 4) * 2;

  return (
    <div
      className="relative"
      style={{ width: size, height: size }}
      aria-label="Knowledge reactor — live graph inside a frame"
    >
      {/* faint ambient bloom around the housing, pulses on activity — Monolith-restrained */}
      <motion.div
        animate={flareCtrl}
        className="absolute inset-0 pointer-events-none"
        style={{
          borderRadius: "50%",
          boxShadow: "0 0 22px rgba(242, 242, 242, 0.06)",
          opacity: 0.35
        }}
      />

      <svg width={size} height={size} className="relative" style={{ overflow: "visible" }}>
        <defs>
          <radialGradient id="metal-housing-mono" cx="50%" cy="32%" r="72%">
            <stop offset="0%" stopColor="#3a3a3a" />
            <stop offset="55%" stopColor="#242424" />
            <stop offset="100%" stopColor="#0a0a0a" />
          </radialGradient>
          <radialGradient id="bezel-inner-mono" cx="50%" cy="55%" r="65%">
            <stop offset="0%" stopColor="#141414" />
            <stop offset="70%" stopColor="#0a0a0a" />
            <stop offset="100%" stopColor="#050505" />
          </radialGradient>
        </defs>

        {/* ── 1. Outer segmented telemetry ring ── */}
        <circle
          cx={cx}
          cy={cy}
          r={rOuter}
          fill="none"
          stroke="var(--border)"
          strokeWidth={0.6}
        />
        <g>
          {segments.map((i) => {
            const angle = (i / SEGMENTS) * Math.PI * 2 - Math.PI / 2;
            const x1 = cx + Math.cos(angle) * (rOuter - 7);
            const y1 = cy + Math.sin(angle) * (rOuter - 7);
            const x2 = cx + Math.cos(angle) * (rOuter - 1);
            const y2 = cy + Math.sin(angle) * (rOuter - 1);
            const active = i < activeSegments;
            return (
              <line
                key={i}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke={active ? "var(--warn)" : "var(--text-3)"}
                strokeWidth={active ? 2 : 0.9}
                strokeLinecap="butt"
                opacity={active ? 1 : 0.5}
              />
            );
          })}
        </g>

        {/* ── 2. Persona counter-rotating ring ── */}
        <motion.g
          animate={{ rotate: -360 }}
          transition={{ duration: 60, ease: "linear", repeat: Infinity }}
          style={{ originX: `${cx}px`, originY: `${cy}px` }}
        >
          <circle
            cx={cx}
            cy={cy}
            r={rPersona}
            fill="none"
            stroke="var(--text-3)"
            strokeWidth={0.8}
            strokeDasharray="4 5"
            opacity={0.7}
          />
        </motion.g>

        {/* ── 3. Metallic housing ── */}
        <circle cx={cx} cy={cy} r={rHousing} fill="url(#metal-housing-mono)" />
        <circle
          cx={cx}
          cy={cy}
          r={rHousing}
          fill="none"
          stroke="var(--border-strong)"
          strokeWidth={0.6}
        />
        {/* rivets — 8 flush machined bolts */}
        {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => {
          const a = (deg * Math.PI) / 180 - Math.PI / 2;
          const rx = cx + Math.cos(a) * (rHousing - 5.5);
          const ry = cy + Math.sin(a) * (rHousing - 5.5);
          return (
            <g key={deg}>
              <circle cx={rx} cy={ry} r={1.8} fill="#0a0a0a" />
              <circle cx={rx} cy={ry} r={1.3} fill="#242424" />
              <circle cx={rx - 0.35} cy={ry - 0.45} r={0.45} fill="#9c9c9c" />
            </g>
          );
        })}

        {/* ── 4. Deep matte bezel well ── */}
        <circle cx={cx} cy={cy} r={rHousingInner} fill="url(#bezel-inner-mono)" />
        <circle
          cx={cx}
          cy={cy}
          r={rHousingInner}
          fill="none"
          stroke="#000"
          strokeWidth={1.4}
        />
        <circle
          cx={cx}
          cy={cy}
          r={rHousingInner - 1.5}
          fill="none"
          stroke="rgba(242, 242, 242, 0.05)"
          strokeWidth={0.6}
        />

        {/* codename tag */}
        <text
          x={cx}
          y={size - 4}
          textAnchor="middle"
          fontFamily="JetBrains Mono, monospace"
          fontSize={9}
          letterSpacing="0.22em"
          fill="var(--accent)"
        >
          GAYA // BODHI ONLINE
        </text>
      </svg>

      {/* ── 5. LIVE KNOWLEDGE GRAPH inside the bezel well ── */}
      <div
        className="absolute pointer-events-auto"
        style={{
          left: cx - graphSize / 2,
          top: cy - graphSize / 2,
          width: graphSize,
          height: graphSize
        }}
      >
        <KnowledgeGraph size={graphSize} padding={6} />
      </div>
    </div>
  );
}
