"use client";

import { useEffect, useState } from "react";
import { useGaya } from "@/lib/store";
import { Label, Dot, Badge } from "./terminal";

interface ThreadRow {
  slug: string;
  title: string;
  description: string;
  type: string;
  persona: string;
  priority: string;
  tags: string[];
  source?: {
    lastModified?: number;
    ingestedAt: number;
    origin: string;
  };
}

interface FullPayload {
  ok: boolean;
  nodes: ThreadRow[];
}

/**
 * ThreadsBoard — the daily-driver "what's on my plate" surface.
 *
 * Reads threads + gotchas from /api/knowledge/full (already cached at
 * the shell layer via revalidate but we hit it fresh here so a re-ingest
 * or a slash-log write shows up within one refresh).
 *
 * Persona scope: rows for the active persona OR shared. Off-persona
 * threads are hidden entirely (unlike the graph which dims them —
 * threads are actionable so no clutter).
 *
 * Sort: priority (boulder → high → normal) then most-recently-modified.
 * Click a row → openRecord(slug).
 */
export function ThreadsBoard() {
  const persona = useGaya((s) => s.persona);
  const openRecord = useGaya((s) => s.openRecord);
  const [rows, setRows] = useState<ThreadRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (!mounted) return;
    let cancelled = false;
    const load = async () => {
      try {
        const res = (await fetch("/api/knowledge/full").then((r) => r.json())) as FullPayload;
        if (cancelled || !res.ok) return;
        const filtered = res.nodes.filter(
          (r) => r.type === "thread" || r.type === "gotcha"
        );
        setRows(filtered);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    const id = setInterval(load, 20_000);
    return () => { cancelled = true; clearInterval(id); };
  }, [mounted]);

  // Gaya OS scope + priority sort
  const priorityRank = (p: string) => (p === "boulder" ? 0 : p === "high" ? 1 : 2);
  const scoped = [...rows].sort((a, b) => {
    const pr = priorityRank(a.priority) - priorityRank(b.priority);
    if (pr !== 0) return pr;
    const am = a.source?.lastModified ?? a.source?.ingestedAt ?? 0;
    const bm = b.source?.lastModified ?? b.source?.ingestedAt ?? 0;
    return bm - am;
  });

  const threads = scoped.filter((r) => r.type === "thread");
  const gotchas = scoped.filter((r) => r.type === "gotcha");

  const empireName = "Gaya OS";

  if (!mounted || loading) {
    return (
      <div className="px-6 max-w-[1600px] mx-auto mt-6">
        <div className="mb-2"><Label rule>Threads Board</Label></div>
        <div className="border border-os-border bg-os-surface p-4 font-mono text-[11px] text-os-dim">
          … loading threads
        </div>
      </div>
    );
  }

  return (
    <div className="px-6 max-w-[1600px] mx-auto mt-6 pb-24">
      <div className="mb-2">
        <div className="flex items-baseline justify-between gap-3">
          <div className="min-w-0 flex-1">
            <Label count={`${threads.length} · ${gotchas.length}`} rule>
              Threads Board · {empireName}
            </Label>
          </div>
          <div className="font-mono text-[10px] uppercase tracking-[0.16em] text-os-dim shrink-0">
            {threads.length} open · {gotchas.length} gotchas
          </div>
        </div>
      </div>

      <div className="border border-os-border bg-os-surface">
        {/* header row */}
        <div
          className="grid grid-cols-[24px_1fr_120px_100px_80px] gap-3 px-3 py-2 border-b border-os-border font-mono text-[9px] font-bold uppercase tracking-[0.2em] text-os-dim"
        >
          <span></span>
          <span>Title / Context</span>
          <span>Type · Persona</span>
          <span>Age</span>
          <span className="text-right">Priority</span>
        </div>

        {/* rows */}
        {scoped.length === 0 && (
          <div className="px-4 py-6 font-mono text-[11px] text-os-dim">
            No open threads for {empireName}. Empty desk.
          </div>
        )}
        {scoped.slice(0, 20).map((r) => (
          <ThreadRow key={r.slug} r={r} onOpen={() => openRecord(r.slug)} />
        ))}
        {scoped.length > 20 && (
          <div className="px-3 py-2 font-mono text-[10px] uppercase tracking-[0.16em] text-os-dim border-t border-os-border">
            + {scoped.length - 20} more · use /search or a seat filter
          </div>
        )}
      </div>
    </div>
  );
}

function ThreadRow({ r, onOpen }: { r: ThreadRow; onOpen: () => void }) {
  const dotState = r.priority === "boulder" ? "err" : r.priority === "high" ? "warn" : "off";
  const priorityText = r.priority.toUpperCase();
  const age = ageOf(r.source?.lastModified ?? r.source?.ingestedAt);

  return (
    <button
      type="button"
      onClick={onOpen}
      className="w-full grid grid-cols-[24px_1fr_120px_100px_80px] gap-3 items-center px-3 py-2 border-b border-os-hairline hover:bg-os-surface2 transition-colors text-left"
    >
      <div className="flex items-center justify-center">
        <Dot state={dotState} />
      </div>
      <div className="min-w-0">
        <div className="font-mono text-[12px] text-os-text truncate">{r.title ?? r.slug}</div>
        <div className="font-mono text-[10px] text-os-dim truncate">
          {(r.description ?? "").slice(0, 120)}
          {(r.description ?? "").length > 120 ? "…" : ""}
        </div>
      </div>
      <div className="font-mono text-[10px] uppercase tracking-[0.14em] text-os-muted">
        {r.type} · {r.persona.replace("-", " ")}
      </div>
      <div className="font-mono text-[10px] text-os-dim">{age}</div>
      <div className="flex justify-end">
        <span
          className="font-mono text-[9px] uppercase tracking-[0.16em]"
          style={{
            color:
              r.priority === "boulder" ? "var(--err)"
              : r.priority === "high" ? "var(--warn)"
              : "var(--text-3)"
          }}
        >
          {priorityText}
        </span>
      </div>
    </button>
  );
}

function ageOf(ms?: number): string {
  if (!ms) return "—";
  const d = Date.now() - ms;
  if (d < 60_000) return "now";
  if (d < 3600_000) return `${Math.round(d / 60_000)}m ago`;
  if (d < 86_400_000) return `${Math.round(d / 3600_000)}h ago`;
  if (d < 604_800_000) return `${Math.round(d / 86_400_000)}d ago`;
  return `${Math.round(d / 604_800_000)}w ago`;
}
