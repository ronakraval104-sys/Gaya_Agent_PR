"use client";

import { useEffect, useState } from "react";
import { useGaya } from "@/lib/store";
import { COUNCIL } from "@/lib/council";
import { Dot } from "./terminal";
import { computeAura, auraDotState, auraLabel } from "@/lib/aura";
import { ArcReactor } from "./ArcReactor";

interface NavItem {
  label: string;
  href?: string;
  onClick?: () => void;
  active?: boolean;
  hint?: string;
  status?: "ok" | "warn" | "err" | "off";
}

export function Sidebar() {
  const pinnedSeat = useGaya((s) => s.pinnedSeat);
  const togglePinnedSeat = useGaya((s) => s.togglePinnedSeat);
  const toggleConsole = useGaya((s) => s.toggleConsole);
  const openRecord = useGaya((s) => s.openRecord);
  const chronicle = useGaya((s) => s.chronicle);
  const chronicleVisible = useGaya((s) => s.chronicleVisible);
  const toggleChronicleVisible = useGaya((s) => s.toggleChronicleVisible);
  const settingsOpen = useGaya((s) => s.settingsOpen);
  const toggleSettings = useGaya((s) => s.toggleSettings);

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
      className="hidden lg:flex flex-col w-[275px] shrink-0 border-r border-os-border bg-os-bg sticky top-0"
      style={{ height: "calc(100vh - 32px)" }}
      aria-label="Primary navigation"
    >
      {/* wordmark — fixed top */}
      <div className="px-5 pt-5 pb-5 border-b border-os-border shrink-0">
        <div className="flex items-center gap-2.5">
          <div
            aria-hidden
            className="w-6 h-6 border border-os-border-strong grid place-items-center shadow-[0_0_10px_rgba(212,175,55,0.4)]"
          >
            <span className="w-2 h-2 bg-os-accent" />
          </div>
          <div className="font-mono text-base font-bold uppercase tracking-[0.14em] text-os-text">
            COUNCIL OF GAYA
          </div>
        </div>
        <div className="mt-1 pl-8 font-mono text-xs uppercase tracking-[0.22em] text-os-accent opacity-90">
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
            onClick={() => openRecord("law-v10-harness")}
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
      <div className="shrink-0 border-t border-os-border bg-os-surface/40">
        {/* title + level line */}
        <div className="px-5 pt-3.5 pb-2 flex items-center justify-between">
          <div className="font-mono text-sm font-bold text-os-text">
            {aura.title}
          </div>
          <div className="font-mono text-xs uppercase tracking-[0.16em] text-os-accent font-bold">
            L{aura.level}
          </div>
        </div>

        {/* XP progress bar — hairline */}
        <div className="px-5">
          <div className="h-[4px] w-full bg-os-surface2 relative">
            <div
              className="h-full bg-os-accent transition-[width] duration-500 ease-out"
              style={{ width: `${aura.pctToNext}%` }}
            />
          </div>
        </div>

        {/* aura state + xp count */}
        <div className="px-5 pt-2.5 pb-2.5 flex items-center justify-between">
          <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-[0.16em]">
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
          <div className="font-mono text-xs uppercase tracking-[0.14em] text-os-dim">
            {aura.sessionXp} XP · {aura.recentEventCount}/5m
          </div>
        </div>

        {/* system hairline */}
        <div className="px-5 pb-3 border-t border-os-hairline pt-2">
          <div className="flex items-center gap-2 font-mono text-xs text-os-dim">
            <Dot state="ok" pulse />
            <span>localhost:4200 · live</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

function NavGroup({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="px-3 py-3.5 border-b border-os-border">
      <div className="px-3 pb-2 font-mono text-xs font-bold uppercase tracking-[0.24em] text-os-dim">
        {title}
      </div>
      <div className="flex flex-col gap-1">{children}</div>
    </div>
  );
}

function NavRow({ label, hint, active, onClick, status }: NavItem) {
  const Content = (
    <>
      <div className="flex items-center gap-2.5 min-w-0">
        {status && <Dot state={status} />}
        <span className="truncate">{label}</span>
      </div>
      {hint && (
        <span className="font-mono text-xs text-os-dim uppercase tracking-[0.14em] shrink-0">
          {hint}
        </span>
      )}
    </>
  );

  const className = `flex items-center justify-between px-3 py-2 font-mono text-sm ${
    active
      ? "bg-os-surface2 text-os-text border-l-2 border-os-accent font-semibold"
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
