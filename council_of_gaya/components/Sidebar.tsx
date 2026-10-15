"use client";

import { useEffect, useState } from "react";
import { useJarvis } from "@/lib/store";
import { COUNCIL } from "@/lib/council";
import { Dot } from "./terminal";
import { computeAura, auraDotState, auraLabel } from "@/lib/aura";

interface NavItem {
  label: string;
  href?: string;
  onClick?: () => void;
  active?: boolean;
  hint?: string;
  status?: "ok" | "warn" | "err" | "off";
}

export function Sidebar() {
  const pinnedSeat = useJarvis((s) => s.pinnedSeat);
  const togglePinnedSeat = useJarvis((s) => s.togglePinnedSeat);
  const toggleConsole = useJarvis((s) => s.toggleConsole);
  const openRecord = useJarvis((s) => s.openRecord);
  const chronicle = useJarvis((s) => s.chronicle);
  const chronicleVisible = useJarvis((s) => s.chronicleVisible);
  const toggleChronicleVisible = useJarvis((s) => s.toggleChronicleVisible);
  const settingsOpen = useJarvis((s) => s.settingsOpen);
  const toggleSettings = useJarvis((s) => s.toggleSettings);

  // Aura tracker — hydration-safe: server render is neutral, client updates
  // on mount + every 30s so relative activity windows stay honest.
  const [mounted, setMounted] = useState(false);
  const [tick, setTick] = useState(0);
  useEffect(() => {
    setMounted(true);
    const id = setInterval(() => setTick((t) => t + 1), 30_000);
    return () => clearInterval(id);
  }, []);
  const aura = mounted
    ? computeAura(chronicle)
    : {
        title: "👑 Bodhi Commander",
        level: 8,
        sessionXp: 0,
        xpForNext: 100,
        pctToNext: 0,
        aura: "cold" as const,
        recentEventCount: 0,
        totalEvents: 0
      };

  return (
    <aside
      className="hidden lg:flex flex-col w-[220px] shrink-0 border-r border-os-border bg-os-bg sticky top-0"
      style={{ height: "calc(100vh - 32px)" }}
      aria-label="Primary navigation"
    >
      {/* wordmark — fixed top */}
      <div className="px-4 pt-4 pb-6 border-b border-os-border shrink-0">
        <div className="flex items-center gap-2">
          <div
            aria-hidden
            className="w-5 h-5 border border-os-border-strong grid place-items-center shadow-[0_0_8px_rgba(212,175,55,0.3)]"
          >
            <span className="w-1.5 h-1.5 bg-os-accent" />
          </div>
          <div className="font-mono text-[13px] font-bold uppercase tracking-[0.12em] text-os-text">
            COUNCIL OF GAYA
          </div>
        </div>
        <div className="mt-1 pl-7 font-mono text-[9px] uppercase tracking-[0.22em] text-os-accent opacity-80">
          Bodhi Vanguard · OS
        </div>
      </div>

      {/* scrollable nav area — flex-1 so it eats remaining space,
          overflow-y-auto so aura stays pinned regardless of viewport height */}
      <div className="flex-1 min-h-0 overflow-y-auto">
        <NavGroup title="Operate">
          <NavRow label="Home" active hint="/" />
        </NavGroup>

        <NavGroup title="Council Specialists">
          {COUNCIL.map((seat) => (
            <NavRow
              key={seat.id}
              label={`${seat.avatarIcon} ${seat.codename}`}
              active={pinnedSeat === seat.id}
              onClick={() => togglePinnedSeat(seat.id)}
              status={pinnedSeat === seat.id ? "ok" : "off"}
            />
          ))}
        </NavGroup>

        <NavGroup title="Knowledge">
          <NavRow
            label="Boulder Rules"
            onClick={() => openRecord("microtronix-gstin-bank")}
            hint="🚨"
            status="err"
          />
          <NavRow
            label="Domain Laws"
            onClick={() => openRecord("law-katviz-is-sir-or-katviz-always")}
            status="warn"
          />
          <NavRow
            label="All Records"
            onClick={toggleConsole}
            hint="/search"
          />
        </NavGroup>

        <NavGroup title="System">
          <NavRow label="Console" onClick={toggleConsole} hint="⌘K" />
          <NavRow
            label="Chronicle"
            onClick={toggleChronicleVisible}
            active={chronicleVisible}
            hint={chronicleVisible ? "✓" : "off"}
          />
          <NavRow
            label="Settings"
            onClick={toggleSettings}
            active={settingsOpen}
            hint="⚙"
          />
          <NavRow label="Persona" hint="GAYA" />
        </NavGroup>
      </div>

      {/* bottom status — aura tracker, ALWAYS visible (shrink-0 pinned) */}
      <div className="shrink-0 border-t border-os-border">
        {/* title + level line */}
        <div className="px-4 pt-3 pb-2 flex items-center justify-between">
          <div className="font-mono text-[11px] font-bold text-os-text">
            {aura.title}
          </div>
          <div className="font-mono text-[9px] uppercase tracking-[0.16em] text-os-dim">
            L{aura.level}
          </div>
        </div>

        {/* XP progress bar — hairline */}
        <div className="px-4">
          <div className="h-[3px] w-full bg-os-surface2 relative">
            <div
              className="h-full bg-os-accent transition-[width] duration-500 ease-out"
              style={{ width: `${aura.pctToNext}%` }}
            />
          </div>
        </div>

        {/* aura state + xp count */}
        <div className="px-4 pt-2 pb-2 flex items-center justify-between">
          <div className="flex items-center gap-1.5 font-mono text-[9px] uppercase tracking-[0.16em]">
            <Dot state={auraDotState(aura.aura)} pulse={aura.aura === "alive"} />
            <span
              style={{
                color:
                  aura.aura === "alive" ? "var(--ok)"
                  : aura.aura === "warm" ? "var(--warn)"
                  : "var(--text-3)"
              }}
            >
              {auraLabel(aura.aura)}
            </span>
          </div>
          <div className="font-mono text-[9px] uppercase tracking-[0.14em] text-os-dim">
            {aura.sessionXp} XP · {aura.recentEventCount}/5m
          </div>
        </div>

        {/* system hairline */}
        <div className="px-4 pb-3 border-t border-os-hairline pt-2">
          <div className="flex items-center gap-2 font-mono text-[9px] text-os-dim">
            <Dot state="ok" pulse />
            <span>localhost:4200 · lowdb · live</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

function NavGroup({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="px-2 py-3 border-b border-os-border">
      <div className="px-2 pb-2 font-mono text-[9px] font-bold uppercase tracking-[0.26em] text-os-dim">
        {title}
      </div>
      <div className="flex flex-col gap-0.5">{children}</div>
    </div>
  );
}

function NavRow({ label, hint, active, onClick, status }: NavItem) {
  const Content = (
    <>
      <div className="flex items-center gap-2 min-w-0">
        {status && <Dot state={status} />}
        <span className="truncate">{label}</span>
      </div>
      {hint && (
        <span className="font-mono text-[9px] text-os-dim uppercase tracking-[0.14em]">
          {hint}
        </span>
      )}
    </>
  );

  const className = `flex items-center justify-between px-2 py-1.5 font-mono text-[12px] ${
    active
      ? "bg-os-surface2 text-os-text border-l-2 border-os-accent"
      : "text-os-muted hover:bg-os-surface2 hover:text-os-text border-l-2 border-transparent"
  } transition-colors cursor-pointer`;

  if (onClick) {
    return (
      <button type="button" onClick={onClick} className={className}>
        {Content}
      </button>
    );
  }
  return <div className={className}>{Content}</div>;
}
