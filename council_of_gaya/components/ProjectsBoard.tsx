"use client";

import { useState } from "react";
import { Dot, Badge } from "./terminal";

export interface ProjectItem {
  id: string;
  name: string;
  codename: string;
  category: "core" | "commercial" | "agent";
  categoryLabel: string;
  status: "live" | "active" | "production" | "engaged";
  statusText: string;
  port?: string;
  leadAgents: Array<{ name: string; role: string; icon: string }>;
  description: string;
  techStack: string[];
  localPath: string;
  repoUrl?: string;
  lastUpdated: string;
  metrics: { [key: string]: string };
}

const PROJECTS: ProjectItem[] = [
  {
    id: "council-of-gaya",
    name: "Council of Gaya",
    codename: "COUNCIL-OPERATOR-OS",
    category: "core",
    categoryLabel: "Core Platform",
    status: "live",
    statusText: "LIVE ON PORT 4200",
    port: "http://localhost:4200",
    leadAgents: [
      { name: "LOGOS", role: "Architecture & QC", icon: "🛡️" },
      { name: "Bob", role: "Fullstack Engine", icon: "🔨" }
    ],
    description: "Executive multi-agent command OS and real-time cockpit. Provides live Antigravity harness telemetry, orbital specialist routing, reactive memory ingestion, and system command deck.",
    techStack: ["Next.js 14", "TypeScript", "Tailwind CSS", "Zustand", "Node.js"],
    localPath: "d:\\Ai_Tools\\antigravity_ai\\council_of_gaya",
    repoUrl: "https://github.com/ronakraval104-sys/Gaya_Agent_PR",
    lastUpdated: "Just now",
    metrics: {
      "Status": "HTTP 200 OK",
      "Nodes": "51 Records",
      "Viewport": "1.5x Laptop Tuned"
    }
  },
  {
    id: "mini-gaya",
    name: "Mini Gaya",
    codename: "DESKTOP-VOICE-PET",
    category: "core",
    categoryLabel: "Core Platform",
    status: "active",
    statusText: "ONLINE ON PORT 8767",
    port: "127.0.0.1:8767",
    leadAgents: [
      { name: "Gaya", role: "Divine Voice", icon: "👑" },
      { name: "Bob", role: "PySide6 Runtime", icon: "🔨" }
    ],
    description: "Interactive desktop sprite and voice companion running on isolated WinSta0 desktop layer. Features CUDA Whisper Turbo STT, Microsoft Heera TTS, animated golden halo, and socket IPC.",
    techStack: ["Python 3.12", "PySide6", "Faster-Whisper CUDA", "SoundDevice", "Windows Tray API"],
    localPath: "d:\\Ai_Tools\\antigravity_ai\\mini_gaya",
    repoUrl: "https://github.com/ronakraval104-sys/Gaya_Agent_PR/tree/master/mini_gaya",
    lastUpdated: "Active Daemon",
    metrics: {
      "TCP Port": "8767 Active",
      "Voice Pipeline": "Heera / Whisper",
      "Controls": "Dual Mute (🎙️/🔊)"
    }
  },
  {
    id: "pixel-quote-max",
    name: "Pixel Quote Max (PQM)",
    codename: "PIXEL-QUOTE-ENGINE",
    category: "commercial",
    categoryLabel: "Commercial Solutions",
    status: "production",
    statusText: "PRODUCTION GRADE",
    leadAgents: [
      { name: "Tvashtar", role: "Calculation Engine", icon: "🦾" },
      { name: "Bob", role: "UI & Export", icon: "🔨" }
    ],
    description: "Commercial LED video wall engineering calculator. Computes exact cabinet configurations, panel pixel pitches, power/cabling loads, GST pricing matrices, and tender-ready client proposals.",
    techStack: ["React", "TypeScript", "Tailwind CSS", "SVG Plan View", "KaTeX Math"],
    localPath: "d:\\Ai_Tools\\antigravity_ai\\pqm",
    lastUpdated: "Production v2.4",
    metrics: {
      "Precision": "100% Zero-Loss",
      "Outputs": "PDF & BOM",
      "Domain": "Commercial LED"
    }
  },
  {
    id: "solidtwin-3d",
    name: "SolidTwin / Visual Rhyme 3D",
    codename: "SOLIDTWIN-SPATIAL-STAGE",
    category: "commercial",
    categoryLabel: "Commercial & 3D",
    status: "active",
    statusText: "SPATIAL ENGINE",
    leadAgents: [
      { name: "Tvashtar", role: "Procedural 3D Math", icon: "🦾" },
      { name: "Freya", role: "Visual Rationale", icon: "🎨" }
    ],
    description: "Procedural curved LED wall array and digital twin stage simulator. Computes non-overlapping edge-to-edge cabinet curvature math, real-time GLSL lighting shaders, and architectural showroom displays.",
    techStack: ["Three.js", "WebGL", "GLSL Shaders", "Parametric Splines", "R3F"],
    localPath: "d:\\Ai_Tools\\antigravity_ai\\solidtwin",
    lastUpdated: "Active Stage",
    metrics: {
      "Geometry": "Parametric Arc",
      "Renderer": "WebGL 2.0",
      "Asset Mode": "CAD / Mesh"
    }
  },
  {
    id: "bodhi-council-mesh",
    name: "Bodhi Vanguard Agent Mesh",
    codename: "MULTI-AGENT-COUNCIL",
    category: "agent",
    categoryLabel: "Autonomous Systems",
    status: "engaged",
    statusText: "REALTIME ENGAGED",
    leadAgents: [
      { name: "LOGOS", role: "Mind & Gate", icon: "🛡️" },
      { name: "Freya", role: "Heart & Taste", icon: "🎨" },
      { name: "Tvashtar", role: "Craft & REA", icon: "🦾" },
      { name: "Bob", role: "Hands & Build", icon: "🔨" }
    ],
    description: "Autonomous multi-agent council protocol with mandatory auto-assigned skills, strict read-only QC review gates, Reverse Engineer Anything (REA) tools, and direct Antigravity execution telemetry.",
    techStack: ["Google Antigravity", "Gemini 2.5 Pro", "REA Protocol", "MCP Tools"],
    localPath: "d:\\Ai_Tools\\antigravity_ai",
    repoUrl: "https://github.com/ronakraval104-sys/Gaya_Agent_PR",
    lastUpdated: "Continuous",
    metrics: {
      "Council Seats": "4 Specialists",
      "Gate Standard": "LOGOS PASS",
      "Auto-Skills": "Enforced"
    }
  },
  {
    id: "agentshield-ecc",
    name: "AgentShield & ECC Security",
    codename: "AGENT-SHIELD-RUNTIME",
    category: "agent",
    categoryLabel: "Security Infrastructure",
    status: "active",
    statusText: "ARMED & SECURE",
    leadAgents: [
      { name: "LOGOS", role: "Security Auditor", icon: "🛡️" },
      { name: "Tvashtar", role: "Boundary Verifier", icon: "🦾" }
    ],
    description: "Active workspace security and prompt injection shield. Scans configurations, MCP servers, shell commands, and environment variables to prevent secret leakage and enforce sandboxed tool execution.",
    techStack: ["Python", "Static Analysis", "Entropy Scanners", "MCP Audit Engine"],
    localPath: "d:\\Ai_Tools\\antigravity_ai\\security",
    lastUpdated: "Armed Status",
    metrics: {
      "Security": "100% SECURE",
      "Secrets Guard": "Zero Leakage",
      "Scan Mode": "Real-time"
    }
  }
];

