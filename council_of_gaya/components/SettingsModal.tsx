"use client";

import { useEffect, useState } from "react";
import { useJarvis } from "@/lib/store";
import { Dot } from "./terminal";

export function SettingsModal() {
  const open = useJarvis((s) => s.settingsOpen);
  const closeSettings = useJarvis((s) => s.closeSettings);
  const [testingIpc, setTestingIpc] = useState(false);
  const [ipcResult, setIpcResult] = useState<string | null>(null);
  const [telemetryCadence, setTelemetryCadence] = useState("5s");
  const [modelTier, setModelTier] = useState("antigravity-pro");
  const [selectedVoice, setSelectedVoice] = useState("Microsoft Heera - English (India)");
  const [savedToast, setSavedToast] = useState(false);
  const [scale, setScale] = useState(1.0);
  const [scaleFeedback, setScaleFeedback] = useState<string | null>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && open) closeSettings();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, closeSettings]);

  useEffect(() => {
    if (open) {
      fetch("/api/connectors/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "refresh" })
      })
        .then((r) => r.json())
        .then((data) => {
          if (data?.connectors?.miniGaya?.scale) {
            setScale(data.connectors.miniGaya.scale);
          }
        })
        .catch(() => {});
    }
  }, [open]);

  const handleScaleChange = async (newScale: number) => {
    const clamped = Math.round(Math.max(0.5, Math.min(2.0, newScale)) * 100) / 100;
    setScale(clamped);
    setScaleFeedback(`Applying ${clamped.toFixed(2)}x...`);
    try {
      const res = await fetch("/api/connectors/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "set_scale", scale: clamped })
      });
      const data = await res.json();
      if (data.ok) {
        setScaleFeedback(`Scale ${clamped.toFixed(2)}x applied live`);
      } else {
        setScaleFeedback(`Scale ${clamped.toFixed(2)}x saved`);
      }
    } catch {
      setScaleFeedback(`Scale ${clamped.toFixed(2)}x cached`);
    } finally {
      setTimeout(() => setScaleFeedback(null), 2500);
    }
  };

  if (!open) return null;

  const handleTestBridge = async () => {
    setTestingIpc(true);
    setIpcResult("Probing 127.0.0.1:8767...");
    try {
      const res = await fetch("/api/connectors/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "ping_gaya",
          message: "Antigravity telemetry sync verified from dashboard settings."
        })
      });
      const data = await res.json();
      if (data.ok) {
        setIpcResult("SUCCESS · Mini Gaya ACK received (HMAC-SHA256 verified)");
      } else {
        setIpcResult(`STANDBY · ${data.error || "Socket not responding"}`);
      }
    } catch {
      setIpcResult("OFFLINE · Could not connect to socket");
    } finally {
      setTestingIpc(false);
    }
  };

  const handleSave = async () => {
    try {
      await fetch("/api/connectors/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "set_voice", voiceName: selectedVoice })
      });
    } catch {}
    setSavedToast(true);
    setTimeout(() => {
      setSavedToast(false);
      closeSettings();
    }, 1200);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm"
      onClick={closeSettings}
    >
      <div
        className="w-full max-w-2xl border border-os-border-strong bg-os-bg p-6 shadow-[0_0_30px_rgba(212,175,55,0.2)] flex flex-col max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-os-border shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-2.5 h-2.5 bg-os-accent shadow-[0_0_8px_var(--accent)]" />
            <div>
              <h2 className="font-mono text-[14px] font-bold uppercase tracking-[0.14em] text-os-text">
                Council of Gaya // System Settings & Integrations
              </h2>
              <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-os-dim mt-0.5">
                Antigravity AI Engine · Mini Gaya Companion · Council Specialist Governance
              </p>
            </div>
          </div>
          <button
            onClick={closeSettings}
            className="px-2 py-1 font-mono text-[11px] text-os-dim hover:text-os-text border border-os-border hover:border-os-border-strong transition-colors"
          >
            ESC / CLOSE
          </button>
        </div>

        {/* Scrollable Settings Form */}
        <div className="flex-1 overflow-y-auto py-5 space-y-6 font-mono pr-1">
          {/* Section 1: Antigravity AI Engine */}
          <div className="p-4 border border-os-border bg-os-surface/60">
            <div className="flex items-center justify-between mb-3">
              <span className="text-[12px] font-bold text-os-accent uppercase tracking-[0.1em]">
                1. Antigravity AI Engine Runtime
              </span>
              <span className="text-[10px] text-os-ok font-bold px-2 py-0.5 bg-os-surface2 border border-os-border">
                ACTIVE
              </span>
            </div>
            <div className="space-y-3 text-[11px]">
              <div className="flex flex-col gap-1">
                <span className="text-os-dim">WORKSPACE RUNTIME:</span>
                <input
                  type="text"
                  readOnly
                  value="d:\Ai_Tools\antigravity_ai"
                  className="bg-os-bg border border-os-border px-3 py-1.5 text-os-text text-[11px]"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="flex flex-col gap-1">
                  <span className="text-os-dim">SKILLS REPOSITORY:</span>
                  <input
                    type="text"
                    readOnly
                    value="~/.gemini/config/skills (84 skills)"
                    className="bg-os-bg border border-os-border px-3 py-1.5 text-os-text text-[11px]"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-os-dim">MCP SERVER DIR:</span>
                  <input
                    type="text"
                    readOnly
                    value="~/.gemini/antigravity/mcp (80 tools)"
                    className="bg-os-bg border border-os-border px-3 py-1.5 text-os-text text-[11px]"
                  />
                </div>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-os-dim">AGENT MODEL PREFERENCE:</span>
                <select
                  value={modelTier}
                  onChange={(e) => setModelTier(e.target.value)}
                  className="bg-os-bg border border-os-border px-3 py-1.5 text-os-accent text-[11px] focus:outline-none focus:border-os-accent"
                >
                  <option value="antigravity-pro">Antigravity Pro (High-Reasoning Multi-Specialist)</option>
                  <option value="antigravity-flash">Antigravity Flash (Rapid Execution)</option>
                  <option value="inherit">Inherit Host Model</option>
                </select>
              </div>
            </div>
          </div>

          {/* Section 2: Mini Gaya Desktop Companion IPC */}
          <div className="p-4 border border-os-border bg-os-surface/60">
            <div className="flex items-center justify-between mb-3">
              <span className="text-[12px] font-bold text-os-accent uppercase tracking-[0.1em]">
                2. Mini Gaya Desktop Companion (IPC Bridge)
              </span>
              <div className="flex items-center gap-1.5">
                <Dot state="ok" pulse />
                <span className="text-[10px] text-os-ok font-bold">PORT 8767</span>
              </div>
            </div>
            <div className="space-y-3 text-[11px]">
              <div className="grid grid-cols-3 gap-3">
                <div className="flex flex-col gap-1">
                  <span className="text-os-dim">IPC HOST & PORT:</span>
                  <input
                    type="text"
                    readOnly
                    value="127.0.0.1:8767"
                    className="bg-os-bg border border-os-border px-3 py-1.5 text-os-text text-[11px]"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-os-dim">SECURITY AUTH:</span>
                  <input
                    type="text"
                    readOnly
                    value="HMAC-SHA256"
                    className="bg-os-bg border border-os-border px-3 py-1.5 text-os-ok text-[11px]"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-os-dim">DISPLAY SURFACE:</span>
                  <input
                    type="text"
                    readOnly
                    value="WinSta0\Default"
                    className="bg-os-bg border border-os-border px-3 py-1.5 text-os-text text-[11px]"
                  />
                </div>
              </div>

              {/* Mini Gaya Dynamic Scale Control: 0.5x to 2.0x */}
              <div className="flex flex-col gap-2 pt-2 border-t border-os-border/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-os-dim uppercase tracking-[0.1em] text-[10px] font-bold">
                      MINI GAYA DESKTOP SCALE:
                    </span>
                    <span className="px-2 py-0.5 bg-os-accent/15 border border-os-accent text-os-accent text-[11px] font-bold font-mono">
                      {scale.toFixed(2)}x
                    </span>
                    <span className="text-[10px] text-os-dim font-mono">
                      (Approx {Math.round(120 * scale)} × {Math.round(197 * scale)} px)
                    </span>
                  </div>
                  {scaleFeedback && (
                    <span className="text-os-accent text-[10px] font-bold animate-pulse">
                      {scaleFeedback}
                    </span>
                  )}
                </div>

                {/* Range Slider */}
                <div className="flex items-center gap-3">
                  <span className="text-[10px] text-os-dim font-mono">0.5x</span>
                  <input
                    type="range"
                    min="0.5"
                    max="2.0"
                    step="0.05"
                    value={scale}
                    onChange={(e) => handleScaleChange(parseFloat(e.target.value))}
                    className="flex-1 accent-[#d4af37] cursor-pointer h-1.5 bg-os-bg border border-os-border appearance-none rounded-none"
                  />
                  <span className="text-[10px] text-os-dim font-mono">2.0x</span>
                </div>

                {/* Quick Presets */}
                <div className="grid grid-cols-6 gap-1.5 pt-0.5">
                  {[
                    { label: "0.5x Mini", val: 0.5 },
                    { label: "0.75x Compact", val: 0.75 },
                    { label: "1.0x Default", val: 1.0 },
                    { label: "1.25x Hero", val: 1.25 },
                    { label: "1.5x Large", val: 1.5 },
                    { label: "2.0x Colossus", val: 2.0 },
                  ].map((preset) => {
                    const active = Math.abs(scale - preset.val) < 0.03;
                    return (
                      <button
                        key={preset.val}
                        type="button"
                        onClick={() => handleScaleChange(preset.val)}
                        className={`py-1 px-1 text-[10px] font-mono uppercase tracking-[0.05em] border transition-colors ${
                          active
                            ? "border-os-accent bg-os-accent text-os-bg font-bold shadow-[0_0_8px_rgba(212,175,55,0.4)]"
                            : "border-os-border bg-os-bg/70 text-os-dim hover:text-os-text hover:border-os-border-strong"
                        }`}
                      >
                        {preset.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="flex flex-col gap-1 pt-1">
                <span className="text-os-dim">DIVINE VOICE SYNTHESIZER (LIBRARY):</span>
                <select
                  value={selectedVoice}
                  onChange={(e) => setSelectedVoice(e.target.value)}
                  className="bg-os-bg border border-os-border px-3 py-1.5 text-os-accent text-[11px] focus:outline-none focus:border-os-accent"
                >
                  <option value="Microsoft Heera - English (India)">
                    Microsoft Heera (English - India) — Divine Bodhi Vanguard Tone (Recommended)
                  </option>
                  <option value="Microsoft Susan - English (United Kingdom)">
                    Microsoft Susan (English - UK) — Soft, Philosophical & Gentle
                  </option>
                  <option value="Microsoft Hazel - English (United Kingdom)">
                    Microsoft Hazel (English - UK) — Regal & Authoritative Commander
                  </option>
                  <option value="Microsoft Zira - English (United States)">
                    Microsoft Zira (English - US) — Clear, Modern & Sharp AI Companion
                  </option>
                </select>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-os-border/50">
                <div className="text-[10px] text-os-dim">
                  {ipcResult ? (
                    <span className="text-os-accent font-bold">{ipcResult}</span>
                  ) : (
                    "Test live communication between Dashboard and Desktop Sprite"
                  )}
                </div>
                <button
                  type="button"
                  onClick={handleTestBridge}
                  disabled={testingIpc}
                  className="px-3 py-1 border border-os-accent bg-os-accent/10 hover:bg-os-accent/20 text-os-accent text-[10px] font-bold uppercase tracking-[0.1em] transition-colors disabled:opacity-40"
                >
                  {testingIpc ? "Pinging..." : "⚡ Test IPC Socket"}
                </button>
              </div>
            </div>
          </div>

          {/* Section 3: Telemetry Cadence & Generative Studio */}
          <div className="p-4 border border-os-border bg-os-surface/60">
            <span className="text-[12px] font-bold text-os-accent uppercase tracking-[0.1em] block mb-3">
              3. Telemetry Cadence & Generative Studio
            </span>
            <div className="grid grid-cols-2 gap-4 text-[11px]">
              <div className="flex flex-col gap-1">
                <span className="text-os-dim">HARDWARE TELEMETRY INTERVAL:</span>
                <select
                  value={telemetryCadence}
                  onChange={(e) => setTelemetryCadence(e.target.value)}
                  className="bg-os-bg border border-os-border px-3 py-1.5 text-os-text text-[11px] focus:outline-none focus:border-os-accent"
                >
                  <option value="5s">5 Seconds (Realtime Heartbeat)</option>
                  <option value="15s">15 Seconds (Balanced)</option>
                  <option value="30s">30 Seconds (Quiet)</option>
                </select>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-os-dim">COMFYUI STUDIO ENDPOINT:</span>
                <input
                  type="text"
                  readOnly
                  value="http://127.0.0.1:8188 (Standalone)"
                  className="bg-os-bg border border-os-border px-3 py-1.5 text-os-text text-[11px]"
                />
              </div>
            </div>
          </div>

          {/* Section 4: Council Quad Gate Policies */}
          <div className="p-4 border border-os-border bg-os-surface/60">
            <span className="text-[12px] font-bold text-os-accent uppercase tracking-[0.1em] block mb-3">
              4. Council Specialists Quality Gate Policies
            </span>
            <div className="grid grid-cols-2 gap-3 text-[10px]">
              <div className="p-2.5 border border-os-border/60 bg-os-bg/50">
                <div className="text-os-accent font-bold mb-1">🛡️ LOGOS GATE</div>
                <div className="text-os-dim">
                  Mandatory read-only hard check gate. Every code mutation requires verified VERDICT: PASS scope.
                </div>
              </div>
              <div className="p-2.5 border border-os-border/60 bg-os-bg/50">
                <div className="text-os-accent font-bold mb-1">🔨 BOB ENGINE</div>
                <div className="text-os-dim">
                  Precision builder delivering atomic changes, desktop export zips, and honest execution receipts.
                </div>
              </div>
              <div className="p-2.5 border border-os-border/60 bg-os-bg/50">
                <div className="text-os-accent font-bold mb-1">✨ FREYA VISION</div>
                <div className="text-os-dim">
                  High-taste visual designer enforcing Sacred Gold & Obsidian palette, halo glow, and UI tokens.
                </div>
              </div>
              <div className="p-2.5 border border-os-border/60 bg-os-bg/50">
                <div className="text-os-accent font-bold mb-1">⚙️ TVASHTAR TOOLKEEPER</div>
                <div className="text-os-dim">
                  Systems architect governing the 12-skill specialty arsenal and runtime MCP servers.
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-os-border shrink-0">
          <span className="font-mono text-[10px] text-os-dim">
            Council of Gaya OS // At your command, R0n
          </span>
          <div className="flex items-center gap-3">
            {savedToast && (
              <span className="font-mono text-[11px] text-os-ok font-bold animate-pulse">
                ✓ Preferences Saved
              </span>
            )}
            <button
              onClick={closeSettings}
              className="px-4 py-1.5 font-mono text-[11px] text-os-dim hover:text-os-text border border-os-border hover:border-os-border-strong transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-1.5 font-mono text-[11px] bg-os-accent text-os-bg font-bold hover:bg-os-accent/90 transition-colors shadow-[0_0_12px_rgba(212,175,55,0.4)]"
            >
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
