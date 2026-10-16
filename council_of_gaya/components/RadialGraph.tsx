"use client";

import { motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
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

  // Live telemetry polling from /api/gaya-state
  const [telemetry, setTelemetry] = useState<{
    state: string;
    detail: string;
    modelName: string;
    harness: string;
    activeSeat: string;
    isProcessing: boolean;
    stepIndex: number;
    activeTool?: string;
    toolSummary?: string;
  }>({
    state: "idle",
    detail: "Council standing by",
    modelName: "Gemini 2.5 Pro (Thinking)",
    harness: "Google Antigravity",
    activeSeat: "bob",
    isProcessing: false,
    stepIndex: 0,
  });

  useEffect(() => {
    let alive = true;
    const poll = async () => {
      try {
        const r = await fetch("/api/gaya-state", { cache: "no-store" });
        const j = await r.json();
        if (alive && j) {
          setTelemetry({
            state: j.state || "idle",
            detail: j.detail || "",
            modelName: j.modelName || "Gemini 2.5 Pro (Thinking)",
            harness: j.harness || "Google Antigravity",
            activeSeat: j.activeSeat || "bob",
            isProcessing: !!j.isProcessing,
            stepIndex: j.stepIndex || 0,
            activeTool: j.activeTool,
            toolSummary: j.toolSummary,
          });
        }
      } catch {}
    };
    poll();
    const id = setInterval(poll, 1200);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

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
    <div className="relative flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          className="absolute inset-0"
          style={{ overflow: "visible" }}
        >
          {/* Active processing energy aura */}
          {telemetry.isProcessing && (
            <motion.circle
              cx={cx}
              cy={cy}
              r={rInnerOrbit}
              fill="none"
              stroke="var(--warn)"
              strokeWidth={1}
              animate={{ opacity: [0.15, 0.45, 0.15], scale: [0.99, 1.015, 0.99] }}
              transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
              style={{ originX: `${cx}px`, originY: `${cy}px` }}
            />
          )}

          {/* orbital guide rings — animated rotation during prompt processing */}
          <motion.circle
            cx={cx}
            cy={cy}
            r={rInnerOrbit}
            fill="none"
            stroke={telemetry.isProcessing ? "var(--accent)" : "var(--border)"}
            strokeDasharray={telemetry.isProcessing ? "3 5" : "1 4"}
            strokeWidth={telemetry.isProcessing ? 0.9 : 0.6}
            opacity={telemetry.isProcessing ? 0.9 : 0.7}
            animate={telemetry.isProcessing ? { rotate: 360 } : { rotate: 0 }}
            transition={telemetry.isProcessing ? { repeat: Infinity, duration: 20, ease: "linear" } : { duration: 0.5 }}
            style={{ originX: `${cx}px`, originY: `${cy}px` }}
          />
          <motion.circle
            cx={cx}
            cy={cy}
            r={rOuterRing}
            fill="none"
            stroke={telemetry.isProcessing ? "var(--warn)" : "var(--border)"}
            strokeDasharray={telemetry.isProcessing ? "4 6" : "1 4"}
            strokeWidth={telemetry.isProcessing ? 0.9 : 0.6}
            opacity={telemetry.isProcessing ? 0.75 : 0.5}
            animate={telemetry.isProcessing ? { rotate: -360 } : { rotate: 0 }}
            transition={telemetry.isProcessing ? { repeat: Infinity, duration: 32, ease: "linear" } : { duration: 0.5 }}
            style={{ originX: `${cx}px`, originY: `${cy}px` }}
          />

          {/* seat -> center connectors with animated photon streaming when processing */}
          {COUNCIL.map((seat) => {
            const a = (seat.angleDeg * Math.PI) / 180 - Math.PI / 2;
            const x = cx + Math.cos(a) * rInnerOrbit;
            const y = cy + Math.sin(a) * rInnerOrbit;
            const isFocused = effectiveFocus === seat.id;
            const isTelemetryActive = telemetry.isProcessing && telemetry.activeSeat === seat.id;
            const active = isFocused || isTelemetryActive;

            return (
              <g key={seat.id}>
                <line
                  x1={cx}
                  y1={cy}
                  x2={x}
                  y2={y}
                  stroke={active ? "var(--warn)" : "var(--border)"}
                  strokeWidth={active ? 1.4 : 0.6}
                  opacity={active ? 0.95 : 0.5}
                />
                {/* Streaming energy particle from seat to reactor during active processing */}
                {telemetry.isProcessing && (isTelemetryActive || isFocused) && (
                  <motion.circle
                    r={2.5}
                    fill="var(--warn)"
                    animate={{
                      cx: [x, cx],
                      cy: [y, cy],
                      opacity: [1, 0.3],
                    }}
                    transition={{
                      repeat: Infinity,
                      duration: 1.2,
                      ease: "easeInOut",
                    }}
                  />
                )}
              </g>
            );
          })}

          {/* skill dashes on outer ring — tiny grey ticks */}
          {skillNodes.map((node) => {
            const active = activeSkillSlugs.has(node.skill.slug);
            const isOwnerActive = telemetry.isProcessing && telemetry.activeSeat === node.skill.ownerSeat;
            const dimmed = effectiveFocus && node.skill.ownerSeat !== effectiveFocus;
            const angle = node.angle;
            const inner = rOuterRing - (isOwnerActive ? 6 : 4);
            const outer = rOuterRing + (isOwnerActive ? 6 : 4);
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
                stroke={active || isOwnerActive ? "var(--warn)" : "var(--text-3)"}
                strokeWidth={active || isOwnerActive ? 2 : 1}
                opacity={dimmed ? 0.15 : active || isOwnerActive ? 1 : 0.5}
                style={{ transition: "all 220ms cubic-bezier(0.22,1,0.36,1)" }}
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
            const isTelemetryActive = telemetry.isProcessing && telemetry.activeSeat === seat.id;
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
                fill={isTelemetryActive ? "var(--warn)" : "var(--text-3)"}
              >
                {seat.domain[0].toUpperCase()}
              </text>
            );
          })}
        </svg>

        {/* Council seats (HTML overlay with live processing beacons) */}
        {COUNCIL.map((seat) => {
          const a = (seat.angleDeg * Math.PI) / 180 - Math.PI / 2;
          const x = cx + Math.cos(a) * rInnerOrbit;
          const y = cy + Math.sin(a) * rInnerOrbit;
          const isFocused = effectiveFocus === seat.id;
          const pinned = pinnedSeat === seat.id;
          const isTelemetryActive = telemetry.isProcessing && telemetry.activeSeat === seat.id;
          const active = isFocused || isTelemetryActive;

          return (
            <button
              key={seat.id}
              onMouseEnter={() => setFocusedSeat(seat.id)}
              onMouseLeave={() => setFocusedSeat(null)}
              onClick={() => togglePinnedSeat(seat.id)}
              aria-pressed={pinned}
              title={pinned ? `${seat.codename} pinned — click to unpin` : `Click to pin ${seat.codename}`}
              className="absolute flex flex-col items-start justify-center transition-all cursor-pointer"
              style={{
                left: x - 52,
                top: y - 22,
                width: 104,
                height: 44,
                background: pinned ? "var(--accent)" : isTelemetryActive ? "rgba(255, 175, 40, 0.08)" : "var(--bg)",
                color: pinned ? "var(--ink)" : "var(--text)",
                border: `1px solid ${
                  pinned ? "var(--accent)" : isTelemetryActive ? "var(--warn)" : active ? "var(--border-strong)" : "var(--border)"
                }`,
                boxShadow: isTelemetryActive ? "0 0 14px rgba(255, 175, 40, 0.28)" : undefined,
                paddingLeft: 8,
                paddingRight: 8
              }}
            >
              <div className="flex items-center gap-1.5 w-full">
                <span
                  className={`dot ${isTelemetryActive ? "animate-pulse" : ""}`}
                  style={{
                    background: pinned ? "var(--ink)" : isTelemetryActive ? "var(--warn)" : active ? "var(--accent)" : "var(--ok)",
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
                  color: pinned ? "var(--ink)" : isTelemetryActive ? "var(--warn)" : "var(--text-3)",
                  marginLeft: 12,
                  marginTop: 1
                }}
              >
                {isTelemetryActive ? "// ACTIVE" : seat.role.split("//")[0].trim()}
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

      {/* Monolith Telemetry HUD — Live LLM Model Name & Prompt Processing State */}
      <div className="mt-4 flex flex-col items-center gap-1.5 pointer-events-none select-none">
        <div className="flex items-center gap-3 px-4 py-1.5 rounded-full bg-[rgba(10,10,12,0.92)] border border-[var(--border-strong)] backdrop-blur-md shadow-2xl">
          <span
            className={`w-2 h-2 rounded-full ${telemetry.isProcessing ? "animate-ping" : ""}`}
            style={{
              backgroundColor: telemetry.isProcessing ? "var(--warn)" : "var(--ok)",
              boxShadow: telemetry.isProcessing ? "0 0 10px var(--warn)" : "0 0 6px var(--ok)",
            }}
          />
          <span className="font-mono text-[10px] font-bold tracking-widest text-[var(--text)] uppercase">
            {telemetry.isProcessing ? "PROCESSING PROMPT" : "HARNESS STANDBY"}
          </span>
          <span className="text-[var(--border-strong)]">|</span>
          <span className="font-mono text-[10px] tracking-wider text-[var(--warn)] font-bold">
            MODEL: {telemetry.modelName}
          </span>
          <span className="text-[var(--border-strong)]">|</span>
          <span className="font-mono text-[9.5px] tracking-wider text-[var(--text-2)] font-medium">
            {telemetry.harness} {telemetry.stepIndex > 0 ? `· STEP #${telemetry.stepIndex}` : ""}
          </span>
        </div>
        {telemetry.activeTool && telemetry.isProcessing && (
          <div className="font-mono text-[9.5px] tracking-wider text-[var(--accent)] font-medium">
            ⚡ ACTIVE TOOL: {telemetry.activeTool} {telemetry.toolSummary ? `— ${telemetry.toolSummary}` : ""}
          </div>
        )}
      </div>
    </div>
  );
}
