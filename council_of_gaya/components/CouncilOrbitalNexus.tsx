"use client";

import { useState } from "react";
import Image from "next/image";
import { useGaya } from "@/lib/store";
import { type CouncilSeatId } from "@/lib/council";
import { Dot } from "./terminal";

interface AgentOrbitalSpec {
  id: CouncilSeatId;
  name: string;
  codename: string;
  icon: string;
  avatar: string;
  role: string;
  skill: string;
  color: string;
  glowColor: string;
  status: string;
  angleDeg: number; // orbital position around center
}

const AGENTS: AgentOrbitalSpec[] = [
  {
    id: "logos",
    name: "LOGOS",
    codename: "MIND // ARCHITECT",
    icon: "🛡️",
    avatar: "/agents/logos.png",
    role: "Mastermind Planner & Hard-Check QC Gate",
    skill: "writing-plans",
    color: "#38BDF8",
    glowColor: "rgba(56, 189, 248, 0.7)",
    status: "ARMED · QC GATE PASS",
    angleDeg: 270 // Top / North (12 o'clock)
  },
  {
    id: "bob",
    name: "Bob",
    codename: "HANDS // BUILDER",
    icon: "🔨",
    avatar: "/agents/bob.png",
    role: "Precision Builder & Execution Engine",
    skill: "deploy-ops",
    color: "#F59E0B",
    glowColor: "rgba(245, 158, 11, 0.7)",
    status: "STANDBY · BUILD ENGINE",
    angleDeg: 0 // Right / East (3 o'clock) - Profile facing LEFT towards Gaya Core
  },
  {
    id: "freya",
    name: "Freya",
    codename: "HEART // DESIGNER",
    icon: "🎨",
    avatar: "/agents/freya.png",
    role: "Polymath Designer & Seer of Visual Truth",
    skill: "frontend-design",
    color: "#10B981",
    glowColor: "rgba(16, 185, 129, 0.7)",
    status: "ACTIVE · VISUAL MATRIX",
    angleDeg: 90 // Bottom / South (6 o'clock)
  },
  {
    id: "tvashtar",
    name: "Tvashtar",
    codename: "CRAFTSMAN // ARCHITECT",
    icon: "🦾",
    avatar: "/agents/tvashtar.png",
    role: "Systems Architect, REA Engine & Toolkeeper",
    skill: "reverse-engineer-anything",
    color: "#EC4899",
    glowColor: "rgba(236, 72, 153, 0.7)",
    status: "ONLINE · REA ACTIVE",
    angleDeg: 180 // Left / West (9 o'clock) - Profile facing RIGHT towards Gaya Core
  }
];

