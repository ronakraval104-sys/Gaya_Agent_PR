"use client";

import { motion } from "framer-motion";
import { useMemo } from "react";
import { COUNCIL, type CouncilSeatId } from "@/lib/council";
import { ALWAYS_ON } from "@/lib/skills-inventory";
import { useGaya } from "@/lib/store";
import { ArcReactor } from "./ArcReactor";

interface Props {
  size?: number;
}

export function RadialGraph({ size = 720 }: Props) {
  const cx = size / 2;
  const cy = size / 2;
  const rInnerOrbit = size * 0.28;
  const rOuterRing = size * 0.44;

  const hoverSeat = useGaya((s) => s.focusedSeat);
  const setFocusedSeat = useGaya((s) => s.setFocusedSeat);
  const pinnedSeat = useGaya((s) => s.pinnedSeat);
  const togglePinnedSeat = useGaya((s) => s.togglePinnedSeat);
  const activeTasks = useGaya((s) => s.activeTasks);

  // effective focus = pinned wins over hover
  const effectiveFocus = pinnedSeat ?? hoverSeat;

  // arrange skills by seat, evenly along outer ring
  const skillNodes = useMemo(() => {
    const bySeat = new Map<CouncilSeatId, typeof ALWAYS_ON>();
    ALWAYS_ON.forEach((s) => {
      const arr = bySeat.get(s.ownerSeat) ?? [];
      arr.push(s);
      bySeat.set(s.ownerSeat, arr);
    });

    const nodes: Array<{ skill: typeof ALWAYS_ON[number]; x: number; y: number; angle: number }> = [];
    const seatOrder: CouncilSeatId[] = ["logos", "bob", "freya", "tvashtar"];
    const arcSpan = (Math.PI * 2) / 4; // each seat owns 90° arc
    const arcPadding = 0.22;

    seatOrder.forEach((seatId, seatIdx) => {
      const seat = COUNCIL.find((c) => c.id === seatId)!;
      const seatCenter = (seat.angleDeg * Math.PI) / 180 - Math.PI / 2;
      const seatSkills = bySeat.get(seatId) ?? [];
      const usable = arcSpan - arcPadding * 2;
      const step = seatSkills.length > 1 ? usable / (seatSkills.length - 1) : 0;
      const start = seatCenter - usable / 2;
      seatSkills.forEach((skill, i) => {
        const angle = seatSkills.length === 1 ? seatCenter : start + step * i;
        nodes.push({
          skill,
          x: cx + Math.cos(angle) * rOuterRing,
          y: cy + Math.sin(angle) * rOuterRing,
          angle
        });
      });
    });

    return nodes;
  }, [cx, cy, rOuterRing]);

  const activeSkillSlugs = new Set(activeTasks.map((t) => t.skillSlug));

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        className="absolute inset-0"
        style={{ overflow: "visible" }}
      >
        {/* orbital guide rings — Monolith hairline */}
        <circle
          cx={cx}
          cy={cy}
          r={rInnerOrbit}
          fill="none"
          stroke="var(--border)"
          strokeDasharray="1 4"
          strokeWidth={0.6}
          opacity={0.7}
        />
        <circle
          cx={cx}
          cy={cy}
          r={rOuterRing}
          fill="none"
          stroke="var(--border)"
          strokeDasharray="1 4"
          strokeWidth={0.6}
          opacity={0.5}
        />

        {/* seat -> center connectors */}
        {COUNCIL.map((seat) => {
          const a = (seat.angleDeg * Math.PI) / 180 - Math.PI / 2;
          const x = cx + Math.cos(a) * rInnerOrbit;
          const y = cy + Math.sin(a) * rInnerOrbit;
          const active = effectiveFocus === seat.id;
          return (
            <line
              key={seat.id}
              x1={cx}
              y1={cy}
              x2={x}
              y2={y}
              stroke={active ? "var(--accent)" : "var(--border)"}
              strokeWidth={active ? 1.2 : 0.6}
              opacity={active ? 0.9 : 0.5}
            />
          );
        })}

        {/* skill dashes on outer ring — tiny grey ticks */}
        {skillNodes.map((node) => {
          const active = activeSkillSlugs.has(node.skill.slug);
          const dimmed = effectiveFocus && node.skill.ownerSeat !== effectiveFocus;
          // Radial tick: a short line pointing outward from the ring center
          const angle = node.angle;
          const inner = rOuterRing - 4;
          const outer = rOuterRing + 4;
          const x1 = cx + Math.cos(angle) * inner;
          const y1 = cy + Math.sin(angle) * inner;
          const x2 = cx + Math.cos(angle) * outer;
          const y2 = cy + Math.sin(angle) * outer;
          return (
            <line
              key={node.skill.slug}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke={active ? "var(--warn)" : "var(--text-3)"}
              strokeWidth={active ? 2 : 1}
              opacity={dimmed ? 0.15 : active ? 1 : 0.5}
              style={{ transition: "opacity 220ms cubic-bezier(0.22,1,0.36,1)" }}
            >
              <title>{node.skill.label}</title>
            </line>
          );
        })}

        {/* domain arc labels — Monolith mono */}
        {COUNCIL.map((seat) => {
          const a = (seat.angleDeg * Math.PI) / 180 - Math.PI / 2;
          const lx = cx + Math.cos(a) * (rOuterRing + 22);
          const ly = cy + Math.sin(a) * (rOuterRing + 22);
          return (
            <text
              key={`arc-${seat.id}`}
              x={lx}
              y={ly}
              textAnchor="middle"
              fontFamily="JetBrains Mono, monospace"
              fontSize={9}
              fontWeight={700}
              letterSpacing="0.26em"
              fill="var(--text-3)"
            >
              {seat.domain[0].toUpperCase()}
            </text>
          );
        })}
      </svg>

      {/* Council seats (HTML overlay so they can be interactive/animated) */}
      {COUNCIL.map((seat) => {
        const a = (seat.angleDeg * Math.PI) / 180 - Math.PI / 2;
        const x = cx + Math.cos(a) * rInnerOrbit;
        const y = cy + Math.sin(a) * rInnerOrbit;
        const active = effectiveFocus === seat.id;
        const pinned = pinnedSeat === seat.id;
        return (
          <button
            key={seat.id}
            onMouseEnter={() => setFocusedSeat(seat.id)}
            onMouseLeave={() => setFocusedSeat(null)}
            onClick={() => togglePinnedSeat(seat.id)}
            aria-pressed={pinned}
            title={pinned ? `${seat.codename} pinned — click to unpin` : `Click to pin ${seat.codename}`}
            className="absolute flex flex-col items-start justify-center transition-colors cursor-pointer"
            style={{
              left: x - 52,
              top: y - 22,
              width: 104,
              height: 44,
              background: pinned ? "var(--accent)" : "var(--bg)",
              color: pinned ? "var(--ink)" : "var(--text)",
              border: `1px solid ${
                pinned ? "var(--accent)" : active ? "var(--border-strong)" : "var(--border)"
              }`,
              paddingLeft: 8,
              paddingRight: 8
            }}
          >
            <div className="flex items-center gap-1.5 w-full">
              <span
                className="dot"
                style={{
                  background: pinned ? "var(--ink)" : active ? "var(--warn)" : "var(--ok)",
                  opacity: active || pinned ? 1 : 0.7
                }}
              />
              <span
                style={{
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: 11,
                  fontWeight: 700,
                  letterSpacing: "0.12em",
                  color: "inherit"
                }}
              >
                {seat.codename}
              </span>
            </div>
            <span
              style={{
                fontFamily: "JetBrains Mono, monospace",
                fontSize: 9,
                letterSpacing: "0.14em",
                textTransform: "uppercase",
                color: pinned ? "var(--ink)" : "var(--text-3)",
                marginLeft: 12,
                marginTop: 1
              }}
            >
              {seat.role.split("//")[0].trim()}
            </span>
          </button>
        );
      })}

      {/* the reactor at center */}
      <div
        className="absolute"
        style={{ left: cx - 110, top: cy - 110 }}
      >
        <ArcReactor size={220} />
      </div>
    </div>
  );
}
