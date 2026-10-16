"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { useGaya } from "@/lib/store";

const SLASH_COMMANDS = [
  { cmd: "/search",    help: "Search knowledge base: /search <query>" },
  { cmd: "/decision",  help: "Log a decision to Decision Records" },
  { cmd: "/win",       help: "Log a win to the Brag Doc" },
  { cmd: "/dump",      help: "Brain-dump into memory, unstructured" },
  { cmd: "/gotcha",    help: "Log a gotcha (lesson learned)" },
  { cmd: "/thread",    help: "Log an open thread / follow-up" },
  { cmd: "/fire",      help: "Fire a skill: /fire <skill-slug>" },
  { cmd: "/persona",   help: "Switch persona: /persona vr | kv" },
  { cmd: "/status",    help: "Show system counts + active tasks" }
];

interface LogLine {
  kind: "in" | "out" | "hits";
  text: string;
  hits?: Array<{ slug: string; type: string; priority: string; description: string }>;
}

export function SlashConsole() {
  const open = useGaya((s) => s.consoleOpen);
  const toggle = useGaya((s) => s.toggleConsole);
  const persona = useGaya((s) => s.persona);
  const setPersona = useGaya((s) => s.setPersona);
  const swapPersona = useGaya((s) => s.swapPersona);
  const fireSkill = useGaya((s) => s.fireSkill);
  const openRecord = useGaya((s) => s.openRecord);
  const [input, setInput] = useState("");
  const [log, setLog] = useState<LogLine[]>([
    { kind: "out", text: "At your command, R0n. Council of Gaya standing by. Try /search, /decision, or /help." }
  ]);
  const [busy, setBusy] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [log]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        toggle();
      }
      if (e.key === "Escape" && open) toggle();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, toggle]);

  const say = (text: string) => setLog((l) => [...l, { kind: "out", text }]);

  const submit = async () => {
    const line = input.trim();
    if (!line || busy) return;
    setLog((l) => [...l, { kind: "in", text: line }]);
    setInput("");
    setBusy(true);
    try {
      await handleCommand(line);
    } catch (err) {
      say(`Error: ${(err as Error).message}`);
    } finally {
      setBusy(false);
    }
  };

  const postLog = async (kind: string, text: string) => {
    const res = await fetch("/api/log", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ kind, text, personaId: persona })
    });
    return res.json();
  };

  const handleCommand = async (line: string): Promise<void> => {
    const [cmd, ...rest] = line.split(/\s+/);
    const arg = rest.join(" ").trim();

    switch (cmd) {
      case "/help":
        say(SLASH_COMMANDS.map((s) => `${s.cmd.padEnd(11)} ${s.help}`).join("\n"));
        return;

      case "/status": {
        const res = await fetch("/api/knowledge/counts").then((r) => r.json());
        say(`SYS :: NOMINAL\n${res.total} records · ${res.boulderCount} boulder rules · sync ${new Date(res.lastIngestAt).toLocaleString("en-IN")}`);
        return;
      }

      case "/search": {
        if (!arg) return say("Format: /search <query>");
        const res = await fetch(`/api/knowledge?q=${encodeURIComponent(arg)}`).then((r) => r.json());
        if (!res.ok || res.count === 0) return say(`No matches for "${arg}".`);
        const top = res.records.slice(0, 8);
        setLog((l) => [
          ...l,
          {
            kind: "out",
            text: `Found ${res.count} match(es) for "${arg}"${res.count > 8 ? " (showing top 8, click to open):" : " (click to open):"}`
          },
          { kind: "hits", text: "", hits: top }
        ]);
        return;
      }

      case "/decision":
      case "/win":
      case "/dump":
      case "/gotcha":
      case "/thread": {
        if (!arg) return say(`Format: ${cmd} <text>`);
        const kind = cmd.slice(1); // drop leading /
        const res = await postLog(kind, arg);
        if (res.ok) {
          say(`✓ ${kind} recorded as ${res.slug} — "${res.record.title}"`);
        } else {
          say(`✗ Failed: ${res.error ?? "unknown error"}`);
        }
        return;
      }

      case "/fire": {
        if (!arg) return say("Format: /fire <skill-slug>");
        fireSkill(arg, "bob");
        say(`Bob executing ${arg}. Watch the reactor.`);
        return;
      }

      case "/persona": {
        swapPersona("gaya-core");
        return say("Context: Gaya Bodhi Core. Sacred Gold & Obsidian active.");
      }

      default:
        return say(`Unknown command. Try /help.`);
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          key="console-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.18 }}
          className="fixed inset-0 z-50 flex items-start justify-center pt-24"
          style={{ background: "rgba(5, 7, 11, 0.55)", backdropFilter: "blur(2px)" }}
          onClick={toggle}
        >
          <motion.div
            initial={{ y: -18, opacity: 0, scale: 0.98 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: -18, opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
            className="flex flex-col"
            style={{
              width: "min(760px, 92vw)",
              maxHeight: "70vh",
              background: "var(--bg)",
              border: "1px solid var(--border-strong)"
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-4 py-2 border-b" style={{ borderColor: "var(--border)" }}>
              <div className="hud-label" style={{ color: "var(--text)" }}>
                GAYA // CONSOLE
              </div>
              <div className="hud-label opacity-60">ESC to close</div>
            </div>

            <div ref={scrollRef} className="px-4 py-3 overflow-y-auto" style={{ maxHeight: "48vh" }}>
              {log.map((l, i) => {
                if (l.kind === "hits" && l.hits) {
                  return (
                    <div key={i} className="mb-3 pl-6">
                      {l.hits.map((h) => {
                        const badge = h.priority === "boulder" ? "🚨" : h.priority === "high" ? "⚠" : "·";
                        const badgeColor =
                          h.priority === "boulder" ? "var(--warn)"
                          : h.priority === "high" ? "var(--warn)"
                          : "var(--text)";
                        return (
                          <button
                            key={h.slug}
                            onClick={() => { openRecord(h.slug); toggle(); }}
                            className="block w-full text-left px-2 py-1.5 rounded hover:bg-white/[0.06] transition"
                          >
                            <div className="flex items-center gap-2">
                              <span style={{ color: badgeColor, fontSize: 12 }}>{badge}</span>
                              <span
                                style={{
                                  fontFamily: "JetBrains Mono, monospace",
                                  fontSize: 10,
                                  letterSpacing: "0.1em",
                                  color: "var(--text)",
                                  opacity: 0.7,
                                  textTransform: "uppercase"
                                }}
                              >
                                {h.type}
                              </span>
                              <span
                                style={{
                                  fontFamily: "Inter, sans-serif",
                                  fontSize: 12,
                                  color: "rgba(255,255,255,0.9)"
                                }}
                              >
                                {h.slug}
                              </span>
                            </div>
                            <div
                              style={{
                                fontFamily: "Inter, sans-serif",
                                fontSize: 11,
                                color: "rgba(255,255,255,0.55)",
                                paddingLeft: 20,
                                marginTop: 2
                              }}
                            >
                              {h.description.slice(0, 110)}
                              {h.description.length > 110 ? "…" : ""}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  );
                }
                return (
                  <div key={i} className="mb-2">
                    <span
                      className="mr-2"
                      style={{
                        fontFamily: "JetBrains Mono, monospace",
                        fontSize: 11,
                        color: l.kind === "in" ? "var(--warn)" : "var(--text)",
                        opacity: 0.85
                      }}
                    >
                      {l.kind === "in" ? ">" : "J"}
                    </span>
                    <span
                      style={{
                        fontFamily: l.kind === "in" ? "JetBrains Mono" : "Inter",
                        fontSize: 13,
                        whiteSpace: "pre-wrap",
                        color: "rgba(255,255,255,0.9)"
                      }}
                    >
                      {l.text}
                    </span>
                  </div>
                );
              })}
              {busy && (
                <div className="mb-2 opacity-60" style={{ fontFamily: "JetBrains Mono", fontSize: 11 }}>
                  … working
                </div>
              )}
            </div>

            <div className="px-4 py-3 border-t flex items-center gap-2" style={{ borderColor: "var(--border)" }}>
              <span
                style={{
                  fontFamily: "JetBrains Mono, monospace",
                  color: "var(--warn)",
                  fontSize: 14
                }}
              >
                &gt;
              </span>
              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") submit();
                }}
                placeholder="/search, /decision, /win, /dump, /gotcha, /thread, /fire, /persona, /status  (or /help)"
                className="flex-1 bg-transparent outline-none"
                style={{
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: 13,
                  color: "#fff"
                }}
                disabled={busy}
              />
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
