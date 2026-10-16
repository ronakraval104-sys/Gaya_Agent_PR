import type { SessionEntry } from "./store";

/**
 * Aura + XP protocol — derives operator morale + session activity from
 * the SessionChronicle event stream. Baseline title/level lifted from the
 * OMNI_GAYA charter Progression table (Level 8 · 🏆 Conqueror).
 *
 * Scoring lineage:
 *   Full   +10   (a shipped skill / real action)
 *   Partial +5   (session-start bonus)
 *   Small  +2    (record read, exploring)
 *   Neutral +1   (nav events)
 *
 * Aura state derived from event RATE in the last 5 minutes:
 *   0 events    → cold  (dim, no dot pulse)
 *   1-2 events  → cool  (steady blue-grey)
 *   3-5 events  → warm  (amber, no pulse)
 *   6+ events   → alive (green pulse — R0n is on a roll)
 */

export type AuraState = "cold" | "cool" | "warm" | "alive";

export interface AuraStatus {
  title: string;                // e.g. "🏆 Conqueror"
  level: number;                // 8 (baseline from OMNI charter)
  sessionXp: number;
  xpForNext: number;            // XP needed to hit next level
  pctToNext: number;            // 0-100
  aura: AuraState;
  recentEventCount: number;     // events in last 5 min
  totalEvents: number;
}

const EVENT_XP: Record<string, number> = {
  "session-start": 5,
  skill:   10,   // fired a skill → real action
  record:   2,   // read a record → exploring / learning
  seat:     1,   // pinned a seat → navigation
  persona:  1,   // swapped persona → context switch
  console:  3    // slash console log → captured a thought
};

const RECENT_WINDOW_MS = 5 * 60 * 1000;
const XP_PER_LEVEL = 100;
const BASELINE_LEVEL = 8;
const BASELINE_TITLE = "🏆 Conqueror";

export function computeAura(chronicle: SessionEntry[]): AuraStatus {
  const now = Date.now();
  const sessionXp = chronicle.reduce((sum, e) => sum + (EVENT_XP[e.kind] ?? 0), 0);
  const recentEventCount = chronicle.filter((e) => now - e.at < RECENT_WINDOW_MS).length;

  const aura: AuraState =
    recentEventCount === 0 ? "cold"
    : recentEventCount <= 2 ? "cool"
    : recentEventCount <= 5 ? "warm"
    : "alive";

  const xpForNext = XP_PER_LEVEL;
  const pctToNext = Math.min(100, Math.round((sessionXp / xpForNext) * 100));

  return {
    title: BASELINE_TITLE,
    level: BASELINE_LEVEL,
    sessionXp,
    xpForNext,
    pctToNext,
    aura,
    recentEventCount,
    totalEvents: chronicle.length
  };
}

/** Map aura state to the terminal Dot primitive's state token. */
export function auraDotState(aura: AuraState): "ok" | "warn" | "err" | "off" {
  switch (aura) {
    case "alive": return "ok";
    case "warm":  return "warn";
    case "cool":  return "off";
    case "cold":  return "off";
  }
}

/** One-word human label for the aura state. */
export function auraLabel(aura: AuraState): string {
  return aura.toUpperCase();
}
