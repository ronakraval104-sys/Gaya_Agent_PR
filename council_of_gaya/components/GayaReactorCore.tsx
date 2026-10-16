"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { GAYA_STATE_COLORS, type GayaState } from "./GayaSprite";

interface Props {
  size: number;
}

export function GayaReactorCore({ size }: Props) {
  const [telemetry, setTelemetry] = useState<{
    state: GayaState;
    detail: string;
    modelName: string;
    harness: string;
    activeSeat: string;
  }>({
    state: "idle",
    detail: "Sacred Bodhi Vanguard standing by",
    modelName: "Gemini 2.5 Pro (Thinking)",
    harness: "Google Antigravity",
    activeSeat: "bob",
  });

  useEffect(() => {
    let alive = true;
    const poll = async () => {
      try {
        const r = await fetch("/api/gaya-state", { cache: "no-store" });
        const j = await r.json();
        if (alive && j.state) {
          setTelemetry((prev) => ({
            ...prev,
            state: j.state,
            detail: j.detail || prev.detail,
            modelName: j.modelName || prev.modelName,
            harness: j.harness || prev.harness,
            activeSeat: j.activeSeat || prev.activeSeat,
          }));
        }
      } catch {}
    };
    poll();
    const id = setInterval(poll, 1500);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  const color = GAYA_STATE_COLORS[telemetry.state] || "#D4AF37";
  const avatarSize = Math.round(size * 0.72);

  return (
    <div
      className="relative w-full h-full rounded-full flex items-center justify-center overflow-hidden select-none group cursor-pointer"
      title={`CURRENT AGENT: GAYA // BODHI CORE\nState: ${telemetry.state.toUpperCase()}\nModel: ${telemetry.modelName}\nHarness: ${telemetry.harness}`}
    >
      {/* Deep well ambient glow */}
      <motion.div
        className="absolute inset-0 rounded-full pointer-events-none"
        animate={{
          boxShadow: [
            `inset 0 0 16px rgba(0, 0, 0, 0.95), 0 0 12px ${color}30`,
            `inset 0 0 24px rgba(0, 0, 0, 0.95), 0 0 20px ${color}55`,
            `inset 0 0 16px rgba(0, 0, 0, 0.95), 0 0 12px ${color}30`,
          ],
        }}
        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Rotating tactical radar reticle */}
      <motion.div
        className="absolute inset-2 rounded-full border border-dashed pointer-events-none"
        style={{ borderColor: `${color}40` }}
        animate={{ rotate: 360 }}
        transition={{ duration: 24, repeat: Infinity, ease: "linear" }}
      />

      {/* Counter-rotating fine tracking ring */}
      <motion.div
        className="absolute inset-4 rounded-full border border-dotted pointer-events-none"
        style={{ borderColor: `${color}25` }}
        animate={{ rotate: -360 }}
        transition={{ duration: 18, repeat: Infinity, ease: "linear" }}
      />

      {/* Avatar Container */}
      <div
        className="relative flex items-center justify-center rounded-full"
        style={{ width: avatarSize, height: avatarSize }}
      >
        {/* Halo Glow Mask */}
        <div
          className="absolute inset-0 pointer-events-none transition-opacity duration-500"
          style={{
            background: color,
            WebkitMaskImage: "url(/gaya/halo_glow.png)",
            maskImage: "url(/gaya/halo_glow.png)",
            WebkitMaskSize: "contain",
            maskSize: "contain",
            WebkitMaskRepeat: "no-repeat",
            maskRepeat: "no-repeat",
            WebkitMaskPosition: "center",
            maskPosition: "center",
            mixBlendMode: "screen",
            opacity: telemetry.state === "asleep" ? 0.3 : 0.85,
            filter: `drop-shadow(0 0 6px ${color})`,
          }}
        />

        {/* Halo Bloom Mask */}
        <div
          className="absolute inset-0 pointer-events-none transition-opacity duration-500"
          style={{
            background: color,
            WebkitMaskImage: "url(/gaya/halo_bloom.png)",
            maskImage: "url(/gaya/halo_bloom.png)",
            WebkitMaskSize: "contain",
            maskSize: "contain",
            WebkitMaskRepeat: "no-repeat",
            maskRepeat: "no-repeat",
            WebkitMaskPosition: "center",
            maskPosition: "center",
            mixBlendMode: "screen",
            opacity: telemetry.state === "asleep" ? 0.2 : 0.65,
          }}
        />

        {/* Gaya Sacred Gold Avatar Base */}
        <motion.img
          src="/gaya/avatar_base.png"
          alt="Gaya Core Active Agent"
          className="relative z-10 w-full h-full object-contain pointer-events-none drop-shadow-[0_4px_10px_rgba(0,0,0,0.9)]"
          animate={{
            scale: [1, 1.02, 1],
            y: [0, -1.5, 0],
          }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      {/* Live "ACTIVE AGENT" HUD Tag */}
      <div className="absolute bottom-1 z-20 flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-black/80 border border-white/10 backdrop-blur-sm pointer-events-none shadow-md">
        <span
          className="w-1.5 h-1.5 rounded-full"
          style={{
            backgroundColor: color,
            boxShadow: `0 0 6px ${color}`,
          }}
        />
        <span className="font-mono text-[8px] uppercase tracking-[0.16em] text-os-text font-bold">
          ACTIVE
        </span>
      </div>
    </div>
  );
}
