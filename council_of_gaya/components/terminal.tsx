/**
 * MONOLITH SIGNAL primitives — the atoms every screen composes from.
 * Direct adaptation of FounderOS `components/terminal.tsx`.
 * Server-component friendly: no state, no handlers.
 */

import * as React from "react";

export type DotState = "ok" | "warn" | "err" | "off";

const DOT_FOR: Record<string, DotState> = {
  connected: "ok",
  active: "ok",
  ok: "ok",
  live: "ok",
  available: "warn",
  warn: "warn",
  degraded: "warn",
  high: "warn",
  idle: "warn",
  error: "err",
  fail: "err",
  boulder: "err",
  not_configured: "off",
  planned: "off",
  off: "off"
};

export function dotState(state: string): DotState {
  return DOT_FOR[state] ?? "off";
}

export function Dot({ state, pulse = false }: { state: string; pulse?: boolean }) {
  const cls = dotState(state);
  return <span className={`dot ${cls}${pulse && cls === "ok" ? " pulse" : ""}`} />;
}

export type BadgeTone = "default" | "accent" | "ok" | "warn" | "err";

const BADGE_TONE: Record<BadgeTone, string> = {
  default: "border-os-border-strong text-os-muted",
  accent:
    "border-[var(--accent-line)] bg-[var(--accent-soft)] text-os-accent",
  ok:
    "border-[color-mix(in_oklab,var(--ok)_35%,transparent)] bg-[color-mix(in_oklab,var(--ok)_9%,transparent)] text-os-ok",
  warn:
    "border-[color-mix(in_oklab,var(--warn)_35%,transparent)] bg-[color-mix(in_oklab,var(--warn)_9%,transparent)] text-os-warn",
  err:
    "border-[color-mix(in_oklab,var(--err)_35%,transparent)] bg-[color-mix(in_oklab,var(--err)_9%,transparent)] text-os-err"
};

export function Badge({
  tone = "default",
  ghost = false,
  children
}: {
  tone?: BadgeTone;
  ghost?: boolean;
  children: React.ReactNode;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 whitespace-nowrap border px-2.5 py-1 font-mono text-xs uppercase tracking-[0.14em] ${BADGE_TONE[tone]} ${
        ghost ? "border-dashed" : ""
      }`}
    >
      {children}
    </span>
  );
}

/** Mono section label: `LABEL  count ————` */
export function Label({
  children,
  count,
  rule = false
}: {
  children: React.ReactNode;
  count?: string | number;
  rule?: boolean;
}) {
  return (
    <div className="flex items-center gap-2.5 font-mono text-xs font-bold uppercase tracking-[0.24em] text-os-dim">
      <span className="whitespace-nowrap">{children}</span>
      {count != null && <span className="text-os-muted">{count}</span>}
      {rule && <span className="h-px flex-1 bg-os-border" />}
    </div>
  );
}

export function SectionHead({
  label,
  count,
  link,
  href
}: {
  label: string;
  count?: string | number;
  link?: string;
  href?: string;
}) {
  return (
    <div className="mb-3 flex items-baseline justify-between gap-3">
      <div className="min-w-0 flex-1">
        <Label count={count} rule>
          {label}
        </Label>
      </div>
      {link && href && (
        <a
          href={href}
          className="shrink-0 font-mono text-[11px] text-os-dim transition-colors hover:text-os-accent"
        >
          {link} →
        </a>
      )}
    </div>
  );
}

export function Kbd({ children }: { children: React.ReactNode }) {
  return (
    <kbd className="border border-os-border-strong border-b-2 bg-os-surface2 px-1.5 py-0.5 font-mono text-[10px] text-os-muted">
      {children}
    </kbd>
  );
}

/** Accent sparkline with a 10%-opacity fill. */
export function Spark({ data, w = 72, h = 22 }: { data: number[]; w?: number; h?: number }) {
  if (data.length < 2) return null;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const pts = data.map(
    (v, i) =>
      `${((i / (data.length - 1)) * w).toFixed(1)},${(h - 2 - ((v - min) / range) * (h - 5)).toFixed(1)}`
  );
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} aria-hidden>
      <polygon points={`0,${h} ${pts.join(" ")} ${w},${h}`} fill="var(--accent)" opacity="0.1" />
      <polyline points={pts.join(" ")} fill="none" stroke="var(--accent)" strokeWidth="1.5" />
    </svg>
  );
}

/** StatCard — big mono number + label + optional delta + optional sparkline */
export function StatCard({
  label,
  value,
  suffix,
  delta,
  spark,
  tone = "default"
}: {
  label: string;
  value: string | number;
  suffix?: string;
  delta?: string;
  spark?: number[];
  tone?: BadgeTone;
}) {
  const toneColor =
    tone === "ok" ? "text-os-ok"
    : tone === "warn" ? "text-os-warn"
    : tone === "err" ? "text-os-err"
    : "text-os-text";
  return (
    <div className="border border-os-border bg-os-surface p-5 hoverable">
      <div className="mb-3.5">
        <Label>{label}</Label>
      </div>
      <div className="flex items-end justify-between gap-3">
        <div className="flex items-baseline gap-2.5">
          <span className={`font-mono text-[34px] leading-none font-bold ${toneColor}`}>
            {value}
          </span>
          {suffix && (
            <span className="font-mono text-xs text-os-muted">{suffix}</span>
          )}
        </div>
        {spark && <Spark data={spark} />}
      </div>
      {delta && (
        <div className="mt-2.5 font-mono text-xs uppercase tracking-[0.16em] text-os-muted">
          {delta}
        </div>
      )}
    </div>
  );
}
