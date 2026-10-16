import { getPublicRepoStatus, type RepoStatus } from "./github";
import { pingSite, type SiteStatus } from "./site-ping";
import { getMiniGayaStatus, type MiniGayaStatus } from "./mini-gaya";
import { getGpuStatus, type GpuStatus } from "./gpu";
import { getSkillsStatus, type SkillsStatus } from "./skills";
import { getMcpStatus, type McpStatus } from "./mcp";
import { getComfyUiStatus, type ComfyUiStatus } from "./comfyui";
import { getSpecialistTelemetry, type SpecialistTelemetry } from "./specialists";
import { getAntigravityStatus, type AntigravityStatus } from "./antigravity";

const GAYA_AGENT_REPO = "ronakraval104-sys/Gaya_Agent_PR";
const GAYA_APP_URL = process.env.GAYA_APP_URL ?? "http://localhost:4200/";

export interface ConfigurableStatus {
  status: "ok" | "warn" | "err" | "off" | "not_configured";
  hint?: string;
  count?: number;
  latestSha?: string;
  error?: string;
  fetchedAt: number;
  meta?: Record<string, unknown>;
}

export interface AllConnectors {
  antigravity: AntigravityStatus;
  miniGaya: MiniGayaStatus;
  systemGpu: GpuStatus;
  skillsArmory: SkillsStatus;
  mcpServers: McpStatus;
  comfyui: ComfyUiStatus;
  specialists: SpecialistTelemetry;
  githubEmpire: RepoStatus;
  kvPages: SiteStatus;
  fetchedAt: number;
}

export async function getAllConnectors(): Promise<AllConnectors> {
  const [
    antigravity,
    miniGaya,
    systemGpu,
    skillsArmory,
    mcpServers,
    comfyui,
    specialists,
    githubEmpire,
    kvPages
  ] = await Promise.all([
    getAntigravityStatus(),
    getMiniGayaStatus(),
    getGpuStatus(),
    getSkillsStatus(),
    getMcpStatus(),
    getComfyUiStatus(),
    getSpecialistTelemetry(),
    getPublicRepoStatus(GAYA_AGENT_REPO),
    pingSite(GAYA_APP_URL, 5000)
  ]);

  return {
    antigravity,
    miniGaya,
    systemGpu,
    skillsArmory,
    mcpServers,
    comfyui,
    specialists,
    githubEmpire,
    kvPages,
    fetchedAt: Date.now()
  };
}
