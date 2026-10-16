import { exec } from "node:child_process";
import { promisify } from "node:util";
import os from "node:os";

const execAsync = promisify(exec);

export interface GpuStatus {
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
  fetchedAt: number;
  error?: string;
}

const CACHE_TTL_MS = 4_000;
let cachedGpu: { at: number; value: GpuStatus } | null = null;

export async function getGpuStatus(): Promise<GpuStatus> {
  if (cachedGpu && Date.now() - cachedGpu.at < CACHE_TTL_MS) {
    return cachedGpu.value;
  }

  const hostTotalRamMb = Math.round(os.totalmem() / (1024 * 1024));
  const hostFreeRamMb = Math.round(os.freemem() / (1024 * 1024));
  const hostUsedRamMb = hostTotalRamMb - hostFreeRamMb;
  const hostRamUsagePct = Math.round((hostUsedRamMb / hostTotalRamMb) * 100);

  try {
    const { stdout } = await execAsync(
      "nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu --format=csv,noheader,nounits",
      { timeout: 3000 }
    );
    const line = stdout.trim().split("\n")[0];
    if (!line) {
      throw new Error("No output from nvidia-smi");
    }

    const parts = line.split(",").map((s) => s.trim());
    const gpuName = parts[0] || "NVIDIA GPU";
    const totalVramMb = parseInt(parts[1], 10) || 0;
    const usedVramMb = parseInt(parts[2], 10) || 0;
    const freeVramMb = parseInt(parts[3], 10) || 0;
    const temperatureC = parseInt(parts[4], 10) || 0;
    const utilizationPct = parseInt(parts[5], 10) || 0;
    const vramUsagePct = totalVramMb > 0 ? Math.round((usedVramMb / totalVramMb) * 100) : 0;

    const result: GpuStatus = {
      status: "ok",
      gpuName,
      totalVramMb,
      usedVramMb,
      freeVramMb,
      vramUsagePct,
      temperatureC,
      utilizationPct,
      hostTotalRamMb,
      hostUsedRamMb,
      hostRamUsagePct,
      fetchedAt: Date.now()
    };

    cachedGpu = { at: Date.now(), value: result };
    return result;
  } catch (err: any) {
    const fallback: GpuStatus = {
      status: "off",
      gpuName: "NVIDIA RTX 4060 (Standby)",
      totalVramMb: 8188,
      usedVramMb: 0,
      freeVramMb: 8188,
      vramUsagePct: 0,
      temperatureC: 0,
      utilizationPct: 0,
      hostTotalRamMb,
      hostUsedRamMb,
      hostRamUsagePct,
      fetchedAt: Date.now(),
      error: err.message
    };
    cachedGpu = { at: Date.now(), value: fallback };
    return fallback;
  }
}
