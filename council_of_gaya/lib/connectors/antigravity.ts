import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";
import os from "node:os";

export interface AntigravityRecentStep {
  stepIndex: number;
  type: string;
  source: string;
  toolName?: string;
  toolSummary?: string;
  toolAction?: string;
  ageSec: number;
}

export interface AntigravityStatus {
  status: "ok" | "standby" | "off";
  sessionId: string;
  state: "thinking" | "spawning" | "hold" | "approved" | "idle" | "asleep";
  detail: string;
  activeTool?: string;
  toolSummary?: string;
  stepIndex: number;
  tokens: {
    inputTokens: number;
    cacheReadTokens: number;
    outputTokens: number;
  };
  lastActiveAgoSec: number;
  recentSteps: AntigravityRecentStep[];
  fetchedAt: number;
  error?: string;
  modelName: string;
  harness: string;
  activeSeat: "logos" | "bob" | "freya" | "tvashtar";
}

const ANTIGRAVITY_ROOT = path.join(os.homedir(), ".gemini", "antigravity");
const BRAIN_DIR = path.join(ANTIGRAVITY_ROOT, "brain");

interface RawStep {
  step_index?: number;
  source?: string;
  type?: string;
  status?: string;
  created_at?: string;
  input_tokens?: number;
  cache_read_tokens?: number;
  output_tokens?: number;
  content?: string;
  tool_calls?: Array<{
    name: string;
    args?: {
      toolSummary?: string;
      toolAction?: string;
      [key: string]: unknown;
    };
  }>;
}

function findActiveSession(): { sessionId: string; transcriptPath: string } | null {
  try {
    if (!fsSync.existsSync(BRAIN_DIR)) return null;

    const dirs = fsSync.readdirSync(BRAIN_DIR, { withFileTypes: true });
    let best: { sessionId: string; transcriptPath: string; mtime: number } | null = null;

    for (const d of dirs) {
      if (!d.isDirectory()) continue;
      const tPath = path.join(BRAIN_DIR, d.name, ".system_generated", "logs", "transcript.jsonl");
      try {
        const stat = fsSync.statSync(tPath);
        if (!best || stat.mtimeMs > best.mtime) {
          best = { sessionId: d.name, transcriptPath: tPath, mtime: stat.mtimeMs };
        }
      } catch {}
    }

    return best;
  } catch {
    return null;
  }
}

async function readTailSteps(filePath: string, maxBytes = 60_000): Promise<RawStep[]> {
  try {
    const fh = await fs.open(filePath, "r");
    const stat = await fh.stat();
    const readSize = Math.min(stat.size, maxBytes);
    const start = Math.max(0, stat.size - readSize);
    const buf = Buffer.alloc(readSize);
    await fh.read(buf, 0, buf.length, start);
    await fh.close();

    const lines = buf.toString("utf8").split(/\r?\n/);
    return lines.flatMap((l) => {
      try {
        return [JSON.parse(l) as RawStep];
      } catch {
        return [];
      }
    });
  } catch {
    return [];
  }
}

let cachedStatus: { at: number; value: AntigravityStatus } | null = null;
const CACHE_TTL_MS = 1_000;

