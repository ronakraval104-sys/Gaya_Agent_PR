"use client";

import { useEffect, useState } from "react";
import { Dot } from "./terminal";

export function GayaCompanionDeck() {
  const [scale, setScale] = useState(1.0);
  const [volume, setVolume] = useState(100);
  const [voice, setVoice] = useState("Piper Neural (Amy - Ultra Natural)");
  const [speakerMuted, setSpeakerMuted] = useState(false);
  const [micMuted, setMicMuted] = useState(false);
  const [status, setStatus] = useState<"ok" | "off">("ok");
  const [feedback, setFeedback] = useState<string | null>(null);
  const [testingVoice, setTestingVoice] = useState(false);

  // Poll current settings on mount
  useEffect(() => {
    fetch("/api/connectors/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "refresh" })
    })
      .then((r) => r.json())
      .then((data) => {
        if (data?.connectors?.miniGaya) {
          const mg = data.connectors.miniGaya;
          setStatus(mg.status === "ok" ? "ok" : "off");
          if (typeof mg.scale === "number") setScale(mg.scale);
        }
      })
      .catch(() => {});
  }, []);

  const handleScaleChange = async (newScale: number) => {
    const clamped = Math.round(Math.max(0.5, Math.min(2.0, newScale)) * 100) / 100;
    setScale(clamped);
    setFeedback(`Scale: ${clamped.toFixed(2)}x`);
    try {
      await fetch("/api/connectors/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "set_scale", scale: clamped })
      });
    } catch {}
    setTimeout(() => setFeedback(null), 2000);
  };

  const handleVolumeChange = async (newVol: number) => {
    const clamped = Math.max(0, Math.min(100, Math.round(newVol)));
    setVolume(clamped);
    setFeedback(`Audio Volume: ${clamped}%`);
    try {
      await fetch("/api/connectors/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "set_volume", volume: clamped })
      });
    } catch {}
    setTimeout(() => setFeedback(null), 2000);
  };

  const handleVoiceChange = async (newVoice: string) => {
    setVoice(newVoice);
    setFeedback(`Voice: ${newVoice.split("(")[0].trim()}`);
    try {
      await fetch("/api/connectors/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "set_voice", voiceName: newVoice })
      });
    } catch {}
    setTimeout(() => setFeedback(null), 2000);
  };

  const handleTestVoice = async () => {
    setTestingVoice(true);
    setFeedback("Synthesizing audio test...");
    try {
      await fetch("/api/connectors/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "ping_gaya",
          message: "Greetings R0n. Divine Bodhi voice synthesis is live at full fidelity."
        })
      });
      setFeedback("Audio dispatched to Mini Gaya");
    } catch {
      setFeedback("Socket ping failed");
    } finally {
      setTestingVoice(false);
      setTimeout(() => setFeedback(null), 2500);
    }
  };

  return (
    <div className="w-full max-w-[1600px] mx-auto px-6 py-4">
      <div className="border border-os-border-strong bg-os-surface/90 backdrop-blur-md p-5 shadow-xl relative overflow-hidden">
        {/* Header Strip */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-os-border pb-3 mb-4">
          <div className="flex items-center gap-2.5">
            <span className="text-xl">🎙️</span>
            <div>
              <div className="font-mono text-sm font-bold uppercase tracking-wider text-os-text flex items-center gap-2">
                <span>Mini Gaya Companion Deck</span>
                <span className="text-xs px-2 py-0.5 border border-os-accent/40 bg-os-accent/10 text-os-accent">
                  AUDIO & SCALE MATRIX
                </span>
              </div>
              <div className="font-mono text-xs text-os-dim mt-0.5">
                Real-time local socket tuning on port 8767 · Zero latency IPC
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {feedback && (
              <span className="font-mono text-xs text-os-accent font-bold animate-pulse">
                {feedback}
              </span>
            )}
            <div className="flex items-center gap-2 px-3 py-1 border border-os-border bg-os-bg font-mono text-xs">
              <Dot state={status} pulse={status === "ok"} />
              <span className={status === "ok" ? "text-os-ok font-bold" : "text-os-dim"}>
                {status === "ok" ? "127.0.0.1:8767 CONNECTED" : "OFFLINE"}
              </span>
            </div>
          </div>
        </div>

        {/* Controls Grid: Scale, Volume, Voice & Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* 1. Response Audio Volume Slider */}
          <div className="flex flex-col justify-between bg-os-bg/60 p-4 border border-os-border">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5 font-mono text-xs font-bold uppercase tracking-wider text-os-text">
                <span>{volume === 0 ? "🔇" : volume < 50 ? "🔉" : "🔊"}</span>
                <span>Response Volume</span>
              </div>
              <span className="font-mono text-sm font-bold text-os-accent px-2 py-0.5 bg-os-surface border border-os-border">
                {volume}%
              </span>
            </div>

            <div className="flex items-center gap-3 my-2">
              <span className="font-mono text-xs text-os-dim">0%</span>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={volume}
                onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                className="flex-1 accent-[#d4af37] cursor-pointer h-2 bg-os-surface border border-os-border appearance-none rounded-none"
              />
              <span className="font-mono text-xs text-os-dim">100%</span>
            </div>

            <div className="flex items-center justify-between gap-1 pt-1">
              {[
                { label: "Mute", val: 0 },
                { label: "30%", val: 30 },
                { label: "50%", val: 50 },
                { label: "80%", val: 80 },
                { label: "100%", val: 100 }
              ].map((p) => (
                <button
                  key={p.val}
                  type="button"
                  onClick={() => handleVolumeChange(p.val)}
                  className={`flex-1 py-1 font-mono text-[11px] border transition-colors ${
                    volume === p.val
                      ? "border-os-accent bg-os-accent text-os-bg font-bold"
                      : "border-os-border bg-os-surface text-os-dim hover:text-os-text"
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* 2. Mini Gaya Desktop Scale Slider */}
          <div className="flex flex-col justify-between bg-os-bg/60 p-4 border border-os-border">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5 font-mono text-xs font-bold uppercase tracking-wider text-os-text">
                <span>📏</span>
                <span>Desktop Sprite Scale</span>
              </div>
              <span className="font-mono text-sm font-bold text-os-accent px-2 py-0.5 bg-os-surface border border-os-border">
                {scale.toFixed(2)}x
              </span>
            </div>

            <div className="flex items-center gap-3 my-2">
              <span className="font-mono text-xs text-os-dim">0.5x</span>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.05"
                value={scale}
                onChange={(e) => handleScaleChange(parseFloat(e.target.value))}
                className="flex-1 accent-[#d4af37] cursor-pointer h-2 bg-os-surface border border-os-border appearance-none rounded-none"
              />
              <span className="font-mono text-xs text-os-dim">2.0x</span>
            </div>

            <div className="flex items-center justify-between gap-1 pt-1">
              {[
                { label: "0.5x", val: 0.5 },
                { label: "0.75x", val: 0.75 },
                { label: "1.0x", val: 1.0 },
                { label: "1.25x", val: 1.25 },
                { label: "1.5x", val: 1.5 },
                { label: "2.0x", val: 2.0 }
              ].map((p) => (
                <button
                  key={p.val}
                  type="button"
                  onClick={() => handleScaleChange(p.val)}
                  className={`flex-1 py-1 font-mono text-[11px] border transition-colors ${
                    Math.abs(scale - p.val) < 0.03
                      ? "border-os-accent bg-os-accent text-os-bg font-bold"
                      : "border-os-border bg-os-surface text-os-dim hover:text-os-text"
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* 3. Natural TTS Voice Synthesizer & Dual Mute Controls */}
          <div className="flex flex-col justify-between bg-os-bg/60 p-4 border border-os-border">
            <div className="mb-2">
              <div className="font-mono text-xs font-bold uppercase tracking-wider text-os-text mb-1 flex items-center justify-between">
                <span>Divine Voice Synthesizer</span>
                <span className="text-[10px] text-os-ok font-semibold">NEURAL READY</span>
              </div>
              <select
                value={voice}
                onChange={(e) => handleVoiceChange(e.target.value)}
                className="w-full bg-os-surface border border-os-border focus:border-os-accent px-3 py-1.5 font-mono text-xs text-os-accent focus:outline-none transition-colors"
              >
                <option value="Piper Neural (Amy - Ultra Natural)">
                  ⭐ Piper Neural (Amy) — Ultra-Natural Human Tone (Recommended)
                </option>
                <option value="Microsoft Heera - English (India)">
                  Microsoft Heera (English - India) — Sacred Gold OneCore
                </option>
                <option value="Microsoft Susan - English (United Kingdom)">
                  Microsoft Susan (English - UK) — Philosophical & Soft
                </option>
                <option value="Microsoft Hazel - English (United Kingdom)">
                  Microsoft Hazel (English - UK) — Regal Commander
                </option>
                <option value="Microsoft Zira - English (United States)">
                  Microsoft Zira (English - US) — Modern & Articulate
                </option>
              </select>
            </div>

            <div className="flex items-center gap-2 pt-2 border-t border-os-border/50">
              <button
                type="button"
                onClick={() => setSpeakerMuted(!speakerMuted)}
                className={`flex-1 py-1.5 px-2 font-mono text-xs border flex items-center justify-center gap-1.5 transition-colors ${
                  speakerMuted 
                    ? "border-os-err bg-os-err/15 text-os-err font-bold" 
                    : "border-os-border bg-os-surface text-os-muted hover:text-os-text"
                }`}
              >
                <span>{speakerMuted ? "🔇" : "🔊"}</span>
                <span>{speakerMuted ? "Speaker Muted" : "Speaker Active"}</span>
              </button>

              <button
                type="button"
                onClick={() => setMicMuted(!micMuted)}
                className={`flex-1 py-1.5 px-2 font-mono text-xs border flex items-center justify-center gap-1.5 transition-colors ${
                  micMuted 
                    ? "border-os-err bg-os-err/15 text-os-err font-bold" 
                    : "border-os-border bg-os-surface text-os-muted hover:text-os-text"
                }`}
              >
                <span>{micMuted ? "🚫🎙️" : "🎙️"}</span>
                <span>{micMuted ? "Mic Muted" : "Mic Active"}</span>
              </button>

              <button
                type="button"
                onClick={handleTestVoice}
                disabled={testingVoice}
                className="py-1.5 px-3 border border-os-accent bg-os-accent/15 hover:bg-os-accent hover:text-os-bg text-os-accent font-mono text-xs font-bold transition-all disabled:opacity-40"
                title="Send test audio phrase to Mini Gaya"
              >
                {testingVoice ? "..." : "▶ Test"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
