import net from "node:net";
import fs from "node:fs/promises";
import path from "node:path";

export interface ComfyUiStatus {
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
  fetchedAt: number;
  error?: string;
}

const COMFY_ROOT = "D:\\Ai_Tools\\ComfyUI_windows_portable";
const PORT = 8188;
const HOST = "127.0.0.1";
const CACHE_TTL_MS = 15_000;

let cachedComfy: { at: number; value: ComfyUiStatus } | null = null;

async function checkPortOnline(): Promise<boolean> {
  return new Promise((resolve) => {
    const s = net.createConnection({ host: HOST, port: PORT, timeout: 300 }, () => {
      s.destroy();
      resolve(true);
    });
    s.on("error", () => resolve(false));
    s.on("timeout", () => {
      s.destroy();
      resolve(false);
    });
  });
}

async function listFilesSafe(dirPath: string): Promise<string[]> {
  try {
    const entries = await fs.readdir(dirPath, { withFileTypes: true });
    return entries
      .filter((e) => e.isFile() && !e.name.startsWith("put_") && (e.name.endsWith(".safetensors") || e.name.endsWith(".gguf") || e.name.endsWith(".pth") || e.name.endsWith(".bin")))
      .map((e) => e.name);
  } catch {
    return [];
  }
}

export async function getComfyUiStatus(): Promise<ComfyUiStatus> {
  if (cachedComfy && Date.now() - cachedComfy.at < CACHE_TTL_MS) {
    return cachedComfy.value;
  }

  let installed = false;
  try {
    const stat = await fs.stat(COMFY_ROOT);
    installed = stat.isDirectory();
  } catch {
    installed = false;
  }

  if (!installed) {
    const result: ComfyUiStatus = {
      status: "off",
      port: PORT,
      installed: false,
      rootPath: COMFY_ROOT,
      models: { diffusion: [], textEncoders: [], vae: [], totalCount: 0 },
      fetchedAt: Date.now(),
      error: "Directory not found"
    };
    cachedComfy = { at: Date.now(), value: result };
    return result;
  }

  const [isOnline, diffModels, textEncoders, vaeModels] = await Promise.all([
    checkPortOnline(),
    listFilesSafe(path.join(COMFY_ROOT, "ComfyUI", "models", "diffusion_models")),
    listFilesSafe(path.join(COMFY_ROOT, "ComfyUI", "models", "text_encoders")),
    listFilesSafe(path.join(COMFY_ROOT, "ComfyUI", "models", "vae"))
  ]);

  const totalCount = diffModels.length + textEncoders.length + vaeModels.length;

  const result: ComfyUiStatus = {
    status: isOnline ? "ok" : "standby",
    port: PORT,
    installed: true,
    rootPath: COMFY_ROOT,
    models: {
      diffusion: diffModels,
      textEncoders: textEncoders,
      vae: vaeModels,
      totalCount
    },
    fetchedAt: Date.now()
  };

  cachedComfy = { at: Date.now(), value: result };
  return result;
}
