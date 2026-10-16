"use client";

import { create } from "zustand";
import { DEFAULT_PERSONA, type PersonaId } from "./personas";

export interface ActiveTask {
  id: string;
  skillSlug: string;
  seatId: string;
  personaId: PersonaId;
  startedAt: number;
}

export interface MorphEvent {
  id: string;
  fromPersona: PersonaId;
  toPersona: PersonaId;
  originX: number;   // px from viewport left (usually near persona switcher)
  originY: number;   // px from viewport top
  startedAt: number;
}

export interface SessionEntry {
  id: string;
  kind: "record" | "seat" | "persona" | "skill" | "console" | "session-start";
  label: string;
  targetSlug?: string;    // for record events → clickable to reopen
  targetSeat?: string;    // for seat pin events → clickable to re-pin
  at: number;
}

const CHRONICLE_KEY = "gaya_council_chronicle_v1";
const CHRONICLE_CAP = 40;

function loadChronicle(): SessionEntry[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(CHRONICLE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as SessionEntry[];
    return Array.isArray(parsed) ? parsed.slice(-CHRONICLE_CAP) : [];
  } catch {
    return [];
  }
}

function saveChronicle(entries: SessionEntry[]) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(CHRONICLE_KEY, JSON.stringify(entries.slice(-CHRONICLE_CAP)));
  } catch {
    // localStorage full/blocked — silently ignore
  }
}

interface GayaState {
  persona: PersonaId;
  activeTasks: ActiveTask[];
  reactorFlare: number; // 0-1, animates arc pulse when task fires
  consoleOpen: boolean;
  focusedSkill: string | null;
  focusedSeat: string | null;
  pinnedSeat: string | null;
  openRecordSlug: string | null;
  morph: MorphEvent | null;
  chronicle: SessionEntry[];
  chronicleVisible: boolean;

  setPersona: (p: PersonaId) => void;
  swapPersona: (p: PersonaId, originX?: number, originY?: number) => void;
  logEvent: (entry: Omit<SessionEntry, "id" | "at">) => void;
  clearChronicle: () => void;
  toggleChronicleVisible: () => void;
  hideChronicle: () => void;
  showChronicle: () => void;
  fireSkill: (skillSlug: string, seatId: string) => void;
  completeTask: (id: string) => void;
  toggleConsole: () => void;
  setFocusedSkill: (s: string | null) => void;
  setFocusedSeat: (s: string | null) => void;
  togglePinnedSeat: (s: string) => void;
  clearPinnedSeat: () => void;
  openRecord: (slug: string) => void;
  closeRecord: () => void;
  endMorph: () => void;
  settingsOpen: boolean;
  toggleSettings: () => void;
  openSettings: () => void;
  closeSettings: () => void;
}

