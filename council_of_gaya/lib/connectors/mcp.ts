import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";

export interface McpServerInfo {
  name: string;
  toolCount: number;
  path: string;
  status: "ok" | "warn" | "off";
}

export interface McpStatus {
  status: "ok" | "err" | "off";
  servers: McpServerInfo[];
  totalTools: number;
  fetchedAt: number;
  error?: string;
}

const MCP_DIR = path.join(os.homedir(), ".gemini", "antigravity", "mcp");
const CACHE_TTL_MS = 25_000;
let cachedMcp: { at: number; value: McpStatus } | null = null;

export async function getMcpStatus(): Promise<McpStatus> {
  if (cachedMcp && Date.now() - cachedMcp.at < CACHE_TTL_MS) {
    return cachedMcp.value;
  }

  try {
    const entries = await fs.readdir(MCP_DIR, { withFileTypes: true });
    const servers: McpServerInfo[] = [];
    let totalTools = 0;

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const sDir = path.join(MCP_DIR, entry.name);
      try {
        const files = await fs.readdir(sDir);
        const tools = files.filter((f) => f.endsWith(".json"));
        servers.push({
          name: entry.name,
          toolCount: tools.length,
          path: sDir,
          status: "ok"
        });
        totalTools += tools.length;
      } catch {}
    }

    const result: McpStatus = {
      status: servers.length > 0 ? "ok" : "off",
      servers,
      totalTools,
      fetchedAt: Date.now()
    };

    cachedMcp = { at: Date.now(), value: result };
    return result;
  } catch (err: any) {
    return {
      status: "err",
      servers: [],
      totalTools: 0,
      fetchedAt: Date.now(),
      error: err.message
    };
  }
}
