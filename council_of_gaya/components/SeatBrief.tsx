"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { COUNCIL, type CouncilSeatId } from "@/lib/council";
import { useGaya } from "@/lib/store";

interface KnowledgeSummary {
  slug: string;
  title: string;
  description: string;
  type: string;
  persona: string;
  priority: string;
  tags: string[];
}

interface CountsPayload {
  total: number;
  byType: Record<string, number>;
  byPriority: Record<string, number>;
}

export function SeatBrief() {
  const pinnedSeat = useGaya((s) => s.pinnedSeat) as CouncilSeatId | null;
  const clear = useGaya((s) => s.clearPinnedSeat);
  const togglePinnedSeat = useGaya((s) => s.togglePinnedSeat);
  const openRecord = useGaya((s) => s.openRecord);

  // Bootstrap from URL ?seat=<id> so screenshots + deep-links work.
  // StrictMode double-fires useEffect — use useRef to guard against a re-toggle.
  const bootstrappedRef = useRef(false);
  useEffect(() => {
    if (bootstrappedRef.current) return;
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const seatParam = params.get("seat");
    if (seatParam && useGaya.getState().pinnedSeat !== seatParam) {
      useGaya.getState().togglePinnedSeat(seatParam);
    }
    bootstrappedRef.current = true;
  }, []);
  const [records, setRecords] = useState<KnowledgeSummary[]>([]);
  const [totalCounts, setTotalCounts] = useState<CountsPayload | null>(null);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [priorityFilter, setPriorityFilter] = useState<"all" | "boulder" | "high" | "normal">("all");

  // Reset filters whenever the pinned seat changes
  useEffect(() => {
    setQuery("");
    setPriorityFilter("all");
  }, [pinnedSeat]);

  useEffect(() => {
    if (!pinnedSeat) return;
    let cancelled = false;
    setLoading(true);
    (async () => {
      try {
        const [listRes, allRes] = await Promise.all([
          fetch(`/api/knowledge?seat=${pinnedSeat}`).then((r) => r.json()),
          fetch(`/api/knowledge/counts`).then((r) => r.json())
        ]);
        if (cancelled) return;
        setRecords(listRes.records ?? []);
        setTotalCounts(allRes ?? null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [pinnedSeat]);

  const seat = pinnedSeat ? COUNCIL.find((c) => c.id === pinnedSeat) : null;

  const filtered = records.filter((r) => {
    if (priorityFilter !== "all" && r.priority !== priorityFilter) return false;
    if (query.trim()) {
      const q = query.toLowerCase();
      const hay = `${r.slug} ${r.title} ${r.description} ${r.tags.join(" ")}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });

  const priorityCounts = {
    boulder: records.filter((r) => r.priority === "boulder").length,
    high: records.filter((r) => r.priority === "high").length,
    normal: records.filter((r) => r.priority === "normal").length
  };

  const priorityBadge = (p: string) =>
    p === "boulder" ? { icon: "■", color: "var(--err)" }
    : p === "high" ? { icon: "■", color: "var(--warn)" }
    : { icon: "·", color: "var(--text-2)" };

  return (
    <AnimatePresence>
      {pinnedSeat && seat && (
        <motion.aside
          key={pinnedSeat}
          initial={false}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 40, opacity: 0 }}
          transition={{ duration: 0.26, ease: [0.22, 1, 0.36, 1] }}
          className="fixed top-14 right-4 z-30 flex flex-col"
          style={{
            width: 360,
            maxHeight: "calc(100vh - 100px)",
            background: "var(--bg)",
            border: "1px solid var(--border)",
            borderLeft: "2px solid var(--accent)"
          }}
        >
          {/* header */}
          <div
            className="flex items-center justify-between px-4 py-3 border-b"
            style={{ borderColor: "var(--border)" }}
          >
            <div>
              <div className="hud-label" style={{ color: "var(--text-3)" }}>
                SEAT BRIEF
              </div>
              <div
                className="mt-1"
                style={{
                  fontFamily: "General Sans, system-ui, sans-serif",
                  fontWeight: 600,
                  fontSize: 18,
                  letterSpacing: "0.04em",
                  color: "#fff"
                }}
              >
                {seat.codename}
              </div>
              <div
                style={{
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: 10,
                  letterSpacing: "0.12em",
                  color: "var(--persona-metal)",
                  opacity: 0.7
                }}
              >
                {seat.role}
              </div>
            </div>
            <button
              onClick={clear}
              className="text-xs px-2 py-1 rounded hover:bg-white/10 transition"
              style={{
                fontFamily: "JetBrains Mono, monospace",
                color: "var(--text-3)",
                border: "1px solid var(--border)"
              }}
              aria-label="Unpin seat"
            >
              CLOSE
            </button>
          </div>

          {/* summary counts */}
          <div className="px-4 py-3 border-b" style={{ borderColor: "var(--border)" }}>
            <div
              className="flex items-baseline gap-3"
              style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 11 }}
            >
              <span style={{ color: "var(--stark-orange)", fontSize: 22, fontWeight: 600 }}>
                {filtered.length}
              </span>
              <span className="hud-label">
                {filtered.length === records.length ? "records owned" : `of ${records.length} shown`}
              </span>
              {totalCounts && (
                <span className="hud-label opacity-50 ml-auto">
                  {Math.round((records.length / totalCounts.total) * 100)}% of {totalCounts.total}
                </span>
              )}
            </div>
          </div>

          {/* filters: search + priority chips */}
          <div
            className="px-3 py-2 border-b flex flex-col gap-2"
            style={{ borderColor: "var(--border)" }}
          >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Filter within this seat…"
              className="w-full bg-transparent outline-none px-2 py-1.5 rounded"
              style={{
                fontFamily: "JetBrains Mono, monospace",
                fontSize: 12,
                color: "#fff",
                border: "1px solid var(--border)",
                background: "rgba(0,0,0,0.35)"
              }}
            />
            <div className="flex items-center gap-1.5">
              {([
                { id: "all", label: "ALL", count: records.length, color: "var(--text-3)" },
                { id: "boulder", label: "🚨", count: priorityCounts.boulder, color: "var(--stark-orange)" },
                { id: "high", label: "⚠", count: priorityCounts.high, color: "var(--stark-orange-hot)" },
                { id: "normal", label: "·", count: priorityCounts.normal, color: "var(--text-3)" }
              ] as const).map((chip) => {
                const active = priorityFilter === chip.id;
                return (
                  <button
                    key={chip.id}
                    onClick={() => setPriorityFilter(chip.id)}
                    className="px-2 py-1 rounded transition"
                    style={{
                      fontFamily: "JetBrains Mono, monospace",
                      fontSize: 10,
                      letterSpacing: "0.08em",
                      color: active ? "#fff" : chip.color,
                      background: active ? chip.color : "rgba(0,0,0,0.3)",
                      border: `1px solid ${active ? chip.color : "var(--border)"}`,
                      opacity: chip.count === 0 && chip.id !== "all" ? 0.4 : 1
                    }}
                    disabled={chip.count === 0 && chip.id !== "all"}
                  >
                    {chip.label}{" "}
                    <span style={{ opacity: 0.7 }}>{chip.count}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* records list */}
          <div className="px-2 py-2 overflow-y-auto flex-1">
            {loading && (
              <div className="hud-label px-2 opacity-60">… reading knowledge base</div>
            )}
            {!loading && records.length === 0 && (
              <div className="hud-label px-2 opacity-60">
                No records mapped to this seat yet.
              </div>
            )}
            {!loading && records.length > 0 && filtered.length === 0 && (
              <div className="hud-label px-2 opacity-60">
                No matches. Try clearing filters.
              </div>
            )}
            {filtered.slice(0, 12).map((r) => {
              const b = priorityBadge(r.priority);
              return (
                <button
                  key={r.slug}
                  onClick={() => openRecord(r.slug)}
                  className="w-full text-left px-3 py-2 rounded mb-1 hover:bg-white/[0.06] transition cursor-pointer"
                  title={`Open ${r.slug}`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span style={{ color: b.color, fontSize: 12 }}>{b.icon}</span>
                    <span
                      style={{
                        fontFamily: "JetBrains Mono, monospace",
                        fontSize: 10,
                        letterSpacing: "0.1em",
                        color: "var(--text-3)",
                        opacity: 0.7,
                        textTransform: "uppercase"
                      }}
                    >
                      {r.type}
                    </span>
                    <span
                      style={{
                        fontFamily: "Inter, sans-serif",
                        fontSize: 13,
                        color: "#fff",
                        fontWeight: 500
                      }}
                    >
                      {r.title}
                    </span>
                  </div>
                  <div
                    style={{
                      fontFamily: "Inter, sans-serif",
                      fontSize: 11,
                      color: "rgba(255,255,255,0.6)",
                      lineHeight: 1.4,
                      paddingLeft: 20
                    }}
                  >
                    {r.description.slice(0, 140)}
                    {r.description.length > 140 ? "…" : ""}
                  </div>
                </button>
              );
            })}
            {filtered.length > 12 && (
              <div className="hud-label px-3 pt-2 pb-1 opacity-50">
                +{filtered.length - 12} more · refine filters or /search
              </div>
            )}
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
