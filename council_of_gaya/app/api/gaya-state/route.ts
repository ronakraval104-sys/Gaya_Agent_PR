import { NextResponse } from "next/server";
import { promises as fs } from "fs";
import fsSync from "fs";
import os from "os";
import path from "path";
import { getAntigravityStatus } from "@/lib/connectors/antigravity";

// Live Gaya/Antigravity state for Council of Gaya topbar sprite + dashboard.
// Priority: Live Antigravity session > .gaya events log fallback
// States: broken > hold > approved > spawning > thinking > idle > asleep

export const dynamic = "force-dynamic";

const GAYA_DIR = path.join(os.homedir(), ".gaya");
const G = GAYA_DIR;

type Ev = { ts?: string; ev?: string; agent?: string; tool?: string; decision?: string; reason?: string; verdict?: string };

async function tailLegacyEvents(file: string, bytes = 100_000): Promise<Ev[]> {
  try {
    const fh = await fs.open(file, "r");
    const { size } = await fh.stat();
    const start = Math.max(0, size - bytes);
    const buf = Buffer.alloc(size - start);
    await fh.read(buf, 0, buf.length, start);
    await fh.close();
    return buf
      .toString("utf8")
      .split(/\r?\n/)
      .slice(-200)
      .flatMap((l) => {
        try {
          return [JSON.parse(l) as Ev];
        } catch {
          return [];
        }
      });
  } catch {
    return [];
  }
}

export async function GET() {
  const agy = await getAntigravityStatus();

  let instinctsCount = 0;
  try {
    const raw = await fs.readFile(path.join(os.homedir(), ".gemini", "antigravity", "instincts.json"), "utf8");
    const arr = JSON.parse(raw);
    if (Array.isArray(arr)) instinctsCount = arr.length;
  } catch {}

  const stepCount = agy.stepIndex || 0;
  const contextPressure = Math.min(100, Math.round((stepCount / 40) * 100));

  // If Antigravity is active (active, idle, thinking, spawning, hold, approved), return it directly!
  if (agy.status !== "off" && agy.lastActiveAgoSec < 600) {
    return NextResponse.json({
      state: agy.state,
      detail: agy.detail,
      armed: "PASS",
      sessionId: agy.sessionId,
      stepIndex: agy.stepIndex,
      activeTool: agy.activeTool,
      toolSummary: agy.toolSummary,
      tokens: agy.tokens,
      lastActiveAgoSec: agy.lastActiveAgoSec,
      source: "antigravity",
      modelName: agy.modelName || "Gemini 2.5 Pro (Thinking)",
      harness: agy.harness || "Google Antigravity",
      activeSeat: agy.activeSeat || "bob",
      isProcessing: agy.state === "thinking" || agy.state === "spawning" || agy.state === "hold" || agy.lastActiveAgoSec < 20,
      ecc: {
        instinctsCount,
        contextPressure,
        securityStatus: "SECURE",
      },
    });
  }

  // Fallback to legacy events logs if Antigravity is asleep/off
  const now = Date.now();
  const age = (e: Ev) => (e.ts ? (now - new Date(e.ts).getTime()) / 1000 : 1e9);
  let status = "";
  try {
    status = (await fs.readFile(path.join(G, "STATUS"), "utf8")).trim();
  } catch {}
  const armed = status.split(" ")[0] || "PASS";
  const reply = (state: string, detail: string) =>
    NextResponse.json({
      state,
      detail,
      armed,
      sessionId: agy.sessionId,
      stepIndex: agy.stepIndex,
      source: "legacy",
      modelName: "Gemini 2.5 Pro (Thinking)",
      harness: "Google Antigravity",
      activeSeat: "bob",
      isProcessing: state === "thinking" || state === "spawning" || state === "hold",
      ecc: {
        instinctsCount,
        contextPressure,
        securityStatus: "SECURE",
      },
    });

  try {
    await fs.access(path.join(G, "DISABLED"));
    return reply("broken", "guard disabled");
  } catch {}
  if (status.startsWith("BROKEN")) return reply("broken", status);

  const evs = await tailLegacyEvents(path.join(G, "logs", "events.jsonl"));
  for (let i = evs.length - 1; i >= 0; i--) {
    const e = evs[i];
    const a = age(e);
    if (a > 600) break;
    if (e.ev === "guard" && a < 25) return reply("hold", `${e.decision}: ${(e.reason || "").slice(0, 60)}`);
    if (e.ev === "subagent_stop" && (e.agent === "logos" || e.agent === "edidth") && e.verdict === "PASS" && a < 15)
      return reply("approved", "LOGOS PASS");
  }
  const recent = evs.filter((e) => age(e) < 25);
  if (recent.some((e) => e.ev === "tool" && e.agent && e.agent !== "main")) return reply("spawning", "subagents working");
  if (recent.length) return reply("thinking", recent[recent.length - 1].tool || recent[recent.length - 1].ev || "");
  if (evs.length && age(evs[evs.length - 1]) < 600) return reply("idle", "standing by");

  // Return Antigravity asleep state if both are asleep
  return reply(agy.state || "asleep", agy.detail || "no session activity");
}
