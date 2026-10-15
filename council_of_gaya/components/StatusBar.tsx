"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useJarvis } from "@/lib/store";
import { PERSONAS } from "@/lib/personas";

export function StatusBar() {
  const persona = useJarvis((s) => s.persona);
  const activeTasks = useJarvis((s) => s.activeTasks);
  const morph = useJarvis((s) => s.morph);
  const [time, setTime] = useState<string>("");
  const [mounted, setMounted] = useState(false);
  const [ecc, setEcc] = useState<{ instinctsCount: number; contextPressure: number; securityStatus: string } | null>(null);

  useEffect(() => {
    setMounted(true);
    const tick = () => {
      const d = new Date();
      const t = d.toTimeString().slice(0, 8);
      setTime(t);
    };
    tick();
    const id = setInterval(tick, 1000);

    const fetchEcc = () => {
      fetch("/api/jarvis-state")
        .then((r) => r.json())
        .then((d) => {
          if (d?.ecc) setEcc(d.ecc);
        })
        .catch(() => {});
    };
    fetchEcc();
    const eccId = setInterval(fetchEcc, 3000);

    return () => {
      clearInterval(id);
      clearInterval(eccId);
    };
  }, []);

  const p = PERSONAS[persona];

  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-30 flex items-center justify-between px-6 py-2"
      style={{
        background: "linear-gradient(to top, var(--void-000), transparent)",
        borderTop: "1px solid var(--hud-line)"
      }}
    >
      <div className="flex items-center gap-6 hud-label">
        <span style={{ color: "var(--arc-teal)" }}>SYS :: NOMINAL</span>
        <span style={{ color: "var(--arc-teal)" }}>SHIELD :: {ecc?.securityStatus || "SECURE"}</span>
        <span style={{ color: "var(--stark-gold, #e6b800)" }}>INSTINCTS :: {ecc ? `${ecc.instinctsCount} XP` : "5 XP"}</span>
        <span
          style={{
            color: (ecc?.contextPressure || 0) > 75 ? "var(--stark-orange)" : undefined,
            transition: "color 0.24s ease"
          }}
        >
          PRESSURE :: {ecc?.contextPressure || 0}%
        </span>
        <span
          style={{
            color: morph ? "var(--stark-orange)" : undefined,
            transition: "color 0.24s ease"
          }}
        >
          CONTEXT :: {p.codename}
        </span>
        <span>TASKS :: {activeTasks.length.toString().padStart(2, "0")}</span>
        <AnimatePresence>
          {morph && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: [0, 1, 1, 0] }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.9, times: [0, 0.25, 0.75, 1] }}
              style={{ color: "var(--stark-orange)" }}
            >
              // MORPH ACTIVE
            </motion.span>
          )}
        </AnimatePresence>
      </div>
      <div className="hud-label" suppressHydrationWarning>{mounted ? `${time} // IST` : ""}</div>
    </div>
  );
}
