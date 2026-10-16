"use client";

import { useEffect, useState } from "react";

// GayaSprite — The Sacred Bodhi Commander & Vanguard Core
// Displays Mini Gaya's portrait with reactive halo glow, bloom, and live state telemetry.

export type GayaState = "idle" | "thinking" | "spawning" | "hold" | "broken" | "approved" | "asleep";

export const GAYA_STATE_COLORS: Record<GayaState, string> = {
  idle: "#D4AF37",      // Sacred Bodhi Gold
  thinking: "#FFD73C",  // Radiant Solar Golden
  spawning: "#FFE066",  // Celestial Amber
  hold: "#FFAA00",      // Warning Amber
  broken: "#FF3B3B",    // Ruby Crimson Alert
  approved: "#2FD36F",  // Emerald Bodhi Pass
  asleep: "#7A7067",    // Dim Obsidian Slumber
};

export function GayaSprite({
  size = 32,
  showLabel = true,
  interactive = true,
}: {
  size?: number;
  showLabel?: boolean;
  interactive?: boolean;
}) {
  const [s, setS] = useState<{ state: GayaState; detail: string; armed: string }>({
    state: "idle",
    detail: "Sacred Bodhi Vanguard standing by",
    armed: "PASS",
  });

  useEffect(() => {
    let alive = true;
    const tick = async () => {
      try {
        const r = await fetch("/api/gaya-state", { cache: "no-store" });
        const j = await r.json();
        if (alive && j.state) setS(j);
      } catch {}
    };
    tick();
    const id = setInterval(tick, 1500);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  const c = GAYA_STATE_COLORS[s.state] || "#D4AF37";

  const mask = (img: string): React.CSSProperties => ({
    position: "absolute",
    inset: 0,
    background: c,
    WebkitMaskImage: `url(/gaya/${img})`,
    maskImage: `url(/gaya/${img})`,
    WebkitMaskSize: "contain",
    maskSize: "contain",
    WebkitMaskRepeat: "no-repeat",
    maskRepeat: "no-repeat",
    WebkitMaskPosition: "center",
    maskPosition: "center",
  });

  return (
    <div
      className="flex items-center gap-2.5 select-none"
      title={`GAYA CORE — ${s.state.toUpperCase()}\n${s.detail || "Bodhi Vanguard active"}`}
    >
      <div
        className={`relative flex items-center justify-center transition-transform duration-300 ${
          interactive ? "hover:scale-105 cursor-pointer" : ""
        }`}
        style={{ width: size, height: size }}
      >
        {/* State aura ring */}
        <div
          className="absolute inset-0 rounded-full transition-all duration-700 pointer-events-none"
          style={{
            boxShadow: `0 0 ${s.state === "asleep" ? "4px" : "12px"} ${c}35`,
            border: `1px solid ${c}50`,
          }}
        />

        {/* Halo Glow Layer recoloured by state */}
        <div
          className="pointer-events-none transition-opacity duration-500"
          style={{
            ...mask("halo_glow.png"),
            mixBlendMode: "screen",
            opacity: s.state === "asleep" ? 0.35 : 0.9,
            filter: `drop-shadow(0 0 3px ${c})`,
          }}
        />

        {/* Halo Bloom Layer */}
        <div
          className="pointer-events-none transition-opacity duration-500"
          style={{
            ...mask("halo_bloom.png"),
            mixBlendMode: "screen",
            opacity: s.state === "asleep" ? 0.2 : 0.65,
          }}
        />

        {/* Gaya Base Portrait */}
        <img
          src="/gaya/avatar_base.png"
          alt="Gaya Core"
          className="relative z-10 w-full h-full object-contain pointer-events-none drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)]"
        />

        {/* State mini badge dot */}
        <span
          className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full border border-os-bg z-20 transition-colors duration-500"
          style={{
            backgroundColor: c,
            boxShadow: `0 0 5px ${c}`,
          }}
        />
      </div>

      {showLabel && (
        <span
          className="font-mono text-[10px] uppercase tracking-[0.16em]"
          style={{ color: s.state === "idle" || s.state === "asleep" ? undefined : c }}
        >
          <span className="text-os-accent font-bold">GAYA</span>
          <span className="text-os-dim"> · </span>
          <span className={s.state === "idle" || s.state === "asleep" ? "text-os-muted" : "font-semibold"}>
            {s.state}
          </span>
        </span>
      )}
    </div>
  );
}

// Backward compatibility alias for any component still importing JarvisSprite
export const JarvisSprite = GayaSprite;
