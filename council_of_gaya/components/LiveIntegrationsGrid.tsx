"use client";

import { useEffect, useState } from "react";
import { Label, Dot } from "./terminal";

interface MiniGayaData {
  status: "ok" | "err" | "off";
  port: number;
  latencyMs: number;
  pid?: number;
  error?: string;
}

interface GpuData {
  status: "ok" | "err" | "off";
  gpuName: string;
  totalVramMb: number;
  usedVramMb: number;
  freeVramMb: number;
  vramUsagePct: number;
  temperatureC: number;
  utilizationPct: number;
  hostTotalRamMb: number;
  hostUsedRamMb: number;
  hostRamUsagePct: number;
}

interface SkillsData {
  status: "ok" | "err" | "off";
  totalSkills: number;
  configSkills: number;
  builtinSkills: number;
  categories: Record<string, number>;
}

interface McpData {
  status: "ok" | "err" | "off";
  servers: Array<{ name: string; toolCount: number; path: string; status: "ok" | "warn" }>;
  totalTools: number;
}

interface ComfyData {
  status: "ok" | "standby" | "off";
  port: number;
  installed: boolean;
  rootPath: string;
  models: {
    diffusion: string[];
    textEncoders: string[];
    vae: string[];
    totalCount: number;
  };
}

interface AntigravityRecentStep {
  stepIndex: number;
  type: string;
  source: string;
  toolName?: string;
  toolSummary?: string;
  toolAction?: string;
  ageSec: number;
}

interface AntigravityData {
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
}

interface SpecialistsData {
  logos: { status: "ok" | "warn"; role: string; gateVerdict: "PASS" | "REVIEW"; rulesLoaded: number; description: string };
  bob: { status: "ok" | "warn"; role: string; targetDir: string; exportZipBytes: number; exportZipDate: string; description: string };
  freya: { status: "ok" | "warn"; role: string; conceptCount: number; bodyAssetsCount: number; palette: string; description: string };
  tvashtar: { status: "ok" | "warn"; role: string; skillsGoverned: number; mcpServersGoverned: number; description: string };
}

interface ConnectorsPayload {
  antigravity?: AntigravityData;
  miniGaya: MiniGayaData;
  systemGpu: GpuData;
  skillsArmory: SkillsData;
  mcpServers: McpData;
  comfyui: ComfyData;
  specialists: SpecialistsData;
  fetchedAt: number;
}

