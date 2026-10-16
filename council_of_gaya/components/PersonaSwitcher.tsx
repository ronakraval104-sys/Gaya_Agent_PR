"use client";

import { useGaya } from "@/lib/store";
import { PERSONAS } from "@/lib/personas";

export function PersonaSwitcher() {
  const persona = useGaya((s) => s.persona);
  const p = PERSONAS[persona] ?? PERSONAS["gaya-core"];

  return (
    <div className="fixed top-6 right-6 z-40 flex items-center gap-2 px-3 py-1.5 border border-os-border bg-os-surface/90 backdrop-blur-md shadow-[0_0_15px_rgba(212,175,55,0.15)] font-mono text-[10px] uppercase tracking-[0.16em]">
      <span className="w-1.5 h-1.5 rounded-full bg-os-accent shadow-[0_0_6px_var(--accent)]" />
      <span className="text-os-accent font-bold">{p.displayName}</span>
      <span className="text-os-dim">·</span>
      <span className="text-os-muted">{p.tagline}</span>
    </div>
  );
}
