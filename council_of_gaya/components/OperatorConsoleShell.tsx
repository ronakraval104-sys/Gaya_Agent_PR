"use client";

import { useEffect, useState } from "react";
import { StatCard, Label, Dot } from "./terminal";
import { useGaya } from "@/lib/store";

import { LiveIntegrationsGrid } from "./LiveIntegrationsGrid";

interface CountsPayload {
  ok: boolean;
  total: number;
  byType: Record<string, number>;
  byPersona: Record<string, number>;
  byPriority: Record<string, number>;
  boulderCount: number;
  brokenLinkCount: number;
  lastIngestAt?: number;
}

interface RecordSlim {
  slug: string;
  type: string;
  persona: string;
  priority: string;
}

interface MiniGayaData {
  status: "ok" | "err" | "off";
  port: number;
  latencyMs: number;
  pid?: number;
}

interface GpuData {
  status: "ok" | "err" | "off";
  gpuName: string;
  totalVramMb: number;
  usedVramMb: number;
  vramUsagePct: number;
  temperatureC: number;
  utilizationPct: number;
}

interface SkillsData {
  status: "ok" | "err" | "off";
  totalSkills: number;
  configSkills: number;
  builtinSkills: number;
}

interface McpData {
  status: "ok" | "err" | "off";
  totalTools: number;
  servers: Array<{ name: string; toolCount: number }>;
}

interface ComfyData {
  status: "ok" | "standby" | "off";
  port: number;
  models: { totalCount: number };
}

interface AntigravityShellData {
  status: "ok" | "standby" | "off";
  state: string;
  stepIndex: number;
  detail: string;
  activeTool?: string;
  lastActiveAgoSec: number;
}

interface AllConnectors {
  antigravity?: AntigravityShellData;
  miniGaya: MiniGayaData;
  systemGpu: GpuData;
  skillsArmory: SkillsData;
  mcpServers: McpData;
  comfyui: ComfyData;
}