export function ProjectsBoard() {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const filteredProjects = PROJECTS.filter((p) => {
    const matchesCategory = selectedCategory === "all" || p.category === selectedCategory;
    const matchesSearch =
      searchQuery === "" ||
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.codename.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.techStack.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase())) ||
      p.leadAgents.some((a) => a.name.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const handleCopyPath = (path: string, id: string) => {
    navigator.clipboard?.writeText(path);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="w-full max-w-[1600px] mx-auto px-6 py-8">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-os-border pb-5 mb-6">
        <div>
          <div className="font-mono text-xs uppercase tracking-[0.24em] text-os-accent font-bold mb-1.5 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-os-accent animate-pulse" />
            <span>OPERATIONAL PORTFOLIO // BODHI VANGUARD</span>
          </div>
          <h2 className="font-mono text-2xl md:text-3xl font-bold uppercase tracking-wide text-os-text">
            Our Projects Board
          </h2>
          <p className="font-mono text-sm text-os-dim mt-1">
            Active production repositories, local engineering runtimes, and multi-agent infrastructure.
          </p>
        </div>

        {/* Global Stats Pill Bar */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="px-3.5 py-1.5 border border-os-border bg-os-surface font-mono text-xs text-os-muted">
            <span className="text-os-accent font-bold">6</span> Projects
          </div>
          <div className="px-3.5 py-1.5 border border-os-border bg-os-surface font-mono text-xs text-os-ok">
            <span className="font-bold">2</span> Live Daemons
          </div>
          <div className="px-3.5 py-1.5 border border-os-border bg-os-surface font-mono text-xs text-os-dim">
            <span className="text-os-text font-bold">100%</span> Verified Health
          </div>
        </div>
      </div>

      {/* Control Strip: Filters & Search */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-6">
        {/* Category Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
          {[
            { id: "all", label: "All Projects (6)" },
            { id: "core", label: "Core Platforms (2)" },
            { id: "commercial", label: "Commercial & 3D (2)" },
            { id: "agent", label: "Agent Systems (2)" }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedCategory(tab.id)}
              className={`px-4 py-2 font-mono text-xs uppercase tracking-wider font-semibold border transition-all whitespace-nowrap ${
                selectedCategory === tab.id
                  ? "bg-os-accent text-os-bg border-os-accent shadow-[0_0_12px_rgba(212,175,55,0.3)]"
                  : "bg-os-surface border-os-border text-os-muted hover:text-os-text hover:border-os-border-strong"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search Bar */}
        <div className="w-full sm:w-72 relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter projects, tech, agents..."
            className="w-full bg-os-surface border border-os-border focus:border-os-accent px-3.5 py-2 font-mono text-xs text-os-text placeholder:text-os-dim focus:outline-none transition-colors"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-2.5 top-2.5 font-mono text-xs text-os-dim hover:text-os-text"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredProjects.map((project) => {
          const isLive = project.status === "live";
          const isActive = project.status === "active";
          const isProd = project.status === "production";

          return (
            <div
              key={project.id}
              className="border border-os-border bg-os-surface/80 hover:bg-os-surface hover:border-os-accent/70 transition-all duration-300 p-6 flex flex-col justify-between group shadow-lg relative"
            >
              <div>
                {/* Card Top: Category & Status */}
                <div className="flex items-center justify-between gap-2 mb-3.5">
                  <span className="font-mono text-xs px-2.5 py-0.5 border border-os-border bg-os-bg text-os-dim uppercase tracking-wider">
                    {project.categoryLabel}
                  </span>
                  <div className="flex items-center gap-2">
                    <Dot state={isLive || isActive ? "ok" : isProd ? "warn" : "ok"} pulse={isLive} />
                    <span 
                      className={`font-mono text-xs uppercase tracking-wider font-bold ${
                        isLive ? "text-os-ok" : isActive ? "text-os-accent" : "text-os-warn"
                      }`}
                    >
                      {project.statusText}
                    </span>
                  </div>
                </div>

                {/* Title & Codename */}
                <h3 className="font-mono text-lg font-bold text-os-text group-hover:text-os-accent transition-colors">
                  {project.name}
                </h3>
                <div className="font-mono text-xs text-os-dim uppercase tracking-widest mt-0.5 mb-3">
                  {project.codename}
                </div>

                {/* Description */}
                <p className="font-mono text-sm text-os-muted leading-relaxed mb-5">
                  {project.description}
                </p>

                {/* Lead Agents */}
                <div className="mb-4">
                  <div className="font-mono text-[11px] uppercase tracking-wider text-os-dim mb-1.5">
                    Lead Council Specialists
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    {project.leadAgents.map((agent, i) => (
                      <span
                        key={i}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-os-bg border border-os-border font-mono text-xs text-os-text"
                      >
                        <span>{agent.icon}</span>
                        <span className="font-bold">{agent.name}</span>
                        <span className="text-os-dim text-[11px]">({agent.role})</span>
                      </span>
                    ))}
                  </div>
                </div>

                {/* Tech Stack Pills */}
                <div className="mb-5">
                  <div className="font-mono text-[11px] uppercase tracking-wider text-os-dim mb-1.5">
                    Core Technology Stack
                  </div>
                  <div className="flex items-center gap-1.5 flex-wrap">
                    {project.techStack.map((tech, i) => (
                      <span
                        key={i}
                        className="font-mono text-[11px] px-2 py-0.5 bg-os-surface2 border border-os-border-strong/60 text-os-muted"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Card Footer: Metrics & Action Bar */}
              <div className="border-t border-os-border pt-4 mt-2">
                <div className="grid grid-cols-3 gap-2 mb-4 font-mono text-xs">
                  {Object.entries(project.metrics).map(([key, val], i) => (
                    <div key={i} className="bg-os-bg/70 p-2 border border-os-border">
                      <div className="text-[10px] text-os-dim uppercase truncate">{key}</div>
                      <div className="text-os-text font-bold truncate mt-0.5">{val}</div>
                    </div>
                  ))}
                </div>

                <div className="flex items-center justify-between gap-2">
                  <button
                    type="button"
                    onClick={() => handleCopyPath(project.localPath, project.id)}
                    className="font-mono text-xs px-3 py-1.5 border border-os-border bg-os-bg hover:border-os-accent text-os-dim hover:text-os-text transition-colors flex items-center gap-1.5"
                    title={project.localPath}
                  >
                    <span>{copiedId === project.id ? "✓ Copied" : "📋 Copy Path"}</span>
                  </button>

                  <div className="flex items-center gap-2">
                    {project.port && (
                      <a
                        href={project.port}
                        target="_blank"
                        rel="noreferrer"
                        className="font-mono text-xs px-3.5 py-1.5 border border-os-accent bg-os-accent/15 text-os-accent hover:bg-os-accent hover:text-os-bg font-bold transition-all"
                      >
                        Launch ↗
                      </a>
                    )}
                    {project.repoUrl && (
                      <a
                        href={project.repoUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="font-mono text-xs px-3 py-1.5 border border-os-border bg-os-bg hover:border-os-text text-os-muted hover:text-os-text transition-colors"
                      >
                        GitHub ↗
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
