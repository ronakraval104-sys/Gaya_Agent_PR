"use client";

import { useEffect, useRef } from "react";
import { useGaya } from "@/lib/store";

/**
 * Ambient particle field — ~200 particles drifting in the void.
 * When JARVIS is "thinking" (activeTasks > 0), particles orient toward center.
 * Canvas 2D for reliability across GPUs. Opacity capped at 8%.
 */
export function ParticleField() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const activeCount = useGaya((s) => s.activeTasks.length);
  const activeRef = useRef(activeCount);
  activeRef.current = activeCount;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let raf = 0;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    const resize = () => {
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      canvas.style.width = window.innerWidth + "px";
      canvas.style.height = window.innerHeight + "px";
      ctx.scale(dpr, dpr);
    };
    resize();
    window.addEventListener("resize", resize);

    const N = 180;
    const particles = Array.from({ length: N }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      vx: (Math.random() - 0.5) * 0.15,
      vy: (Math.random() - 0.5) * 0.15,
      r: 0.6 + Math.random() * 1.4
    }));

    const draw = () => {
      const w = window.innerWidth;
      const h = window.innerHeight;
      const cx = w / 2;
      const cy = h / 2;
      const pull = activeRef.current > 0 ? 0.0008 * activeRef.current : 0;

      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "rgba(79, 227, 255, 0.06)";
      for (const p of particles) {
        if (pull > 0) {
          const dx = cx - p.x;
          const dy = cy - p.y;
          p.vx += dx * pull;
          p.vy += dy * pull;
        }
        // gentle damping
        p.vx *= 0.985;
        p.vy *= 0.985;
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0) p.x = w;
        if (p.x > w) p.x = 0;
        if (p.y < 0) p.y = h;
        if (p.y > h) p.y = 0;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      }
      raf = requestAnimationFrame(draw);
    };
    raf = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 1, opacity: 0.6 }}
      aria-hidden
    />
  );
}