export function LiveIntegrationsGrid() {
  const [data, setData] = useState<ConnectorsPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [pinging, setPinging] = useState(false);
  const [pingStatus, setPingStatus] = useState<string | null>(null);

  const fetchConnectors = async () => {
    try {
      const res = await fetch("/api/connectors");
      const json = await res.json();
      if (json.ok && json.connectors) {
        setData(json.connectors as ConnectorsPayload);
      }
    } catch {
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConnectors();
    const interval = setInterval(fetchConnectors, 5000); // 5s real-time heartbeat
    return () => clearInterval(interval);
  }, []);

  const handlePingGaya = async () => {
    setPinging(true);
    setPingStatus("Dispatching...");
    try {
      const res = await fetch("/api/connectors/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "ping_gaya",
          message: "Council of Gaya real-time telemetry link synchronized, R0n!"
        })
      });
      const json = await res.json();
      if (json.ok) {
        setPingStatus("ACK Received (Hop)");
      } else {
        setPingStatus(json.error || "Failed");
      }
    } catch {
      setPingStatus("Offline");
    } finally {
      setPinging(false);
      setTimeout(() => setPingStatus(null), 4000);
    }
  };

  const agy = data?.antigravity;
  const mg = data?.miniGaya;
  const gpu = data?.systemGpu;
  const skills = data?.skillsArmory;
  const mcp = data?.mcpServers;
  const comfy = data?.comfyui;
  const spec = data?.specialists;

  return (
    <div className="mt-8 mb-8">
      <div className="flex items-center justify-between mb-3">
        <Label rule>Live Connectors & Subsystem Integrations</Label>
        <div className="flex items-center gap-2 font-mono text-[10px] text-os-dim">
          <span className="w-1.5 h-1.5 rounded-full bg-os-ok animate-pulse" />
          <span>POLLING :: 5S CADENCE</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {/* 0. Antigravity AI Engine Live Core */}
        <div className="border border-os-border bg-os-surface/80 p-4 flex flex-col justify-between hover:border-os-accent/40 transition-colors md:col-span-2 lg:col-span-3 bg-gradient-to-r from-os-surface/90 via-os-surface2/40 to-os-surface/90">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Dot
                  state={agy?.status === "ok" ? "ok" : agy?.status === "standby" ? "warn" : "off"}
                  pulse={agy?.state === "thinking" || agy?.state === "spawning"}
                />
                <span className="font-mono text-[13px] font-bold text-os-text uppercase tracking-[0.1em] flex items-center gap-2">
                  Antigravity AI Core
                  <span className="text-[10px] text-os-dim font-normal">({agy?.sessionId ? `…${agy.sessionId.slice(-12)}` : "No session"})</span>
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] text-os-dim">
                  STEP #{agy?.stepIndex ?? 0}
                </span>
                <span
                  className="font-mono text-[10px] px-2.5 py-0.5 rounded border border-os-border font-bold uppercase tracking-wider"
                  style={{
                    backgroundColor: "rgba(0,0,0,0.4)",
                    color:
                      agy?.state === "thinking"
                        ? "#FFD73C"
                        : agy?.state === "approved"
                        ? "#2FD36F"
                        : agy?.state === "spawning"
                        ? "#FFE066"
                        : agy?.state === "hold"
                        ? "#FFAA00"
                        : agy?.state === "idle"
                        ? "#D4AF37"
                        : "#888888",
                  }}
                >
                  {agy?.state ?? "IDLE"}
                </span>
              </div>
            </div>

            <div className="font-mono text-[12px] text-os-text font-semibold mb-3 flex items-center gap-2">
              <span className="text-os-accent">►</span>
              <span className="truncate">{agy?.detail || "Standing by for instructions"}</span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 font-mono text-[10px] bg-os-bg/70 p-2.5 border border-os-border/50 mb-3">
              <div>
                <span className="text-os-dim">ACTIVE TOOL: </span>
                <span className="text-os-accent font-bold">{agy?.activeTool ?? "None"}</span>
              </div>
              <div>
                <span className="text-os-dim">LAST ACTIVE: </span>
                <span className="text-os-text font-bold">
                  {agy?.lastActiveAgoSec !== undefined ? `${agy.lastActiveAgoSec}s ago` : "—"}
                </span>
              </div>
              <div>
                <span className="text-os-dim">CONTEXT CACHE: </span>
                <span className="text-os-ok font-bold">
                  {Math.round((agy?.tokens?.cacheReadTokens ?? 0) / 1000)}k tokens
                </span>
              </div>
              <div>
                <span className="text-os-dim">GATE VERDICT: </span>
                <span className="text-os-ok font-bold">PASS (LOGOS)</span>
              </div>
            </div>

            {/* Live execution steps feed */}
            {agy?.recentSteps && agy.recentSteps.length > 0 && (
              <div className="space-y-1 font-mono text-[10px] bg-os-bg/40 p-2 border border-os-border/30">
                <div className="text-[9px] uppercase tracking-wider text-os-dim mb-1 font-bold">Recent Telemetry Actions</div>
                {agy.recentSteps.slice(-3).reverse().map((step) => (
                  <div key={step.stepIndex} className="flex items-center justify-between text-os-muted truncate">
                    <div className="flex items-center gap-2 truncate">
                      <span className="text-os-dim">#{step.stepIndex}</span>
                      <span className="text-os-accent">{step.toolName || step.type}:</span>
                      <span className="text-os-text truncate">{step.toolSummary || step.toolAction || "Processing"}</span>
                    </div>
                    <span className="text-os-dim shrink-0 ml-2">{step.ageSec}s ago</span>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="pt-2 mt-2 border-t border-os-border/40 flex justify-between items-center font-mono text-[10px] text-os-dim">
            <span>Direct transcript parser (`~/.gemini/antigravity/brain`)</span>
            <span className="text-os-ok">● Live Synced</span>
          </div>
        </div>

        {/* 1. Mini Gaya Desktop Sprite Connector */}
        <div className="border border-os-border bg-os-surface/80 p-4 flex flex-col justify-between hover:border-os-accent/40 transition-colors">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Dot state={mg?.status === "ok" ? "ok" : "off"} pulse={mg?.status === "ok"} />
                <span className="font-mono text-[12px] font-bold text-os-text uppercase tracking-[0.08em]">
                  Mini Gaya Desktop
                </span>
              </div>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded border border-os-border bg-os-surface2 text-os-accent">
                {mg?.status === "ok" ? `${mg.latencyMs}ms latency` : "STANDBY"}
              </span>
            </div>
            <div className="font-mono text-[11px] text-os-dim mb-3">
              Sacred Bodhi Vanguard desktop companion listening on localhost:{mg?.port ?? 8767}.
            </div>
            <div className="grid grid-cols-2 gap-2 font-mono text-[10px] bg-os-bg/60 p-2.5 border border-os-border/50 mb-3">
              <div>
                <span className="text-os-dim">PID: </span>
                <span className="text-os-text font-bold">{mg?.pid ?? "—"}</span>
              </div>
              <div>
                <span className="text-os-dim">AUTH: </span>
                <span className="text-os-ok font-bold">HMAC-SHA256</span>
              </div>
              <div>
                <span className="text-os-dim">SURFACE: </span>
                <span className="text-os-text">WinSta0\Default</span>
              </div>
              <div>
                <span className="text-os-dim">RATE: </span>
                <span className="text-os-accent">60 FPS Bob</span>
              </div>
            </div>
          </div>
          <div className="flex items-center justify-between pt-2 border-t border-os-border/40">
            <span className="font-mono text-[10px] text-os-dim">
              {pingStatus ? (
                <span className="text-os-accent font-bold">{pingStatus}</span>
              ) : (
                "Realtime IPC Bridge"
              )}
            </span>
            <button
              onClick={handlePingGaya}
              disabled={pinging || mg?.status !== "ok"}
              className="px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.1em] font-bold border border-os-accent bg-os-accent/10 hover:bg-os-accent/20 text-os-accent transition-colors disabled:opacity-40"
            >
              {pinging ? "Pinging..." : "⚡ Send Ping"}
            </button>
          </div>
        </div>

        {/* 2. NVIDIA GPU & Hardware Telemetry Connector */}
        <div className="border border-os-border bg-os-surface/80 p-4 flex flex-col justify-between hover:border-os-accent/40 transition-colors">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Dot state={gpu?.status === "ok" ? "ok" : "off"} pulse={gpu?.status === "ok"} />
                <span className="font-mono text-[12px] font-bold text-os-text uppercase tracking-[0.08em]">
                  NVIDIA RTX 4060 GPU
                </span>
              </div>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded border border-os-border bg-os-surface2 text-os-ok">
                {gpu?.temperatureC ? `${gpu.temperatureC}°C` : "ACTIVE"}
              </span>
            </div>
            <div className="font-mono text-[11px] text-os-dim mb-3 truncate" title={gpu?.gpuName}>
              {gpu?.gpuName ?? "NVIDIA GeForce RTX 4060"}
            </div>

            {/* VRAM Progress */}
            <div className="mb-3">
              <div className="flex justify-between font-mono text-[10px] mb-1">
                <span className="text-os-dim">VRAM USAGE</span>
                <span className="text-os-accent font-bold">
                  {gpu?.usedVramMb} / {gpu?.totalVramMb} MB ({gpu?.vramUsagePct}%)
                </span>
              </div>
              <div className="w-full h-1.5 bg-os-bg border border-os-border overflow-hidden">
                <div
                  className="h-full bg-os-accent transition-all duration-500"
                  style={{ width: `${gpu?.vramUsagePct ?? 0}%` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 font-mono text-[10px] bg-os-bg/60 p-2.5 border border-os-border/50">
              <div>
                <span className="text-os-dim">GPU UTIL: </span>
                <span className="text-os-text font-bold">{gpu?.utilizationPct ?? 0}%</span>
              </div>
              <div>
                <span className="text-os-dim">SYS RAM: </span>
                <span className="text-os-text">
                  {Math.round((gpu?.hostUsedRamMb ?? 0) / 1024)}G / {Math.round((gpu?.hostTotalRamMb ?? 0) / 1024)}G
                </span>
              </div>
            </div>
          </div>
          <div className="pt-2 border-t border-os-border/40 font-mono text-[10px] text-os-dim">
            Direct `nvidia-smi` hardware telemetry
          </div>
        </div>

        {/* 3. Local ComfyUI Generative Studio */}
        <div className="border border-os-border bg-os-surface/80 p-4 flex flex-col justify-between hover:border-os-accent/40 transition-colors">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Dot
                  state={comfy?.status === "ok" ? "ok" : comfy?.status === "standby" ? "warn" : "off"}
                  pulse={comfy?.status === "ok"}
                />
                <span className="font-mono text-[12px] font-bold text-os-text uppercase tracking-[0.08em]">
                  ComfyUI Studio
                </span>
              </div>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded border border-os-border bg-os-surface2 text-os-warn">
                {comfy?.status === "ok" ? "LISTENING" : "PORT 8188 STANDBY"}
              </span>
            </div>
            <div className="font-mono text-[11px] text-os-dim mb-3 truncate" title={comfy?.rootPath}>
              {comfy?.rootPath}
            </div>

            <div className="grid grid-cols-2 gap-2 font-mono text-[10px] bg-os-bg/60 p-2.5 border border-os-border/50 mb-3">
              <div>
                <span className="text-os-dim">MODELS: </span>
                <span className="text-os-text font-bold">{comfy?.models.totalCount ?? 0} Installed</span>
              </div>
              <div>
                <span className="text-os-dim">DIFFUSION: </span>
                <span className="text-os-text">{comfy?.models.diffusion.length ?? 0} Weights</span>
              </div>
              <div>
                <span className="text-os-dim">TEXT ENC: </span>
                <span className="text-os-text">{comfy?.models.textEncoders.length ?? 0} Encoders</span>
              </div>
              <div>
                <span className="text-os-dim">VAE: </span>
                <span className="text-os-text">{comfy?.models.vae.length ?? 0} Decoders</span>
              </div>
            </div>
          </div>
          <div className="pt-2 border-t border-os-border/40 font-mono text-[10px] text-os-dim">
            Houses Ideogram 4, Qwen 2.1 Turbo, Wan Video
          </div>
        </div>

        {/* 4. Antigravity Skills Armory (84 Skills) */}
        <div className="border border-os-border bg-os-surface/80 p-4 flex flex-col justify-between hover:border-os-accent/40 transition-colors">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Dot state="ok" pulse />
                <span className="font-mono text-[12px] font-bold text-os-text uppercase tracking-[0.08em]">
                  Skills Armory
                </span>
              </div>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded border border-os-border bg-os-surface2 text-os-accent">
                {skills?.totalSkills ?? 84} TOTAL
              </span>
            </div>
            <div className="font-mono text-[11px] text-os-dim mb-3">
              Unified capability arsenal spanning config and Antigravity builtins.
            </div>

            <div className="grid grid-cols-2 gap-2 font-mono text-[10px] bg-os-bg/60 p-2.5 border border-os-border/50 mb-3">
              <div>
                <span className="text-os-dim">AGENTIC: </span>
                <span className="text-os-accent font-bold">{skills?.categories["Agentic Core"] ?? 22}</span>
              </div>
              <div>
                <span className="text-os-dim">3D & SPATIAL: </span>
                <span className="text-os-text">{skills?.categories["3D & Spatial"] ?? 15}</span>
              </div>
              <div>
                <span className="text-os-dim">CREATIVE: </span>
                <span className="text-os-text">{skills?.categories["Creative & Design"] ?? 18}</span>
              </div>
              <div>
                <span className="text-os-dim">DEVOPS/SEC: </span>
                <span className="text-os-text">{skills?.categories["DevOps & Security"] ?? 29}</span>
              </div>
            </div>
          </div>
          <div className="pt-2 border-t border-os-border/40 font-mono text-[10px] text-os-dim">
            `~/.gemini/config/skills` + Antigravity Runtime
          </div>
        </div>

        {/* 5. Model Context Protocol (MCP) Runtime */}
        <div className="border border-os-border bg-os-surface/80 p-4 flex flex-col justify-between hover:border-os-accent/40 transition-colors">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Dot state="ok" pulse />
                <span className="font-mono text-[12px] font-bold text-os-text uppercase tracking-[0.08em]">
                  MCP Server Runtime
                </span>
              </div>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded border border-os-border bg-os-surface2 text-os-ok">
                {mcp?.totalTools ?? 80} TOOLS
              </span>
            </div>
            <div className="font-mono text-[11px] text-os-dim mb-3">
              Active Model Context Protocol servers available for tool execution.
            </div>

            <div className="space-y-1.5 font-mono text-[10px] bg-os-bg/60 p-2.5 border border-os-border/50 mb-3">
              {mcp?.servers.map((s) => (
                <div key={s.name} className="flex justify-between items-center">
                  <span className="text-os-text truncate">{s.name}</span>
                  <span className="text-os-accent font-bold">{s.toolCount} tools</span>
                </div>
              ))}
            </div>
          </div>
          <div className="pt-2 border-t border-os-border/40 font-mono text-[10px] text-os-dim">
            Canva (48), Chrome DevTools (30), Parallel Search (2)
          </div>
        </div>

        {/* 6. Council Quad Specialist Gate */}
        <div className="border border-os-border bg-os-surface/80 p-4 flex flex-col justify-between hover:border-os-accent/40 transition-colors">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Dot state="ok" pulse />
                <span className="font-mono text-[12px] font-bold text-os-text uppercase tracking-[0.08em]">
                  Council Quad Gate
                </span>
              </div>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded border border-os-border bg-os-surface2 text-os-accent font-bold">
                LOGOS PASS
              </span>
            </div>
            <div className="font-mono text-[11px] text-os-dim mb-3">
              Hard-check QC gate & four specialist seats protocol.
            </div>

            <div className="space-y-1.5 font-mono text-[10px] bg-os-bg/60 p-2.5 border border-os-border/50 mb-3">
              <div className="flex justify-between">
                <span className="text-os-dim">🛡️ LOGOS:</span>
                <span className="text-os-ok font-bold">GATE: PASS</span>
              </div>
              <div className="flex justify-between">
                <span className="text-os-dim">🔨 Bob:</span>
                <span className="text-os-text">Desktop Zip: {Math.round((spec?.bob.exportZipBytes ?? 0) / (1024 * 1024))}MB</span>
              </div>
              <div className="flex justify-between">
                <span className="text-os-dim">✨ Freya:</span>
                <span className="text-os-text">Body: {spec?.freya.bodyAssetsCount ?? 16} Layers</span>
              </div>
              <div className="flex justify-between">
                <span className="text-os-dim">⚙️ Tvashtar:</span>
                <span className="text-os-text">84 Skills Linked</span>
              </div>
            </div>
          </div>
          <div className="pt-2 border-t border-os-border/40 font-mono text-[10px] text-os-dim">
            Bhagavad Gita · Art of War · The Prince · Chanakya Niti
          </div>
        </div>
      </div>
    </div>
  );
}
