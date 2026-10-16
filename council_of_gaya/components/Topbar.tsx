"use client";

import { useEffect, useRef } from "react";
import { useGaya } from "@/lib/store";
import { PERSONAS, type PersonaId } from "@/lib/personas";
import { Kbd } from "./terminal";
import { GayaSprite } from "./GayaSprite";

export function Topbar() {
  const persona = useGaya((s) => s.persona);
  const swapPersona = useGaya((s) => s.swapPersona);
  const setPersona = useGaya((s) => s.setPersona);
  const toggleConsole = useGaya((s) => s.toggleConsole);
  const p = PERSONAS[persona];

  useEffect(() => {
    if (useGaya.getState().persona !== "gaya-core") {
      setPersona("gaya-core");
    }
  }, [setPersona]);

  return (
    <div className="h-14 border-b border-os-border bg-os-bg sticky top-0 z-40 flex items-center justify-between px-6">
      {/* breadcrumb */}
      <div className="flex items-center gap-3 font-mono text-sm">
        <GayaSprite size={36} />
        <span className="text-os-dim ml-1">council-of-gaya</span>
        <span className="text-os-dim">/</span>
        <span className="text-os-text font-bold">mission-cockpit</span>
      </div>

      {/* right — persona pill + palette hint */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5 px-3.5 py-1.5 border border-os-border bg-os-surface2/60 shadow-[0_0_14px_rgba(212,175,55,0.2)] font-mono text-xs uppercase tracking-[0.16em]">
          <span className="w-2 h-2 rounded-full bg-os-accent shadow-[0_0_8px_var(--accent)] animate-pulse" />
          <span className="text-os-dim">context ::</span>
          <span className="text-os-accent font-bold">GAYA CORE</span>
          <span className="text-os-dim">·</span>
          <span className="text-os-muted">BODHI VANGUARD</span>
        </div>

        <button
          onClick={toggleConsole}
          className="flex items-center gap-2 px-3 py-1.5 font-mono text-xs text-os-muted hover:text-os-text border border-os-border hover:border-os-accent transition-colors"
          title="Open console"
        >
          <span>search or command</span>
          <Kbd>⌘K</Kbd>
        </button>
      </div>
    </div>
  );
}
