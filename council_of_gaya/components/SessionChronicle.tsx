"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useGaya } from "@/lib/store";

const KIND_ICON: Record<string, { icon: string; color: string; label: string }> = {
  record:  { icon: "◆", color: "var(--text)",  label: "REC"    },
  seat:    { icon: "■", color: "var(--text)",  label: "SEAT"   },
  persona: { icon: "◼", color: "var(--warn)",  label: "MORPH"  },
  skill:   { icon: "▲", color: "var(--warn)",  label: "FIRE"   },
  console: { icon: "»", color: "var(--text-2)", label: "LOG"   },
  "session-start": { icon: "•", color: "var(--ok)", label: "BOOT" }
};

function relTime(then: number): string {
  const diff = Date.now() - then;
  if (diff < 5_000) return "now";
  if (diff < 60_000) return `${Math.round(diff / 1000)}s`;
  if (diff < 3600_000) return `${Math.round(diff / 60_000)}m`;
  if (diff < 86_400_000) return `${Math.round(diff / 3_600_000)}h`;
  return `${Math.round(diff / 86_400_000)}d`;
}

export function SessionChronicle() {
  const chronicle = useGaya((s) => s.chronicle);
  const openRecord = useGaya((s) => s.openRecord);
  const togglePinnedSeat = useGaya((s) => s.togglePinnedSeat);
  const clearChronicle = useGaya((s) => s.clearChronicle);
  const chronicleVisible = useGaya((s) => s.chronicleVisible);
  const hideChronicle = useGaya((s) => s.hideChronicle);
  const [expanded, setExpanded] = useState(false);

  // Guard against hydration mismatch: store reads localStorage at import time
  // on the client but is empty on the server. Only render live data after mount.
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  const activeChronicle = mounted ? chronicle : [];

  // Newest first
  const visible = [...activeChronicle].reverse().slice(0, expanded ? 20 : 6);
  const total = activeChronicle.length;

  // Hidden state — panel closed; sidebar Chronicle row reopens it
  if (mounted && !chronicleVisible) return null;

  const handleClick = (e: (typeof visible)[number]) => {
    if (e.kind === "record" && e.targetSlug) openRecord(e.targetSlug);
    else if (e.kind === "seat" && e.targetSeat) togglePinnedSeat(e.targetSeat);
  };

  return (
    <aside
      className="fixed z-30 flex flex-col"
      style={{
        left: 236,           // clear the 220px sidebar + 16px gap
        bottom: 40,          // clear the 32px status bar + 8px gap
        width: 300,
        maxHeight: expanded ? "60vh" : 320,
        background: "var(--bg)",
        border: "1px solid var(--border)"
      }}
    >
      {/* header */}
      <div
        className="flex items-center justify-between px-3 py-2 border-b"
        style={{ borderColor: "var(--border)" }}
      >
        <div className="page-eyebrow">Session Chronicle</div>
        <div className="flex items-center gap-1">
          <span
            className="hud-label opacity-60"
            style={{ fontSize: 10 }}
            title="Total entries stored (capped at 40)"
          >
            {total}
          </span>
          <button
            onClick={() => setExpanded((v) => !v)}
            className="px-1.5 py-0.5 hover:bg-os-surface2 transition"
            style={{
              fontFamily: "JetBrains Mono, monospace",
              fontSize: 10,
              color: "var(--text-2)",
              border: "1px solid var(--border)"
            }}
            title={expanded ? "Collapse" : "Expand"}
          >
            {expanded ? "−" : "+"}
          </button>
          {expanded && total > 0 && (
            <button
              onClick={clearChronicle}
              className="px-1.5 py-0.5 hover:bg-os-surface2 transition"
              style={{
                fontFamily: "JetBrains Mono, monospace",
                fontSize: 10,
                color: "var(--err)",
                border: "1px solid var(--border)"
              }}
              title="Clear chronicle"
            >
              ⌫
            </button>
          )}
          <button
            onClick={hideChronicle}
            className="px-1.5 py-0.5 hover:bg-os-surface2 transition"
            style={{
              fontFamily: "JetBrains Mono, monospace",
              fontSize: 10,
              color: "var(--text-2)",
              border: "1px solid var(--border)"
            }}
            title="Close chronicle · reopen from sidebar › Chronicle"
          >
            ×
          </button>
        </div>
      </div>

      {/* list */}
      <div className="px-1 py-1 overflow-y-auto flex-1">
        {visible.length === 0 && (
          <div
            className="hud-label px-2 py-3 opacity-50"
            style={{ fontStyle: "italic" }}
          >
            Nothing yet. Open a record, pin a seat, fire a skill…
          </div>
        )}
        <AnimatePresence initial={false}>
          {visible.map((e, i) => {
            const spec = KIND_ICON[e.kind] ?? KIND_ICON.console;
            const clickable = (e.kind === "record" && e.targetSlug) || (e.kind === "seat" && e.targetSeat);
            const El = clickable ? "button" : "div";
            return (
              <motion.div
                key={e.id}
                initial={i === 0 ? { opacity: 0, x: -12 } : false}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2 }}
              >
                <El
                  onClick={clickable ? () => handleClick(e) : undefined}
                  className={`w-full text-left px-2 py-1.5 ${clickable ? "hover:bg-os-surface2 cursor-pointer" : ""} transition block`}
                  style={{
                    fontFamily: "JetBrains Mono, monospace",
                    fontSize: 11,
                    display: "flex",
                    alignItems: "flex-start",
                    gap: 8
                  }}
                >
                  <span
                    style={{
                      color: spec.color,
                      fontSize: 12,
                      lineHeight: 1,
                      marginTop: 2,
                      minWidth: 12,
                      textAlign: "center"
                    }}
                  >
                    {spec.icon}
                  </span>
                  <span style={{ flex: 1, minWidth: 0 }}>
                    <span
                      style={{
                        fontSize: 9,
                        letterSpacing: "0.1em",
                        color: spec.color,
                        opacity: 0.75,
                        marginRight: 6
                      }}
                    >
                      {spec.label}
                    </span>
                    <span
                      style={{
                        color: "rgba(255,255,255,0.85)",
                        wordBreak: "break-word"
                      }}
                    >
                      {e.label}
                    </span>
                  </span>
                  <span
                    style={{
                      fontSize: 10,
                      color: "rgba(255,255,255,0.4)",
                      whiteSpace: "nowrap"
                    }}
                  >
                    {relTime(e.at)}
                  </span>
                </El>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </aside>
  );
}
