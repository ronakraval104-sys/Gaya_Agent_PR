"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { useGaya } from "@/lib/store";

interface FullRecord {
  id: string;
  slug: string;
  type: string;
  title: string;
  description: string;
  body: string;
  persona: string;
  priority: string;
  tags: string[];
  links: string[];
  source: {
    path: string;
    origin: string;
    lastModified?: number;
    ingestedAt: number;
  };
}

const PRIORITY_BADGE: Record<string, { icon: string; label: string; color: string }> = {
  boulder: { icon: "■", label: "BOULDER", color: "var(--err)" },
  high:    { icon: "■", label: "HIGH",    color: "var(--warn)" },
  normal:  { icon: "·", label: "NORMAL",  color: "var(--text-2)" }
};

const ORIGIN_LABEL: Record<string, string> = {
  "memory-dir": "auto-memory",
  "omni-gaya": "omni-gaya charter",
  obsidian: "obsidian vault",
  manual: "slash console",
  "index-line": "memory index"
};

export function RecordDetail() {
  const slug = useGaya((s) => s.openRecordSlug);
  const closeRecord = useGaya((s) => s.closeRecord);
  const openRecord = useGaya((s) => s.openRecord);
  const [record, setRecord] = useState<FullRecord | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // URL bootstrap: /?record=<slug> auto-opens on load (deep-link + screenshot support)
  const bootstrappedRef = useRef(false);
  useEffect(() => {
    if (bootstrappedRef.current) return;
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const recordParam = params.get("record");
    if (recordParam && useGaya.getState().openRecordSlug !== recordParam) {
      useGaya.getState().openRecord(recordParam);
    }
    bootstrappedRef.current = true;
  }, []);

  // ESC to close
  useEffect(() => {
    if (!slug) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeRecord();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [slug, closeRecord]);

  useEffect(() => {
    if (!slug) {
      setRecord(null);
      setError(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    (async () => {
      try {
        const res = await fetch(`/api/knowledge/${encodeURIComponent(slug)}`);
        if (!res.ok) {
          if (!cancelled) setError(`Record not found: ${slug}`);
          return;
        }
        const data = await res.json();
        if (!cancelled) setRecord(data.record ?? null);
      } catch (err) {
        if (!cancelled) setError((err as Error).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [slug]);

  const badge = record ? PRIORITY_BADGE[record.priority] ?? PRIORITY_BADGE.normal : null;
  const originLabel = record ? ORIGIN_LABEL[record.source.origin] ?? record.source.origin : "";

  const stamp = (ms?: number) =>
    ms ? new Date(ms).toLocaleString("en-IN", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "—";

  return (
    <AnimatePresence>
      {slug && (
        <motion.div
          key="record-overlay"
          initial={false}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.18 }}
          className="fixed inset-0 z-[60] flex items-center justify-center p-8"
          style={{ background: "rgba(5, 7, 11, 0.72)", backdropFilter: "blur(4px)" }}
          onClick={closeRecord}
        >
          <motion.div
            initial={false}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 16 }}
            transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
            className="flex flex-col"
            style={{
              width: "min(880px, 96vw)",
              maxHeight: "88vh",
              background: "var(--bg)",
              border: "1px solid var(--border)",
              borderLeft: badge ? `2px solid ${badge.color}` : "2px solid var(--border-strong)"
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* header */}
            <div
              className="flex items-start justify-between px-6 py-4 border-b"
              style={{ borderColor: "var(--border)" }}
            >
              <div style={{ minWidth: 0, flex: 1 }}>
                <div className="flex items-center gap-2 mb-1">
                  {badge && (
                    <span
                      className="px-2 py-0.5 rounded"
                      style={{
                        fontFamily: "JetBrains Mono, monospace",
                        fontSize: 10,
                        letterSpacing: "0.12em",
                        color: badge.color,
                        border: `1px solid ${badge.color}`,
                        background: "rgba(0,0,0,0.3)"
                      }}
                    >
                      {badge.icon} {badge.label}
                    </span>
                  )}
                  {record && (
                    <span
                      className="hud-label"
                      style={{ color: "var(--text-2)", opacity: 0.7 }}
                    >
                      {record.type.toUpperCase()} · {record.persona.replace("-", " ").toUpperCase()}
                    </span>
                  )}
                </div>
                <div
                  style={{
                    fontFamily: "General Sans, system-ui, sans-serif",
                    fontWeight: 600,
                    fontSize: 22,
                    color: "#fff",
                    letterSpacing: "0.01em",
                    wordBreak: "break-word"
                  }}
                >
                  {record?.title ?? (loading ? "Loading…" : error ? "Not found" : slug)}
                </div>
                {record?.description && (
                  <div
                    className="mt-2"
                    style={{
                      fontFamily: "Inter, sans-serif",
                      fontSize: 13,
                      color: "rgba(255,255,255,0.7)",
                      lineHeight: 1.5
                    }}
                  >
                    {record.description}
                  </div>
                )}
              </div>
              <button
                onClick={closeRecord}
                aria-label="Close"
                className="ml-4 px-2 py-1 rounded hover:bg-white/10 transition"
                style={{
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: 11,
                  color: "var(--text-2)",
                  border: "1px solid var(--border)"
                }}
              >
                ESC
              </button>
            </div>

            {/* body */}
            <div className="px-6 py-4 overflow-y-auto" style={{ flex: 1 }}>
              {loading && <div className="hud-label opacity-60">… reading record</div>}
              {error && (
                <div style={{ color: "var(--stark-orange)", fontFamily: "JetBrains Mono, monospace" }}>
                  {error}
                </div>
              )}
              {record && (
                <>
                  <MarkdownBody
                    body={record.body}
                    onLinkClick={(target) => openRecord(target)}
                  />

                  {record.links.length > 0 && (
                    <div className="mt-6 pt-4 border-t" style={{ borderColor: "var(--border)" }}>
                      <div className="hud-label mb-2" style={{ color: "var(--text-2)" }}>
                        LINKED RECORDS
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {record.links.map((linkSlug) => (
                          <button
                            key={linkSlug}
                            onClick={() => openRecord(linkSlug)}
                            className="px-3 py-1.5 rounded transition hover:brightness-125"
                            style={{
                              fontFamily: "JetBrains Mono, monospace",
                              fontSize: 11,
                              letterSpacing: "0.05em",
                              color: "var(--text-2)",
                              background: "rgba(79, 227, 255, 0.08)",
                              border: "1px solid var(--border)"
                            }}
                          >
                            {linkSlug}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* footer meta */}
            {record && (
              <div
                className="px-6 py-3 border-t flex items-center justify-between flex-wrap gap-2"
                style={{ borderColor: "var(--border)" }}
              >
                <div className="flex items-center gap-3">
                  <span className="hud-label opacity-60">SLUG</span>
                  <code
                    style={{
                      fontFamily: "JetBrains Mono, monospace",
                      fontSize: 11,
                      color: "var(--text-3)",
                      wordBreak: "break-all"
                    }}
                  >
                    {record.slug}
                  </code>
                </div>
                <div className="flex items-center gap-3 hud-label opacity-60">
                  <span>SOURCE :: {originLabel}</span>
                  <span>·</span>
                  <span>MOD {stamp(record.source.lastModified)}</span>
                </div>
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/**
 * Very light markdown renderer — enough to make body readable.
 * Supports: paragraphs, bold **x**, headings ## and ###, - bulleted lists,
 * inline `code`, and [[wiki-links]] which become clickable jumps to other records.
 */
function MarkdownBody({
  body,
  onLinkClick
}: {
  body: string;
  onLinkClick: (slug: string) => void;
}) {
  const lines = body.split(/\r?\n/);
  const blocks: React.ReactNode[] = [];
  let listBuf: string[] = [];

  const flushList = (key: string) => {
    if (listBuf.length === 0) return;
    blocks.push(
      <ul
        key={key}
        style={{
          margin: "0 0 12px 20px",
          padding: 0,
          fontFamily: "Inter, sans-serif",
          fontSize: 13,
          color: "rgba(255,255,255,0.85)",
          lineHeight: 1.55
        }}
      >
        {listBuf.map((item, i) => (
          <li key={i} style={{ marginBottom: 4 }}>
            {renderInline(item, onLinkClick)}
          </li>
        ))}
      </ul>
    );
    listBuf = [];
  };

  lines.forEach((raw, i) => {
    const line = raw;
    const trimmed = line.trim();

    // list item
    const listMatch = trimmed.match(/^[-*]\s+(.+)$/);
    if (listMatch) {
      listBuf.push(listMatch[1]);
      return;
    }
    flushList(`list-${i}`);

    if (!trimmed) {
      blocks.push(<div key={`sp-${i}`} style={{ height: 8 }} />);
      return;
    }

    const h3 = trimmed.match(/^###\s+(.+)$/);
    if (h3) {
      blocks.push(
        <h3
          key={i}
          style={{
            fontFamily: "General Sans, system-ui, sans-serif",
            fontWeight: 600,
            fontSize: 14,
            color: "var(--text-2)",
            letterSpacing: "0.03em",
            margin: "16px 0 6px 0"
          }}
        >
          {renderInline(h3[1], onLinkClick)}
        </h3>
      );
      return;
    }
    const h2 = trimmed.match(/^##\s+(.+)$/);
    if (h2) {
      blocks.push(
        <h2
          key={i}
          style={{
            fontFamily: "General Sans, system-ui, sans-serif",
            fontWeight: 600,
            fontSize: 16,
            color: "#fff",
            letterSpacing: "0.02em",
            margin: "20px 0 8px 0"
          }}
        >
          {renderInline(h2[1], onLinkClick)}
        </h2>
      );
      return;
    }

    blocks.push(
      <p
        key={i}
        style={{
          fontFamily: "Inter, sans-serif",
          fontSize: 13,
          color: "rgba(255,255,255,0.88)",
          lineHeight: 1.55,
          margin: "0 0 10px 0"
        }}
      >
        {renderInline(trimmed, onLinkClick)}
      </p>
    );
  });
  flushList("list-end");

  return <>{blocks}</>;
}

function renderInline(
  text: string,
  onLinkClick: (slug: string) => void
): React.ReactNode[] {
  // Tokenize: [[wiki|display]] | **bold** | `code` | rest
  const parts: React.ReactNode[] = [];
  const re = /(\[\[[^\]]+\]\])|(\*\*[^*]+\*\*)|(`[^`]+`)/g;
  let last = 0;
  let match: RegExpExecArray | null;
  let key = 0;
  while ((match = re.exec(text)) !== null) {
    if (match.index > last) {
      parts.push(text.slice(last, match.index));
    }
    const token = match[0];
    if (token.startsWith("[[")) {
      const inner = token.slice(2, -2);
      const [target, display] = inner.split("|").map((s) => s.trim());
      const slug = target.toLowerCase().replace(/_/g, "-");
      parts.push(
        <button
          key={`ln-${key++}`}
          onClick={() => onLinkClick(slug)}
          style={{
            color: "var(--text-2)",
            background: "none",
            border: "none",
            borderBottom: "1px dashed var(--border)",
            cursor: "pointer",
            font: "inherit",
            padding: 0
          }}
        >
          {display || target}
        </button>
      );
    } else if (token.startsWith("**")) {
      parts.push(
        <strong key={`b-${key++}`} style={{ color: "#fff", fontWeight: 600 }}>
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith("`")) {
      parts.push(
        <code
          key={`c-${key++}`}
          style={{
            fontFamily: "JetBrains Mono, monospace",
            fontSize: 12,
            padding: "1px 5px",
            background: "rgba(79, 227, 255, 0.08)",
            border: "1px solid var(--border)",
            borderRadius: 3,
            color: "var(--text-3)"
          }}
        >
          {token.slice(1, -1)}
        </code>
      );
    }
    last = re.lastIndex;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}