export const useGaya = create<GayaState>((set, get) => ({
  persona: DEFAULT_PERSONA,
  activeTasks: [],
  reactorFlare: 0,
  consoleOpen: false,
  focusedSkill: null,
  focusedSeat: null,
  pinnedSeat: null,
  openRecordSlug: null,
  morph: null,
  chronicle: loadChronicle(),
  chronicleVisible: true,
  settingsOpen: false,

  setPersona: (p) => {
    if (typeof document !== "undefined") {
      document.documentElement.dataset.persona = p;
    }
    set({ persona: p, reactorFlare: 1 });
    setTimeout(() => set({ reactorFlare: 0 }), 900);
  },

  swapPersona: (p, originX, originY) => {
    const cur = get().persona;
    if (cur === p) return;
    // log persona swap into chronicle
    const chronEntry: SessionEntry = {
      id: `se_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      kind: "persona",
      label: `swapped ${cur} → ${p}`,
      at: Date.now()
    };
    const nextChron = [...get().chronicle, chronEntry].slice(-CHRONICLE_CAP);
    saveChronicle(nextChron);
    set({ chronicle: nextChron });
    // Trigger cinematic morph event; PersonaMorph overlay + StatusBar listen.
    const morphEvent: MorphEvent = {
      id: `mo_${Date.now()}`,
      fromPersona: cur,
      toPersona: p,
      originX: originX ?? (typeof window !== "undefined" ? window.innerWidth - 96 : 0),
      originY: originY ?? 48,
      startedAt: Date.now()
    };
    set({ morph: morphEvent, reactorFlare: 1 });
    // Swap the DOM data-attribute at the midpoint of the ceremony so the
    // clip-path expansion visually "paints" the new palette across the viewport.
    setTimeout(() => {
      if (typeof document !== "undefined") {
        document.documentElement.dataset.persona = p;
      }
      set({ persona: p });
    }, 240);
    setTimeout(() => set({ reactorFlare: 0 }), 900);
    setTimeout(() => set({ morph: null }), 950);
  },

  fireSkill: (skillSlug, seatId) => {
    const id = `t_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
    set((s) => ({
      activeTasks: [
        ...s.activeTasks,
        { id, skillSlug, seatId, personaId: s.persona, startedAt: Date.now() }
      ],
      reactorFlare: 1
    }));
    setTimeout(() => set({ reactorFlare: 0 }), 800);
    // log to chronicle
    const chronEntry: SessionEntry = {
      id: `se_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      kind: "skill",
      label: `fired ${skillSlug} → ${seatId}`,
      at: Date.now()
    };
    const nextChron = [...get().chronicle, chronEntry].slice(-CHRONICLE_CAP);
    saveChronicle(nextChron);
    set({ chronicle: nextChron });
  },

  completeTask: (id) =>
    set((s) => ({ activeTasks: s.activeTasks.filter((t) => t.id !== id) })),

  toggleConsole: () => set((s) => ({ consoleOpen: !s.consoleOpen })),
  setFocusedSkill: (s) => set({ focusedSkill: s }),
  setFocusedSeat: (s) => set({ focusedSeat: s }),
  togglePinnedSeat: (seatId) => {
    const wasPin = get().pinnedSeat;
    const nowPin = wasPin === seatId ? null : seatId;
    set({ pinnedSeat: nowPin });
    if (nowPin) {
      const chronEntry: SessionEntry = {
        id: `se_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
        kind: "seat",
        label: `pinned ${seatId}`,
        targetSeat: seatId,
        at: Date.now()
      };
      const nextChron = [...get().chronicle, chronEntry].slice(-CHRONICLE_CAP);
      saveChronicle(nextChron);
      set({ chronicle: nextChron });
    }
  },
  clearPinnedSeat: () => set({ pinnedSeat: null }),
  openRecord: (slug) => {
    set({ openRecordSlug: slug });
    const entry: SessionEntry = {
      id: `se_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      kind: "record",
      label: `opened ${slug}`,
      targetSlug: slug,
      at: Date.now()
    };
    const next = [...get().chronicle, entry].slice(-CHRONICLE_CAP);
    set({ chronicle: next });
    saveChronicle(next);
  },
  closeRecord: () => set({ openRecordSlug: null }),
  endMorph: () => set({ morph: null }),

  logEvent: (partial) => {
    const entry: SessionEntry = {
      id: `se_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      at: Date.now(),
      ...partial
    };
    const next = [...get().chronicle, entry].slice(-CHRONICLE_CAP);
    set({ chronicle: next });
    saveChronicle(next);
  },
  clearChronicle: () => {
    set({ chronicle: [] });
    saveChronicle([]);
  },
  toggleChronicleVisible: () => set((s) => ({ chronicleVisible: !s.chronicleVisible })),
  hideChronicle: () => set({ chronicleVisible: false }),
  showChronicle: () => set({ chronicleVisible: true }),
  toggleSettings: () => set((s) => ({ settingsOpen: !s.settingsOpen })),
  openSettings: () => set({ settingsOpen: true }),
  closeSettings: () => set({ settingsOpen: false })
}));

