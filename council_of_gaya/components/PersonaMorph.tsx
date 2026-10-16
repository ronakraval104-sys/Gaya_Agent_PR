"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useGaya } from "@/lib/store";
import { PERSONAS } from "@/lib/personas";

/**
 * Persona-swap ceremony — Monolith Signal restraint.
 * The MCU chromatic-split spectacle is retired. What's left:
 *   - A thin white scanline sweeping vertically across the viewport
 *   - A brief mono confirmation chip pinned bottom-center
 *   - A whisper of accent glow around the switcher pill for one cycle
 * Machinery, not mascots. Honest signal that state changed.
 */
export function PersonaMorph() {
  const morph = useGaya((s) => s.morph);

  return (
    <AnimatePresence>
      {morph && (
        <>
          {/* 1. Thin white scanline — top to bottom of the viewport */}
          <motion.div
            key={`scan-${morph.id}`}
            initial={{ y: -40, opacity: 0 }}
            animate={{ y: "100vh", opacity: [0, 1, 1, 0] }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6, ease: [0.32, 0.72, 0, 1], times: [0, 0.15, 0.85, 1] }}
            className="fixed left-0 right-0 pointer-events-none"
            style={{
              top: 0,
              height: 2,
              background:
                "linear-gradient(to bottom, transparent, var(--accent), transparent)",
              zIndex: 55
            }}
          />

          {/* 2. Faint glow at the switcher pill origin, single pulse */}
          <motion.div
            key={`origin-${morph.id}`}
            initial={{ opacity: 0.8, scale: 0.6 }}
            animate={{ opacity: 0, scale: 2 }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            className="fixed pointer-events-none"
            style={{
              zIndex: 56,
              left: morph.originX - 40,
              top: morph.originY - 40,
              width: 80,
              height: 80,
              border: "1px solid var(--accent)",
              background: "transparent"
            }}
          />

          {/* 3. Bottom-center confirmation chip */}
          <motion.div
            key={`sting-${morph.id}`}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: [0, 1, 1, 0], y: 0 }}
            transition={{ duration: 0.9, times: [0, 0.15, 0.75, 1] }}
            className="fixed pointer-events-none"
            style={{
              zIndex: 57,
              left: "50%",
              bottom: 88,
              transform: "translateX(-50%)",
              fontFamily: "JetBrains Mono, monospace",
              fontSize: 10,
              fontWeight: 700,
              letterSpacing: "0.24em",
              textTransform: "uppercase",
              color: "var(--bg)",
              background: "var(--accent)",
              padding: "6px 14px",
              border: "1px solid var(--accent)"
            }}
          >
            context :: {PERSONAS[morph.toPersona].codename}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