export async function getAntigravityStatus(): Promise<AntigravityStatus> {
  if (cachedStatus && Date.now() - cachedStatus.at < CACHE_TTL_MS) {
    return cachedStatus.value;
  }

  const now = Date.now();
  const session = findActiveSession();

  if (!session) {
    const val: AntigravityStatus = {
      status: "off",
      sessionId: "none",
      state: "asleep",
      detail: "No active Antigravity session found",
      stepIndex: 0,
      tokens: { inputTokens: 0, cacheReadTokens: 0, outputTokens: 0 },
      lastActiveAgoSec: 99999,
      recentSteps: [],
      fetchedAt: now,
      modelName: "Gemini 2.5 Pro (Thinking)",
      harness: "Google Antigravity",
      activeSeat: "bob",
    };
    cachedStatus = { at: now, value: val };
    return val;
  }

  const steps = await readTailSteps(session.transcriptPath);
  if (!steps.length) {
    const val: AntigravityStatus = {
      status: "standby",
      sessionId: session.sessionId,
      state: "idle",
      detail: "Session initialized, waiting for input",
      stepIndex: 0,
      tokens: { inputTokens: 0, cacheReadTokens: 0, outputTokens: 0 },
      lastActiveAgoSec: 0,
      recentSteps: [],
      fetchedAt: now,
      modelName: "Gemini 2.5 Pro (Thinking)",
      harness: "Google Antigravity",
      activeSeat: "bob",
    };
    cachedStatus = { at: now, value: val };
    return val;
  }

  const lastStep = steps[steps.length - 1];
  const lastTs = lastStep.created_at ? new Date(lastStep.created_at).getTime() : now;
  const ageSec = Math.max(0, Math.round((now - lastTs) / 1000));

  let tokens = { inputTokens: 0, cacheReadTokens: 0, outputTokens: 0 };
  for (let i = steps.length - 1; i >= 0; i--) {
    const s = steps[i];
    if (s.input_tokens || s.cache_read_tokens || s.output_tokens) {
      tokens = {
        inputTokens: s.input_tokens || 0,
        cacheReadTokens: s.cache_read_tokens || 0,
        outputTokens: s.output_tokens || 0,
      };
      break;
    }
  }

  let state: AntigravityStatus["state"] = "idle";
  let detail = "Antigravity standing by";
  let activeTool: string | undefined;
  let toolSummary: string | undefined;

  // Evaluate recent steps for active state within 45 seconds
  if (ageSec < 45) {
    for (let i = steps.length - 1; i >= Math.max(0, steps.length - 6); i--) {
      const s = steps[i];
      const sAge = s.created_at ? (now - new Date(s.created_at).getTime()) / 1000 : 999;
      if (sAge > 50) continue;

      if (s.content && s.content.includes("[🛡️ LOGOS]") && s.content.includes("PASS")) {
        state = "approved";
        detail = "LOGOS PASS :: Gate verified";
        break;
      }

      if (s.tool_calls && s.tool_calls.length > 0) {
        const tc = s.tool_calls[0];
        activeTool = tc.name;
        const rawSummary = tc.args?.toolSummary || tc.args?.toolAction || tc.name;
        toolSummary = typeof rawSummary === "string" ? rawSummary.replace(/^["']|["']$/g, "").trim() : tc.name;

        if (tc.name === "ask_question") {
          state = "hold";
          detail = `Awaiting input: ${toolSummary}`;
          break;
        }

        if (tc.name === "invoke_subagent") {
          state = "spawning";
          detail = `Subagents active: ${toolSummary}`;
          break;
        }

        state = "thinking";
        detail = toolSummary;
        break;
      }

      if (s.type === "PLANNER_RESPONSE") {
        state = "thinking";
        detail = "Deep thinking & planning";
        break;
      }
    }
  } else if (ageSec < 600) {
    state = "idle";
    const mins = Math.floor(ageSec / 60);
    detail = mins > 0 ? `Antigravity standing by (${mins}m ago)` : `Antigravity standing by`;
  } else {
    state = "asleep";
    detail = "No recent session activity";
  }

  const recentSteps: AntigravityRecentStep[] = steps.slice(-8).map((s) => ({
    stepIndex: s.step_index ?? 0,
    type: s.type ?? "UNKNOWN",
    source: s.source ?? "MODEL",
    toolName: s.tool_calls?.[0]?.name,
    toolSummary: s.tool_calls?.[0]?.args?.toolSummary,
    toolAction: s.tool_calls?.[0]?.args?.toolAction,
    ageSec: s.created_at ? Math.max(0, Math.round((now - new Date(s.created_at).getTime()) / 1000)) : 0,
  }));

  let activeSeat: "logos" | "bob" | "freya" | "tvashtar" = "bob";
  const detLow = detail.toLowerCase();
  const toolLow = (activeTool || "").toLowerCase();

  if (state === "approved" || toolLow === "ask_question" || detLow.includes("logos") || detLow.includes("qc") || detLow.includes("audit") || detLow.includes("check")) {
    activeSeat = "logos";
  } else if (toolLow.includes("rea") || toolLow.includes("reverse") || detLow.includes("tvashtar") || detLow.includes("mod") || detLow.includes("disassembly")) {
    activeSeat = "tvashtar";
  } else if (toolLow.includes("canva") || detLow.includes("freya") || detLow.includes("design") || detLow.includes("ui") || detLow.includes("motion") || detLow.includes("css")) {
    activeSeat = "freya";
  } else {
    activeSeat = "bob";
  }

  const val: AntigravityStatus = {
    status: ageSec < 600 ? "ok" : "standby",
    sessionId: session.sessionId,
    state,
    detail,
    activeTool,
    toolSummary,
    stepIndex: lastStep.step_index ?? 0,
    tokens,
    lastActiveAgoSec: ageSec,
    recentSteps,
    fetchedAt: now,
    modelName: "Gemini 2.5 Pro (Thinking)",
    harness: "Google Antigravity",
    activeSeat,
  };

  cachedStatus = { at: now, value: val };
  return val;
}