export function OperatorConsoleShell() {
  const persona = useGaya((s) => s.persona);
  const activeTasks = useGaya((s) => s.activeTasks);
  const [counts, setCounts] = useState<CountsPayload | null>(null);
  const [records, setRecords] = useState<RecordSlim[]>([]);
  const [now, setNow] = useState<string>("");
  const [conn, setConn] = useState<AllConnectors | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const [c, full] = await Promise.all([
          fetch("/api/knowledge/counts").then((r) => r.json()),
          fetch("/api/knowledge/full").then((r) => r.json())
        ]);
        if (cancelled) return;
        setCounts(c as CountsPayload);
        setRecords((full.nodes ?? []) as RecordSlim[]);
      } catch {}
    };
    load();
    const id = setInterval(load, 15000);
    return () => { cancelled = true; clearInterval(id); };
  }, []);

  useEffect(() => {
    const tick = () => setNow(new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }));
    tick();
    const id = setInterval(tick, 30_000);
    return () => clearInterval(id);
  }, []);

  // Live connectors: one bulk poll of all sources
  useEffect(() => {
    let cancelled = false;
    const pull = async () => {
      try {
        const res = await fetch("/api/connectors").then((r) => r.json());
        if (!cancelled && res.ok) {
          setConn(res.connectors as AllConnectors);
        }
      } catch {}
    };
    pull();
    const id = setInterval(pull, 60_000);
    return () => { cancelled = true; clearInterval(id); };
  }, []);

  // Gaya OS scope: all records in unified operating context
  const scoped = records;

  const boulderCount = scoped.filter((r) => r.priority === "boulder").length;
  const highCount = scoped.filter((r) => r.priority === "high").length;
  const projectCount = scoped.filter((r) => r.type === "project").length;
  const refCount = scoped.filter((r) => r.type === "reference").length;
  const winCount = scoped.filter((r) => r.type === "win").length;
  const decisionCount = scoped.filter((r) => r.type === "decision").length;
  const scopedTotal = scoped.length;
  const globalTotal = counts?.total ?? scoped.length;

  const ingested = counts?.lastIngestAt
    ? new Date(counts.lastIngestAt).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })
    : "—";
  const personaLabel = "GAYA // BODHI VANGUARD";
  const empireName = "Gaya OS";

  return (
    <div className="px-6 py-4 max-w-[1600px] mx-auto view">
      {/* Eyebrow */}
      <div className="page-eyebrow mb-2">Council of Gaya Console · Bodhi Vanguard</div>

      {/* Hero prompt */}
      <div className="mb-2">
        <div className="font-mono text-[32px] md:text-[42px] font-bold uppercase tracking-[0.02em] text-os-text caret-blink">
          At your command, R0n
        </div>
      </div>
      <div className="flex items-center gap-3.5 mb-6 flex-wrap font-mono text-xs md:text-sm">
        <span className="text-os-ok font-semibold">▪ {scopedTotal} records</span>
        <span className="text-os-dim">/</span>
        <span className="text-os-dim">{globalTotal} total</span>
        <span className="text-os-dim">·</span>
        <span className="text-os-err font-semibold">▪ {boulderCount} boulder</span>
        <span className="text-os-dim">·</span>
        <span className="text-os-warn font-semibold">▪ {highCount} high</span>
        <span className="text-os-dim">·</span>
        <span className="text-os-accent font-bold">context :: {personaLabel}</span>
        <span className="text-os-dim">·</span>
        <span className="text-os-muted">{activeTasks.length}/60 tasks</span>
        <span className="text-os-dim">·</span>
        <span className="text-os-muted">sync {ingested}</span>
      </div>

      {/* Stat row — Gaya Unified */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <StatCard
          label={`${empireName} Records`}
          value={scopedTotal}
          suffix={`of ${globalTotal}`}
          delta={`${projectCount} projects · ${refCount} refs`}
        />
        <StatCard
          label="Boulder Rules"
          value={boulderCount}
          suffix="/ in scope"
          tone={boulderCount > 0 ? "err" : "default"}
          delta={`+${highCount} high priority`}
        />
        <StatCard
          label="Decisions / Wins"
          value={`${decisionCount} / ${winCount}`}
          suffix="logged"
          delta="Evergrowth & Bodhi Principles"
        />
        <StatCard
          label="Council Specialists"
          value={4}
          suffix="active"
          delta="LOGOS · Bob · Freya · Tvashtar"
        />
      </div>

      {/* Sources strip — Gaya OS */}
      <div className="mb-2"><Label rule>Gaya OS Sources & Live Infrastructure</Label></div>
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2 mb-4">
        <SourceChip
          label="Antigravity Core"
          status={conn?.antigravity?.status === "ok" ? "ok" : "warn"}
          count={conn?.antigravity?.stepIndex ?? 0}
          hint={conn?.antigravity?.state ? conn.antigravity.state.toUpperCase() : "LIVE"}
        />
        <SourceChip
          label="Skills Armory"
          status="ok"
          count={conn?.skillsArmory?.totalSkills ?? 84}
          hint={`${conn?.skillsArmory?.totalSkills ?? 84} Skills`}
        />
        <SourceChip
          label="Mini Gaya Desktop"
          status={conn?.miniGaya?.status ?? "off"}
          count={conn?.miniGaya?.pid ?? 0}
          hint={conn?.miniGaya?.status === "ok" ? `${conn.miniGaya.latencyMs}ms` : "Standby"}
        />
        <SourceChip
          label="Specialist Quad"
          status="ok"
          count={4}
          hint="LOGOS·Bob·Freya·Tvashtar"
        />
        <SourceChip
          label="NVIDIA GPU"
          status={conn?.systemGpu?.status ?? "off"}
          count={conn?.systemGpu?.vramUsagePct ?? 0}
          hint={conn?.systemGpu?.temperatureC ? `${conn.systemGpu.temperatureC}°C` : "RTX 4060"}
        />
        <SourceChip
          label="ComfyUI Studio"
          status={conn?.comfyui?.status === "ok" ? "ok" : "warn"}
          count={conn?.comfyui?.models?.totalCount ?? 15}
          hint={conn?.comfyui?.status === "ok" ? "Listening" : "Port 8188"}
        />
        <SourceChip
          label="MCP Servers"
          status="ok"
          count={conn?.mcpServers?.totalTools ?? 80}
          hint="3 Servers"
        />
      </div>

      {/* Live Integrations Grid HUD */}
      <LiveIntegrationsGrid />

      {/* placeholder for graph section, gets mounted below */}
      <div className="mb-2"><Label rule>Council Graph</Label></div>
    </div>
  );
}

function SourceChip({
  label,
  status,
  count,
  hint,
  tooltip
}: {
  label: string;
  status: "ok" | "warn" | "err" | "off" | "not_configured";
  count: number;
  hint?: string;
  tooltip?: string;
}) {
  const isNotConfigured = status === "not_configured";
  // Map not_configured to visual: dashed border, "off" dot, muted colors
  const dotState = isNotConfigured ? "off" : status;
  const borderStyle = isNotConfigured
    ? "border border-dashed border-os-border-strong"
    : "border border-os-border";

  return (
    <div
      className={`${borderStyle} bg-os-surface px-3 py-2 flex items-center justify-between hoverable`}
      title={tooltip}
    >
      <div className="flex items-center gap-2 min-w-0">
        <Dot state={dotState} pulse={dotState === "ok"} />
        <span
          className={`font-mono text-[11px] truncate ${
            isNotConfigured ? "text-os-dim" : "text-os-text"
          }`}
        >
          {label}
        </span>
      </div>
      <div className="flex items-center gap-1.5 flex-shrink-0">
        {hint && (
          <span
            className={`font-mono text-[9px] uppercase tracking-[0.1em] ${
              isNotConfigured ? "text-os-dim" : "text-os-dim"
            }`}
          >
            {hint}
          </span>
        )}
        {count > 0 && (
          <span className="font-mono text-[10px] text-os-dim">{count}</span>
        )}
      </div>
    </div>
  );
}
