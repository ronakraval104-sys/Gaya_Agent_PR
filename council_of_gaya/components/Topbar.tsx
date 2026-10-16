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
    <div className="h-11 border-b border-os-border bg-os-bg sticky top-0 z-40 flex items-center justify-between px-4">
      {/* breadcrumb */}
      <div className="flex items-center gap-2 font-mono text-[11px]">
        <GayaSprite size={30} />
        <span className="text-os-dim ml-2">council-of-gaya</span>
        <span className="text-os-dim">/</span>
        <span className="text-os-text">home</span>
      </div>

      {/* right — persona pill + palette hint */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1 border border-os-border bg-os-surface2/60 shadow-[0_0_12px_rgba(212,175,55,0.15)] font-mono text-[10px] uppercase tracking-[0.16em]">
          <span className="w-1.5 h-1.5 rounded-full bg-os-accent shadow-[0_0_6px_var(--accent)] animate-pulse" />
          <span className="text-os-dim">context ::</span>
          <span className="text-os-accent font-bold">GAYA CORE</span>
          <span className="text-os-dim">·</span>
          <span className="text-os-muted">BODHI VANGUARD</span>
        </div>

        <button
          onClick={toggleConsole}
          className="flex items-center gap-1.5 px-2 py-1 font-mono text-[10px] text-os-muted hover:text-os-text border border-os-border hover:border-os-border-strong transition-colors"
          title="Open console"
        >
          <span>search or command</span>
          <Kbd>⌘K</Kbd>
        </button>
      </div>
    </div>
  );
}