export function CouncilOrbitalNexus() {
  const pinnedSeat = useGaya((s) => s.pinnedSeat);
  const togglePinnedSeat = useGaya((s) => s.togglePinnedSeat);
  const [hoveredAgent, setHoveredAgent] = useState<CouncilSeatId | null>(null);

  const activeAgent = hoveredAgent 
    ? AGENTS.find((a) => a.id === hoveredAgent) 
    : pinnedSeat 
    ? AGENTS.find((a) => a.id === pinnedSeat) 
    : null;

  const ORBITAL_RADIUS = 150; // Exact radial distance from center

  return (
    <div className="w-full border border-os-border bg-os-surface/70 relative overflow-hidden p-6 md:p-8 backdrop-blur-sm shadow-2xl">
      {/* Ambient background tactical grid and watermark */}
      <div 
        className="absolute inset-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: "radial-gradient(circle, var(--accent) 1px, transparent 1px)",
          backgroundSize: "28px 28px"
        }}
      />
      <div className="absolute top-3 right-4 font-mono text-xs uppercase tracking-[0.24em] text-os-dim flex items-center gap-2">
        <Dot state="ok" pulse />
        <span>Grand Council Nexus · All Specialists Synchronized</span>
      </div>

      <div className="flex flex-col items-center justify-center gap-8 relative z-10 w-full">
        {/* Orbital Constellation Graphic - Centered & Balanced Spacing */}
        <div className="relative w-[360px] h-[360px] sm:w-[420px] sm:h-[420px] flex items-center justify-center select-none my-4">
          {/* Outer Orbital Boundary Ring */}
          <div className="absolute inset-0 rounded-full border border-os-border-strong/30 animate-[spin_120s_linear_infinite]" />
          <div className="absolute inset-3 rounded-full border border-dashed border-os-accent/20 animate-[spin_80s_linear_infinite_reverse]" />
          
          {/* Subtle concentric tactical rings */}
          <div className="absolute w-[300px] h-[300px] rounded-full border border-os-border/40" />
          <div className="absolute w-[210px] h-[210px] rounded-full border border-os-accent/25" />

          {/* Central Core: GAYA NEXUS */}
          <div 
            onClick={() => togglePinnedSeat(pinnedSeat ?? "logos")}
            className="group cursor-pointer relative z-20 flex flex-col items-center justify-center"
            title="Click to reset focus to Gaya Nexus"
          >
            <div className="relative w-24 h-24 sm:w-28 sm:h-28 rounded-full border-2 border-os-accent bg-os-bg flex items-center justify-center shadow-[0_0_24px_rgba(212,175,55,0.35)] transition-all duration-300 group-hover:scale-105 group-hover:shadow-[0_0_36px_rgba(212,175,55,0.85)]">
              {/* Reactive Halo Bloom */}
              <div 
                className="absolute inset-0 pointer-events-none animate-pulse transition-opacity duration-300 group-hover:opacity-100"
                style={{
                  backgroundImage: "url('/gaya/halo_bloom.png')",
                  backgroundSize: "cover",
                  backgroundPosition: "center",
                  opacity: 0.65
                }}
              />
              {/* Reactive Halo Glow */}
              <div 
                className="absolute inset-0 pointer-events-none transition-opacity duration-300 group-hover:opacity-95"
                style={{
                  backgroundImage: "url('/gaya/halo_glow.png')",
                  backgroundSize: "cover",
                  backgroundPosition: "center",
                  opacity: 0.5
                }}
              />
              {/* Gaya Core Avatar: Scaled down, 50% opacity default, radiant interactive gold glow */}
              <div className="relative w-14 h-14 sm:w-16 sm:h-16 z-10 opacity-50 group-hover:opacity-100 group-hover:scale-110 transition-all duration-300">
                <Image
                  src="/gaya/avatar_base.png"
                  alt="Gaya Core Avatar"
                  fill
                  className="object-contain drop-shadow-[0_0_12px_rgba(212,175,55,0.7)] group-hover:drop-shadow-[0_0_26px_rgba(212,175,55,1)]"
                  priority
                />
              </div>

              {/* Status Badge in Center Core */}
              <div className="absolute -bottom-3 px-2.5 py-0.5 bg-os-bg border border-os-accent text-[11px] font-mono font-bold uppercase tracking-wider text-os-accent rounded-sm shadow-md whitespace-nowrap z-20">
                GAYA CORE
              </div>
            </div>
          </div>

          {/* 4 Orbital Agent Nodes with Orientation-Aligned Profiles & Matching Visual Treatment */}
          {AGENTS.map((agent) => {
            const isHovered = hoveredAgent === agent.id;
            const isPinned = pinnedSeat === agent.id;
            const isActive = isHovered || isPinned;

            // Geometry calculations for exact centered radial placement
            const rad = (agent.angleDeg * Math.PI) / 180;
            const x = Math.round(ORBITAL_RADIUS * Math.cos(rad));
            const y = Math.round(ORBITAL_RADIUS * Math.sin(rad));

            return (
              <div
                key={agent.id}
                style={{
                  left: `calc(50% + ${x}px)`,
                  top: `calc(50% + ${y}px)`,
                  transform: "translate(-50%, -50%)"
                }}
                className="absolute z-30 transition-all duration-300"
              >
                {/* Connecting Laser Ley-line to Core */}
                <div 
                  className="absolute pointer-events-none origin-left h-[1.5px] transition-opacity duration-300"
                  style={{
                    width: `${ORBITAL_RADIUS}px`,
                    left: "50%",
                    top: "50%",
                    transform: `rotate(${agent.angleDeg + 180}deg)`,
                    background: isActive 
                      ? `linear-gradient(90deg, ${agent.color}, transparent)` 
                      : "linear-gradient(90deg, rgba(77,63,51,0.4), transparent)",
                    opacity: isActive ? 1 : 0.35
                  }}
                />

                {/* Agent Pod Button with 50% opacity default and radiant glow on interaction */}
                <button
                  type="button"
                  onClick={() => togglePinnedSeat(agent.id)}
                  onMouseEnter={() => setHoveredAgent(agent.id)}
                  onMouseLeave={() => setHoveredAgent(null)}
                  className={`group relative flex flex-col items-center justify-center p-1.5 rounded-full border transition-all duration-300 ${
                    isActive
                      ? "bg-os-surface border-os-accent shadow-2xl scale-110"
                      : "bg-os-bg/95 border-os-border hover:border-os-border-strong hover:bg-os-surface2"
                  }`}
                  style={{
                    borderColor: isActive ? agent.color : undefined,
                    boxShadow: isActive ? `0 0 22px ${agent.glowColor}` : undefined
                  }}
                  title={`${agent.name} (${agent.codename}) - Click to inspect`}
                >
                  {/* Circular Avatar Frame with 50% opacity default & interactive glow */}
                  <div 
                    className="relative w-14 h-14 sm:w-16 sm:h-16 rounded-full overflow-hidden flex items-center justify-center transition-all duration-300"
                    style={{
                      borderColor: isActive ? agent.color : "var(--border)",
                      backgroundColor: isActive ? "rgba(0,0,0,0.7)" : "rgba(10,10,12,0.85)"
                    }}
                  >
                    <Image
                      src={agent.avatar}
                      alt={agent.name}
                      fill
                      className={`object-cover transition-all duration-300 ${
                        isActive
                          ? "opacity-100 scale-105"
                          : "opacity-50 group-hover:opacity-100 group-hover:scale-105"
                      }`}
                      style={{
                        filter: isActive ? `drop-shadow(0 0 10px ${agent.glowColor})` : undefined
                      }}
                    />
                  </div>

                  {/* Micro Name Pill Attached to Pod */}
                  <div 
                    className="absolute -bottom-4 px-2 py-0.5 bg-os-bg border text-[10px] font-mono font-bold uppercase tracking-wider rounded-sm shadow-md whitespace-nowrap z-20 transition-colors"
                    style={{
                      borderColor: isActive ? agent.color : "var(--border)",
                      color: isActive ? agent.color : "var(--text-muted)"
                    }}
                  >
                    {agent.name}
                  </div>

                  {/* Active Indicator Pip */}
                  {isPinned && (
                    <span 
                      className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full animate-ping"
                      style={{ backgroundColor: agent.color }}
                    />
                  )}
                </button>
              </div>
            );
          })}
        </div>

        {/* Centered Council Directive & Specialist Dossier Card */}
        <div className="w-full max-w-3xl bg-os-bg border border-os-border p-6 shadow-xl relative text-left">
          <div className="flex items-center justify-between border-b border-os-border pb-3 mb-4">
            <div className="font-mono text-sm font-bold uppercase tracking-[0.16em] text-os-accent flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-os-accent animate-pulse" />
              <span>COUNCIL COMMAND PROTOCOL</span>
            </div>
            <div className="font-mono text-xs text-os-dim uppercase tracking-wider">
              {activeAgent ? "SPECIALIST FOCUS" : "UNIFIED COUNCIL DECK"}
            </div>
          </div>

          {activeAgent ? (
            <div className="space-y-4 animate-in fade-in duration-200">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <div className="relative w-10 h-10 rounded-full border overflow-hidden shrink-0" style={{ borderColor: activeAgent.color }}>
                      <Image
                        src={activeAgent.avatar}
                        alt={activeAgent.name}
                        fill
                        className="object-cover"
                      />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span 
                          className="font-mono text-xl font-bold uppercase tracking-wide"
                          style={{ color: activeAgent.color }}
                        >
                          {activeAgent.name}
                        </span>
                        <span className="font-mono text-xs px-2 py-0.5 border border-os-border bg-os-surface text-os-muted uppercase">
                          {activeAgent.codename}
                        </span>
                      </div>
                      <div className="font-mono text-sm text-os-text mt-0.5 font-medium">
                        {activeAgent.role}
                      </div>
                    </div>
                  </div>
                </div>
                <div 
                  className="font-mono text-xs px-2.5 py-1 uppercase tracking-widest font-semibold border rounded-sm"
                  style={{
                    borderColor: activeAgent.color,
                    color: activeAgent.color,
                    backgroundColor: `${activeAgent.color}15`
                  }}
                >
                  {activeAgent.status}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="border border-os-border bg-os-surface/60 p-3">
                  <div className="font-mono text-xs uppercase tracking-wider text-os-dim mb-1">
                    Assigned Primary Skill
                  </div>
                  <div className="font-mono text-sm text-os-accent font-bold truncate">
                    {activeAgent.skill}
                  </div>
                </div>
                <div className="border border-os-border bg-os-surface/60 p-3">
                  <div className="font-mono text-xs uppercase tracking-wider text-os-dim mb-1">
                    Direct Focus Target
                  </div>
                  <div className="font-mono text-sm text-os-ok font-bold truncate">
                    {pinnedSeat === activeAgent.id ? "ACTIVE PINNED" : "CLICK POD TO PIN"}
                  </div>
                </div>
              </div>

              <div className="font-mono text-xs text-os-muted leading-relaxed border-t border-os-hairline pt-3">
                {activeAgent.id === "logos" && (
                  <span>Mandatory QC Gate: master architect that verifies plan trees, prevents regression, and requires strict verification verdicts before code commits ship.</span>
                )}
                {activeAgent.id === "bob" && (
                  <span>Precision hands: turns specs into atomic commits, manages builds, dependency hygiene, test passes, and live server deployments.</span>
                )}
                {activeAgent.id === "freya" && (
                  <span>Visual visionary: high-taste design floor, typographic hierarchy, responsive viewport geometry, vector polish, and brand truth.</span>
                )}
                {activeAgent.id === "tvashtar" && (
                  <span>Craftsman & reverse engineering engine: deep binary disassembly, ASAR extraction, protocol reconstruction, and spatial 3D tools.</span>
                )}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <span className="text-3xl">👑</span>
                <div>
                  <div className="font-mono text-xl font-bold uppercase tracking-wider text-os-accent">
                    Gaya Vanguard Mesh
                  </div>
                  <div className="font-mono text-sm text-os-dim">
                    Four Specialists. One Unified Intelligence. Real-Time Telemetry.
                  </div>
                </div>
              </div>

              <p className="font-mono text-sm text-os-text leading-relaxed">
                Gaya commands the Council of Specialists through strict No-Ventriloquism Tagged Protocols. Click any orbital node to inspect that specialist&apos;s active skill assignment, telemetry, and execution gates.
              </p>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2">
                {AGENTS.map((a) => (
                  <button
                    key={a.id}
                    type="button"
                    onClick={() => togglePinnedSeat(a.id)}
                    className="p-2.5 border border-os-border bg-os-surface/80 hover:border-os-accent text-left transition-colors flex items-center gap-2.5"
                  >
                    <div className="relative w-8 h-8 rounded-full border overflow-hidden shrink-0" style={{ borderColor: a.color }}>
                      <Image
                        src={a.avatar}
                        alt={a.name}
                        fill
                        className="object-cover"
                      />
                    </div>
                    <div className="min-w-0">
                      <div className="font-mono text-xs font-bold text-os-text truncate">
                        {a.name}
                      </div>
                      <div className="font-mono text-[10px] text-os-dim uppercase truncate">
                        {a.codename.split("//")[0].trim()}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
