import net from "node:net";
import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import crypto from "node:crypto";
import { exec } from "node:child_process";
import { promisify } from "node:util";

const execAsync = promisify(exec);

export interface MiniGayaStatus {
  status: "ok" | "err" | "off";
  port: number;
  latencyMs: number;
  pid?: number;
  scale?: number;
  windowCount?: number;
  fetchedAt: number;
  error?: string;
}

const PORT = 8767;
const HOST = "127.0.0.1";
const CONNECT_TIMEOUT_MS = 600;
const CACHE_TTL_MS = 3_000;

let cachedStatus: { at: number; value: MiniGayaStatus } | null = null;
let cachedPid: { at: number; pid: number } | null = null;

async function getRunningPid(): Promise<number | undefined> {
  if (cachedPid && Date.now() - cachedPid.at < 15_000) {
    return cachedPid.pid;
  }
  try {
    const { stdout } = await execAsync(
      `powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort ${PORT} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1"`
    );
    const pid = parseInt(stdout.trim(), 10);
    if (!isNaN(pid) && pid > 0) {
      cachedPid = { at: Date.now(), pid };
      return pid;
    }
  } catch {}
  return undefined;
}

export async function getMiniGayaStatus(): Promise<MiniGayaStatus> {
  if (cachedStatus && Date.now() - cachedStatus.at < CACHE_TTL_MS) {
    return cachedStatus.value;
  }

  const t0 = Date.now();

  const pingResult = await new Promise<{ ok: boolean; latencyMs: number; error?: string }>((resolve) => {
    let resolved = false;
    const socket = net.createConnection({ host: HOST, port: PORT, timeout: CONNECT_TIMEOUT_MS }, () => {
      if (!resolved) {
        resolved = true;
        const latencyMs = Date.now() - t0;
        socket.destroy();
        resolve({ ok: true, latencyMs });
      }
    });

    socket.on("timeout", () => {
      if (!resolved) {
        resolved = true;
        socket.destroy();
        resolve({ ok: false, latencyMs: Date.now() - t0, error: "connection timeout" });
      }
    });

    socket.on("error", (err) => {
      if (!resolved) {
        resolved = true;
        resolve({ ok: false, latencyMs: Date.now() - t0, error: err.message });
      }
    });
  });

  let pid: number | undefined;
  if (pingResult.ok) {
    pid = await getRunningPid();
  }

  let scale = 1.0;
  try {
    const prefsPath = path.join(os.homedir(), ".gaya", "sprite.json");
    const prefsRaw = await fs.readFile(prefsPath, "utf-8");
    const prefs = JSON.parse(prefsRaw);
    if (typeof prefs.scale === "number") scale = prefs.scale;
  } catch {}

  const result: MiniGayaStatus = {
    status: pingResult.ok ? "ok" : "off",
    port: PORT,
    latencyMs: pingResult.ok ? pingResult.latencyMs : 0,
    pid,
    scale,
    fetchedAt: Date.now(),
    error: pingResult.error
  };

  cachedStatus = { at: Date.now(), value: result };
  return result;
}

/**
 * Dispatch an authentic notification to Mini Gaya desktop sprite using HMAC authentication.
 */
export async function sendMiniGayaNotification(message: string): Promise<{ ok: boolean; error?: string }> {
  try {
    const keyFile = path.join(os.homedir(), ".gaya", "secrets", "sprite.key");
    const key = (await fs.readFile(keyFile, "utf-8")).trim();
    const rid = crypto.randomUUID().replace(/-/g, "");

    function sig(...parts: string[]) {
      return crypto.createHmac("sha256", key).update(parts.join("|")).digest("hex");
    }

    return await new Promise((resolve) => {
      const socket = net.createConnection({ host: HOST, port: PORT, timeout: 2000 }, () => {
        // Step 1: Handshake hello
        const helloMsg = JSON.stringify({ hello: rid, auth: sig("hook", rid) }) + "\n";
        socket.write(helloMsg);
      });

      let buf = "";
      socket.on("data", (data) => {
        buf += data.toString();
        const lines = buf.split("\n");
        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i].trim();
          if (!line) continue;
          try {
            const parsed = JSON.parse(line);
            if (parsed.ready) {
              // Sprite is ready, send notification payload
              const payload = {
                event: "Notification",
                payload: {
                  hook_event_name: "Notification",
                  message: message
                },
                truncated: false,
                sizes: {}
              };
              socket.write(JSON.stringify(payload) + "\n");
              socket.end();
              resolve({ ok: true });
              return;
            }
          } catch {}
        }
      });

      socket.on("error", (err) => resolve({ ok: false, error: err.message }));
      socket.on("timeout", () => {
        socket.destroy();
        resolve({ ok: false, error: "timeout" });
      });
    });
  } catch (err: any) {
    return { ok: false, error: err.message };
  }
}

/**
 * Dynamically resize Mini Gaya desktop sprite across 0.5x to 2.0x scale.
 */
export async function setMiniGayaScale(scale: number): Promise<{ ok: boolean; scale?: number; error?: string }> {
  const clamped = Math.max(0.5, Math.min(2.0, Math.round((Number(scale) || 1.0) * 100) / 100));

  // 1. Immediately persist to ~/.gaya/sprite.json as reliable local state
  try {
    const prefsPath = path.join(os.homedir(), ".gaya", "sprite.json");
    let prefs: Record<string, any> = {};
    try {
      prefs = JSON.parse(await fs.readFile(prefsPath, "utf-8"));
    } catch {}
    prefs.scale = clamped;
    await fs.writeFile(prefsPath, JSON.stringify(prefs, null, 2), "utf-8");
  } catch {}

  // 2. Dispatch real-time HMAC packet to live Mini Gaya sprite socket
  try {
    const keyFile = path.join(os.homedir(), ".gaya", "secrets", "sprite.key");
    const key = (await fs.readFile(keyFile, "utf-8")).trim();
    const rid = crypto.randomUUID().replace(/-/g, "");

    function sig(...parts: string[]) {
      return crypto.createHmac("sha256", key).update(parts.join("|")).digest("hex");
    }

    return await new Promise((resolve) => {
      const socket = net.createConnection({ host: HOST, port: PORT, timeout: 2000 }, () => {
        const helloMsg = JSON.stringify({ hello: rid, auth: sig("hook", rid) }) + "\n";
        socket.write(helloMsg);
      });

      let buf = "";
      socket.on("data", (data) => {
        buf += data.toString();
        const lines = buf.split("\n");
        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i].trim();
          if (!line) continue;
          try {
            const parsed = JSON.parse(line);
            if (parsed.ready) {
              const payload = {
                event: "SetScale",
                payload: { scale: clamped },
                truncated: false,
                sizes: {}
              };
              socket.write(JSON.stringify(payload) + "\n");
            } else if (parsed.ok) {
              socket.destroy();
              resolve({ ok: true, scale: parsed.scale ?? clamped });
              return;
            }
          } catch {}
        }
      });

      socket.on("error", (err) => {
        // Preference was already persisted to disk
        resolve({ ok: true, scale: clamped, error: `Saved to prefs (live socket: ${err.message})` });
      });
      socket.on("timeout", () => {
        socket.destroy();
        resolve({ ok: true, scale: clamped, error: "Saved to prefs (socket timeout)" });
      });
    });
  } catch (err: any) {
    return { ok: true, scale: clamped, error: err.message };
  }
}
